import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { UserCreateInput, UserUpdateInput } from '../types/user.types.js';

/* LLM_SECTION_START */
// Entity: User
// Fields (name: ts_type, required/optional):
//   email: string (required)
//   name: string (required)
//   password: string (required) [sensitive]
//   bio: string (optional)
//   createdAt: Date (required)
//   updatedAt: Date (required)
// TODO: define Zod schemas for User create and update
// BUSINESS RULE: Users can only read and modify their own profile — enforce self-ownership on GET/PUT/DELETE /users/:id
// BUSINESS RULE: Email must be unique and lowercased before storage
// BUSINESS RULE: Password must be at least 8 characters; never returned in any API response
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
// FIELD DEFAULT: updatedAt has @default(now()) — MUST be .optional() in createSchema
const userCreateSchema = z.object({});
const userUpdateSchema = z.object({});
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

export function validateUserCreate(body: unknown): UserCreateInput {
  const result = userCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as UserCreateInput;
}

export function validateUserUpdate(body: unknown): UserUpdateInput {
  const result = userUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as UserUpdateInput;
}
