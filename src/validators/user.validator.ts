import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { UserCreateInput, UserUpdateInput } from '../types/user.types.js';

const userCreateSchema = z.object({
  email: z.string().email({ message: 'Please provide a valid email address' }),
  name: z.string().min(1).max(255).trim(),
  password: z.string().min(8).max(128),
  bio: z.string().min(1).trim().optional(),
  createdAt: z.coerce.date().optional(),
  updatedAt: z.coerce.date().optional(),
});
const userUpdateSchema = userCreateSchema.partial();

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
