import { Request, Response, NextFunction } from 'express';
import { PostRepository } from '../repositories/post.repository.js';
import { validatePostCreate, validatePostUpdate } from '../validators/post.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';
import { CommentRepository } from '../repositories/comment.repository.js';
import { validateCommentCreate, validateCommentCreateNested, validateCommentUpdate } from '../validators/comment.validator.js';

export class PostController {
  private repository: PostRepository;
  private commentRepository: CommentRepository;

  constructor() {
    this.repository = new PostRepository();
    this.commentRepository = new CommentRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['title', 'content', 'published', 'authorId'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'title', 'content', 'published', 'authorId'] as const;

  async getAll(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const params = parseListQuery(req, this.ALLOWED_FILTER_FIELDS, this.ALLOWED_SORT_FIELDS);
      const { data, total } = await this.repository.findMany(params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const record = await this.repository.findById(id);
      if (!record) {
        throw new NotFoundError('Post', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validatePostCreate(req.body);
      // Inject the authenticated user's ID as the owner FK
      const record = await this.repository.create({ ...data, authorId: req.user!.id });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const existing = await this.repository.findById(id);
      if (!existing) {
        throw new NotFoundError('Post', id);
      }
      if (existing.authorId !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const data = validatePostUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Post', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async remove(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseId(req.params.id);
      const existing = await this.repository.findById(id);
      if (!existing) {
        throw new NotFoundError('Post', id);
      }
      if (existing.authorId !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const deleted = await this.repository.delete(id);
      if (!deleted) {
        throw new NotFoundError('Post', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  // --- Nested: Comment under Post ---

  async getCommentsForPost(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      const nestedFilterFields = ['body', 'authorId', 'postId'] as const;
      const nestedSortFields = ['id', 'body', 'authorId', 'postId'] as const;
      const params = parseListQuery(req, nestedFilterFields, nestedSortFields);
      const { data, total } = await this.commentRepository.findManyByPostId(parentId, params);
      res.json(buildPaginatedResponse(data, total, params));
    } catch (err) {
      next(err);
    }
  }

  async createCommentForPost(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parentId = this._parseId(req.params.id);
      // Use the nested schema: parent FK (postId) is injected from URL, not expected in body
      const data = validateCommentCreateNested(req.body);
      // Inject the parent FK; ignore any postId provided in the body
      // Also inject the owner FK (authorId) from the authenticated user's token
      const record = await this.commentRepository.create({ ...data, postId: parentId, authorId: req.user!.id });
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }


  private _parseId(raw: string): number {
    if (!/^\d+$/.test(raw)) {
      throw new AppError(400, 'Invalid ID format');
    }
    const id = Number(raw);
    if (id > Number.MAX_SAFE_INTEGER) {
      throw new AppError(400, 'ID out of range');
    }
    return id;
  }
}
