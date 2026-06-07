import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { PostCreateInput, PostUpdateInput } from '../types/post.types.js';

/* LLM_SECTION_START */
// Entity: Post
// Fields (name: ts_type, required/optional):
//   title: string (required)
//   content: string (required)
//   published: boolean (required)
//   authorId: number (required)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for Post create and update
// SERVER-INJECTED (always): authorId is set from req.user.id — exclude from ALL schemas
// BUSINESS RULE: Only the author can edit or delete a post
// BUSINESS RULE: Title must be non-empty and trimmed; content must be at least 10 characters
// FIELD DEFAULT: published has @default(false) — MUST be .optional() in createSchema
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const postCreateSchema = z.object({});
const postUpdateSchema = z.object({});
/* LLM_SECTION_END */

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
