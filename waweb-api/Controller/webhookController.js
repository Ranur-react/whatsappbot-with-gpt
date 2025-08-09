import { sendTemplateMessage } from '../API/Facebook/whatsappService.js';
import { WhatsAppLogger } from '../Helper/middleware.js';

// Webhook untuk verifikasi WhatsApp API
export const handleWebhookGet = (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    
    // Ganti dengan token verifikasi Anda
    const WEBHOOK_VERIFY_TOKEN = process.env.WEBHOOK_VERIFY_TOKEN || 'your_webhook_verify_token';

    if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
        res.status(200).send(challenge);
        WhatsAppLogger.logWebhookVerification(true, token);
    } else {
        res.sendStatus(403);
        WhatsAppLogger.logWebhookVerification(false, token);
    }
};

// Webhook untuk menerima pesan masuk dan membalas dengan WelcomeTemplate
export const handleWebhookPost = async (req, res) => {
    try {
        const message = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
        
        if (message && message.type === 'text') {
            const businessPhoneNumberId = req.body.entry?.[0]?.changes?.[0]?.value?.metadata?.phone_number_id;
            const userId = message.from;
            const messageText = message.text.body;

            // Log pesan masuk
            WhatsAppLogger.logIncomingMessage(userId, messageText, message.type);

            // Balas dengan WelcomeTemplate
            await sendTemplateMessage(userId, 'WelcomeTemplate');
        }
        
        res.sendStatus(200);
    } catch (error) {
        WhatsAppLogger.logError('handleWebhookPost', error);
        res.sendStatus(500);
    }
};
