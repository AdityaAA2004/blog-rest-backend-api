import { Router } from 'express';
import { CommentController } from '../controllers/comment.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new CommentController();

// List all comments with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single comment by ID
router.get('/:id', controller.getById.bind(controller));
// Update an existing comment (requires authentication + ownership)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a comment (requires authentication + ownership)
router.delete('/:id', authenticate, controller.remove.bind(controller));

export { router as commentsRouter };
