import { axiosInstance } from '../../Helper/Axios/index.js';
import { WhatsAppLogger } from '../../Helper/middleware.js';

const api = axiosInstance(); // Inisialisasi axios instance

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
