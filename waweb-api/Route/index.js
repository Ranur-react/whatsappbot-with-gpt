import express from 'express';
import { handleWebhookGet, handleWebhookPost } from '../API/Facebook/index.js';

const router = express.Router();

// Route webhook WhatsApp sederhana
router.get('/webhook', handleWebhookGet);
router.post('/webhook', handleWebhookPost);


export default router;