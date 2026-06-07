import { Request, Response, NextFunction } from 'express';
import { CommentRepository } from '../repositories/comment.repository.js';
import { validateCommentCreate, validateCommentUpdate } from '../validators/comment.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';

export class CommentController {
  private repository: CommentRepository;

  constructor() {
    this.repository = new CommentRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['body', 'authorId', 'postId'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'body', 'authorId', 'postId'] as const;

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
        throw new NotFoundError('Comment', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateCommentCreate(req.body);
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
        throw new NotFoundError('Comment', id);
      }
      if (existing.authorId !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const data = validateCommentUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Comment', id);
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
        throw new NotFoundError('Comment', id);
      }
      if (existing.authorId !== req.user!.id) {
        throw new AppError(403, 'Forbidden');
      }
      const deleted = await this.repository.delete(id);
      if (!deleted) {
        throw new NotFoundError('Comment', id);
      }
      res.status(204).send();
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
