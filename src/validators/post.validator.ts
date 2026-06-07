import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { PostCreateInput, PostUpdateInput } from '../types/post.types.js';

const postCreateSchema = z.object({
  title: z.string().min(1).max(255).trim(),
  content: z.string().min(10).max(10000),
  published: z.boolean().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const postUpdateSchema = postCreateSchema.partial();

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

export function validatePostCreate(body: unknown): PostCreateInput {
  const result = postCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as PostCreateInput;
}

export function validatePostUpdate(body: unknown): PostUpdateInput {
  const result = postUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as PostUpdateInput;
}
