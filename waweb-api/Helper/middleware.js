export const logRequests = (req, res, next) => {
    console.log(`${req.method} ${req.url}`, JSON.stringify(req.body, null, 2));
    next();
};

// Helper untuk logging WhatsApp API operations
export class WhatsAppLogger {
    static logIncomingMessage(userId, messageText, messageType = 'text') {
        console.log('\n=== 📨 PESAN MASUK ===');
        console.log(`👤 User ID: ${userId}`);
        console.log(`📝 Type: ${messageType}`);
        console.log(`💬 Pesan: ${messageText}`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('====================\n');
    }

    static logOutgoingMessage(userId, messageType, content, status = 'sending') {
        const statusIcon = status === 'success' ? '✅' : status === 'error' ? '❌' : '📤';
        const statusText = status === 'success' ? 'BERHASIL TERKIRIM' : status === 'error' ? 'GAGAL TERKIRIM' : 'MENGIRIM PESAN';
        
        console.log(`\n=== ${statusIcon} ${statusText} ===`);
        console.log(`👤 To User: ${userId}`);
        console.log(`📋 Type: ${messageType}`);
        console.log(`📝 Content: ${content}`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('====================\n');
    }

    static logTemplateMessage(userId, templateName, status = 'sending') {
        const statusIcon = status === 'success' ? '✅' : status === 'error' ? '❌' : '📤';
        const statusText = status === 'success' ? 'TEMPLATE BERHASIL TERKIRIM' : status === 'error' ? 'TEMPLATE GAGAL TERKIRIM' : 'MENGIRIM TEMPLATE';
        
        console.log(`\n=== ${statusIcon} ${statusText} ===`);
        console.log(`👤 To User: ${userId}`);
        console.log(`📋 Template: ${templateName}`);
        console.log(`🌐 Language: Indonesian (id)`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('====================\n');
    }

    static logWebhookVerification(success = true, token = '') {
        const statusIcon = success ? '✅' : '❌';
        const statusText = success ? 'WEBHOOK VERIFIKASI BERHASIL' : 'WEBHOOK VERIFIKASI GAGAL';
        
        console.log(`\n=== ${statusIcon} ${statusText} ===`);
        console.log(`🔑 Token: ${token}`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('====================\n');
    }

    static logError(operation, error, userId = null) {
        console.log('\n=== ❌ ERROR TERJADI ===');
        console.log(`🔧 Operation: ${operation}`);
        if (userId) console.log(`👤 User ID: ${userId}`);
        console.log(`💥 Error: ${error.message || error}`);
        console.log(`📍 Stack: ${error.stack || 'No stack trace'}`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('=====================\n');
    }

    static logApiCall(method, endpoint, data = null, status = 'calling') {
        const statusIcon = status === 'success' ? '✅' : status === 'error' ? '❌' : '🌐';
        const statusText = status === 'success' ? 'API CALL BERHASIL' : status === 'error' ? 'API CALL GAGAL' : 'CALLING API';
        
        console.log(`\n=== ${statusIcon} ${statusText} ===`);
        console.log(`🔧 Method: ${method}`);
        console.log(`🌐 Endpoint: ${endpoint}`);
        if (data) console.log(`📦 Data: ${JSON.stringify(data, null, 2)}`);
        console.log(`⏰ Timestamp: ${new Date().toLocaleString('id-ID')}`);
        console.log('====================\n');
    }
}