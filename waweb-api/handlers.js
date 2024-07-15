import axiosInstance from './axiosInstance.js';
import respondBuilderText from './respondBuilder.js';
import dotenv from 'dotenv';

dotenv.config();

const { WEBHOOK_VERIFY_TOKEN } = process.env;

const userStates = new Map();

const getUserState = (userId) => userStates.get(userId) || { currentState: "" };
const setUserState = (userId, state) => userStates.set(userId, state);
const resetUserState = (userId) => userStates.delete(userId);
const sendTemplateMessage = async (userId,templateName) => {
    let data = JSON.stringify({
        "messaging_product": "whatsapp",
        "to": userId,
        "type": "template",
        "template": {
            "name": templateName,
            "language": {
                "code": "id"
            }
        }
    });

    try {
        const response = await axiosInstance.post('269270049609670/messages', data, {
            headers: { 'Content-Type': 'application/json' }
        });
        console.log("Template message sent successfully:", JSON.stringify(response.data));
    } catch (error) {
        console.error("Error sending template message:", error);
    }
};

export const handleWebhookPost = async (req, res) => {
    const message = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
    if (message?.type === 'text' || message?.type === 'button') {
        const businessPhoneNumberId = req.body.entry?.[0]?.changes?.[0]?.value?.metadata?.phone_number_id;
        const userId = message.from;

        console.log('===========User ID=========================');
        console.log(userId);
        console.log('====================================');

        const messageText = message?.text?.body || message?.button?.text || "";

        if (messageText.toLowerCase() == "home" || messageText.toLowerCase() == "Home") {
            await sendTemplateMessage(userId, "absensi_intro");
            resetUserState(userId);
            res.sendStatus(200);
            return;
        }
        if (messageText.toLowerCase() === "GPT" || messageText.toLowerCase() === "gpt" || messageText.toLowerCase() === "reset" || messageText.toLowerCase() === "Reset") {
            await sendTemplateMessage(userId, "absensi_intro");
            resetUserState(userId);
            res.sendStatus(200);
            return;
        }

        const userState = getUserState(userId);
        try {
            const response = await respondBuilderText(
                message?.type !== 'button' ? message.text.body : message.button.text,
                userState,
                userId
            );

            await axiosInstance.post(`${businessPhoneNumberId}/messages`, {
                messaging_product: 'whatsapp',
                to: userId,
                text: { body: response.text },
                context: { message_id: message.id },
            });

            setUserState(userId, { currentState: response.nextState });
            res.sendStatus(200);
        } catch (error) {
            console.error('Error processing message:', error);
            res.sendStatus(500);
        }
    } else {
        res.sendStatus(200);
    }
};

export const handleWebhookGet = (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
        res.status(200).send(challenge);
        console.log('Webhook verified successfully!');
    } else {
        res.sendStatus(403);
    }
};

export const handleRootGet = (req, res) => {
    res.send(`<pre>Nothing to see here.\nCheckout README.md to start.</pre>`);
};
