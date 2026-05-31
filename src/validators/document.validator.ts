import { z } from 'zod';
import { ValidationError } from '../lib/errors.js';
import { DocumentCreateInput, DocumentUpdateInput } from '../types/document.types.js';

/* LLM_SECTION_START */
// Entity: Document
// Fields (name: ts_type, required/optional):
//   title: string (required)
//   content: string (required)
//   createdAt: Date (required)
// TODO: define Zod schemas for Document create and update
// FIELD DEFAULT: createdAt has @default(now()) — MUST be .optional() in createSchema
const documentCreateSchema = z.object({});
const documentUpdateSchema = z.object({});
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

export function validateDocumentCreate(body: unknown): DocumentCreateInput {
  const result = documentCreateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as DocumentCreateInput;
}

export function validateDocumentUpdate(body: unknown): DocumentUpdateInput {
  const result = documentUpdateSchema.safeParse(body);
  if (!result.success) {
    throw new ValidationError(formatErrors(result.error.errors));
  }
  return result.data as DocumentUpdateInput;
}
