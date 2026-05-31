import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { CommentCreateInput, CommentUpdateInput } from '../types/comment.types.js';

const commentCreateSchema = z.object({
  body: z.string().min(1),
  postId: z.number(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const commentCreateNestedSchema = z.object({
  body: z.string().min(1),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const commentUpdateSchema = commentCreateSchema.partial();

function formatErrors(errors: z.ZodIssue[]): string {
  const seen = new Set<string>();
  return errors
    .map(e => {
      const field = e.path.length > 0 ? e.path.join('.') : null;
      return field ? `${field}: ${e.message}` : e.message;
    })
    .filter(msg => {
      if (seen.has(msg)) return false;
      seen.add(msg);
      return true;
    })
    .join(', ');
}

export function validateCommentCreate(body: unknown): CommentCreateInput {
  const result = commentCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as CommentCreateInput;
}

export function validateCommentCreateNested(body: unknown): CommentCreateInput {
  const result = commentCreateNestedSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as CommentCreateInput;
}

export function validateCommentUpdate(body: unknown): CommentUpdateInput {
  const result = commentUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as CommentUpdateInput;
}
