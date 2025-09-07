import express from 'express';
import { handleRootGet, handleStatusGet } from '../Controller/pageController.js';
import { handleWebhookGet, handleWebhookPost } from '../Controller/webhookController.js';

const router = express.Router();

// Root page
router.get('/', handleRootGet);

// API Status
router.get('/status', handleStatusGet);

// Route webhook WhatsApp sederhana
router.get('/webhook', handleWebhookGet);
router.post('/webhook', handleWebhookPost);

export default router;