import { log } from 'console';
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
        WhatsAppLogger.logApiCall('POST', `${phoneId}/messages`, "Started", 'calling');
    let data = {};
    if (templateHeaderType == "image") {
        if (!templateImageLink) {
            throw new Error("templateImageLink is required when templateHeaderType is 'image'");
        }
        WhatsAppLogger.logApiCall('POST', templateHeaderType, "Declare Variable of Data template with image header ", 'calling');

        data = {
            messaging_product: "whatsapp",
            to: userId,
            type: "template",
            template: {
                name: templateName,
                language: { code: "id" },
                components: [
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
            }
        };
        WhatsAppLogger.logApiCall('POST', JSON.stringify(data), "Goten Variable of Data ", 'calling');
    } else {
        WhatsAppLogger.logApiCall('POST', templateHeaderType, "Declare Variable of Data template without header ", 'calling');
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
        WhatsAppLogger.logApiCall('POST', templateHeaderType, "Starting call api to Facebook", 'calling');
        await api.post(`${phoneId}/messages`, data);
        WhatsAppLogger.logTemplateMessage(userId,  phoneId+":"+templateName+" :"+templateHeaderType+" :"+templateImageLink, 'success');
    } catch (error) {
        WhatsAppLogger.logTemplateMessage(userId, phoneId+":"+templateName+" :"+templateHeaderType+" :"+templateImageLink, 'error');
        WhatsAppLogger.logError('sendTemplateMessage', error, userId);
        throw error;
    }
};
