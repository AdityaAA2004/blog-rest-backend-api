import { Router } from 'express';
import { DocumentController } from '../controllers/document.controller.js';
import { authenticate } from '../lib/auth.js';

const router = Router();
const controller = new DocumentController();

// List all documents with pagination and filtering
router.get('/', controller.getAll.bind(controller));
// Get a single document by ID
router.get('/:id', controller.getById.bind(controller));
// Create a new document (requires authentication)
router.post('/', authenticate, controller.create.bind(controller));
// Update an existing document (requires authentication)
router.put('/:id', authenticate, controller.update.bind(controller));
// Delete a document (requires authentication)
router.delete('/:id', authenticate, controller.remove.bind(controller));

export { router as documentsRouter };
