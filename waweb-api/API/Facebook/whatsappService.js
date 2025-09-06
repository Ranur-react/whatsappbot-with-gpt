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

export const sendTemplateMessage = async (phoneId, userId, templateName, templateHeaderType="text", templateImageLink=null) => {
    try {
        const data = {};
        if (templateHeaderType === "image" && !templateImageLink) {
            data = {
                messaging_product: "whatsapp",
                to: userId,
                type: "template",
                template: {
                    name: templateName,
                    language: { code: "id" }
                },
                components: 
                [
                    {
                        type: "header",
                        parameters: [
                            {
                                type: "image",
                                image: {
                                    link: templateImageLink
                                        }
                            }
                        ]
                    }
                ]
            };
        }
        else{
        data = {
            messaging_product: "whatsapp",
            to: userId,
            type: "template",
            template: {
                name: templateName,
                language: { code: "id" }
            }
            
        };
    }
        
        WhatsAppLogger.logApiCall('POST', `${phoneId}/messages`, data, 'calling');
        await api.post(`${phoneId}/messages`, data);
        WhatsAppLogger.logTemplateMessage(userId, templateName, 'success');
    } catch (error) {
        WhatsAppLogger.logTemplateMessage(userId, templateName, 'error');
        WhatsAppLogger.logError('sendTemplateMessage', error, userId);
        throw error;
    }
};
