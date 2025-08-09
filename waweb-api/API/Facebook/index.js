import { axiosInstance } from '../../Helper/Axios/index.js';
import { WhatsAppLogger } from '../../Helper/middleware.js';

const userStates = new Map();
const api = axiosInstance(); // Inisialisasi axios instance

export const getUserState = (userId) => userStates.get(userId) || null;
export const setUserState = (userId, state) => userStates.set(userId, state);
export const resetUserState = (userId) => userStates.delete(userId);

export const sendTextMessage = async (phoneId, userId, text, contextId = null) => {
    try {
        const payload = {
            messaging_product: 'whatsapp',
            to: userId,
            text: { body: text }
        };
        if (contextId) payload.context = { message_id: contextId };
        
        WhatsAppLogger.logApiCall('POST', `${phoneId}/messages`, payload, 'calling');
        await api.post(`${phoneId}/messages`, payload);
        WhatsAppLogger.logOutgoingMessage(userId, 'text', text, 'success');
    } catch (error) {
        WhatsAppLogger.logError('sendTextMessage', error, userId);
        throw error;
    }
};

export const sendButtonMessage = async (phoneId, userId, text, buttons) => {
    try {
        const payload = {
            messaging_product: 'whatsapp',
            to: userId,
            type: 'interactive',
            interactive: {
                type: 'button',
                body: { text },
                action: {
                    buttons: buttons.map((btn, idx) => ({
                        type: 'reply',
                        reply: { id: `btn_${idx + 1}`, title: btn }
                    }))
                }
            }
        };
        
        WhatsAppLogger.logApiCall('POST', `${phoneId}/messages`, payload, 'calling');
        await api.post(`${phoneId}/messages`, payload);
        WhatsAppLogger.logOutgoingMessage(userId, 'button', `${text} | Buttons: ${buttons.join(', ')}`, 'success');
    } catch (error) {
        WhatsAppLogger.logError('sendButtonMessage', error, userId);
        throw error;
    }
};

export const sendTemplateMessage = async (userId, templateName) => {
    try {
        const data = {
            messaging_product: "whatsapp",
            to: userId,
            type: "template",
            template: {
                name: templateName,
                language: { code: "id" }
            }
        };
        
        WhatsAppLogger.logApiCall('POST', '269270049609670/messages', data, 'calling');
        await api.post('269270049609670/messages', data);
        WhatsAppLogger.logTemplateMessage(userId, templateName, 'success');
    } catch (error) {
        WhatsAppLogger.logTemplateMessage(userId, templateName, 'error');
        WhatsAppLogger.logError('sendTemplateMessage', error, userId);
        throw error;
    }
};

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
