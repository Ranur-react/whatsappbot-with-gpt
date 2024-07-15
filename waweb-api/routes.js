import express from 'express';
import { handleWebhookPost, handleWebhookGet, handleRootGet } from './handlers.js';

const router = express.Router();

router.post('/webhook', handleWebhookPost);
router.get('/webhook', handleWebhookGet);
router.get('/', handleRootGet);

export default router;