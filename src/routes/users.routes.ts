import { Router } from 'express';
import { UserController } from '../controllers/user.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new UserController();

// List all users with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single user by ID
router.get('/:id', controller.getById.bind(controller));
// Create a new user (requires authentication)
router.post('/', authenticate, controller.create.bind(controller));
// Update an existing user (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a user (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

// --- Nested routes: posts under User ---
// List all posts for a user (always available)
router.get('/:id/posts', controller.getPostsForUser.bind(controller));
// Create a post — canonical create route (primary parent: User)
// Parent ID is taken from the auth token, not the URL
router.post('/posts', authenticate, controller.createPostForUser.bind(controller));

// --- Nested routes: comments under User ---
// List all comments for a user (always available)
router.get('/:id/comments', controller.getCommentsForUser.bind(controller));

export { router as usersRouter };
