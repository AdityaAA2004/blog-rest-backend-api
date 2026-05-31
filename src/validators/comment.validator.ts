import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { CommentCreateInput, CommentUpdateInput } from '../types/comment.types.js';

/* LLM_SECTION_START */
// Entity: Comment
// Fields (name: ts_type, required/optional):
//   body: string (required)
//   authorId: number (required)
//   postId: number (required)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for Comment create and update
// SERVER-INJECTED (always): authorId is set from req.user.id — exclude from ALL schemas
// PARENT-FK: postId is required in the request body for direct POST /comments,
//            but injected from URL params in nested routes — exclude it from commentCreateNestedSchema
// BUSINESS RULE: Comments belong to both an author (User) and a post (Post)
// BUSINESS RULE: Body must be non-empty; no maximum length restriction for comments
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const commentCreateSchema = z.object({});
const commentCreateNestedSchema = z.object({});
const commentUpdateSchema = z.object({});
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
