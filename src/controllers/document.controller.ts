import { Request, Response, NextFunction } from 'express';
import { DocumentRepository } from '../repositories/document.repository.js';
import { validateDocumentCreate, validateDocumentUpdate } from '../validators/document.validator.js';
import { parseListQuery, buildPaginatedResponse } from '../lib/pagination.js';
import { NotFoundError, AppError } from '../lib/errors.js';

export class DocumentController {
  private repository: DocumentRepository;

  constructor() {
    this.repository = new DocumentRepository();
  }

  private readonly ALLOWED_FILTER_FIELDS = ['title', 'content'] as const;
  private readonly ALLOWED_SORT_FIELDS = ['id', 'title', 'content'] as const;

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
      const id = this._parseStringId(req.params.id);
      const record = await this.repository.findById(id);
      if (!record) {
        throw new NotFoundError('Document', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const data = validateDocumentCreate(req.body);
      const record = await this.repository.create(data);
      res.status(201).json(record);
    } catch (err) {
      next(err);
    }
  }

  async update(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseStringId(req.params.id);
      const data = validateDocumentUpdate(req.body);
      const record = await this.repository.update(id, data);
      if (!record) {
        throw new NotFoundError('Document', id);
      }
      res.json(record);
    } catch (err) {
      next(err);
    }
  }

  async remove(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const id = this._parseStringId(req.params.id);
      const deleted = await this.repository.delete(id);
      if (!deleted) {
        throw new NotFoundError('Document', id);
      }
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  }

  private _parseStringId(raw: string): string {
    if (!raw || raw.trim() !== raw || raw.length > 128) {
      throw new AppError(400, 'Invalid ID format');
    }
    // UUID v4 format validation
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(raw)) {
      throw new AppError(400, 'Invalid ID format');
    }
    return raw;
  }
}
