import { WhatsAppLogger } from '../Helper/middleware.js';

// Root page handler
export const handleRootGet = (req, res) => {
    // Log akses ke root page
    WhatsAppLogger.logApiCall('GET', '/', null, 'success');
    
    const html = `
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp Bot API - OWHUB</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            .logo {
                font-size: 3em;
                margin-bottom: 20px;
                color: #25D366;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .status {
                background: #25D366;
                color: white;
                padding: 15px 30px;
                border-radius: 50px;
                display: inline-block;
                margin: 20px 0;
                font-weight: bold;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            .info {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #25D366;
            }
            .endpoint {
                font-family: monospace;
                background: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                font-weight: bold;
            }
            .footer {
                margin-top: 30px;
                color: #aaa;
                font-size: 0.9em;
            }
            .feature {
                display: inline-block;
                margin: 10px;
                padding: 10px 20px;
                background: #f1f3f4;
                border-radius: 25px;
                color: #333;
            }
            .link-button {
                display: inline-block;
                margin: 10px;
                padding: 12px 25px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                transition: background 0.3s;
            }
            .link-button:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">📱💬</div>
            <h1>OWHUB WhatsApp Bot</h1>
            <p class="subtitle">API Service untuk WhatsApp Business</p>
            
            <div class="status">
                🟢 Server Active & Running
            </div>
            
            <div class="info">
                <h3>🔗 Available Endpoints:</h3>
                <div class="endpoint">GET /webhook - Webhook Verification</div>
                <div class="endpoint">POST /webhook - Message Handler</div>
                <div class="endpoint">GET /status - API Status (JSON)</div>
            </div>
            
            <div class="info">
                <h3>✨ Features:</h3>
                <div class="feature">📨 Auto Reply</div>
                <div class="feature">📋 Template Messages</div>
                <div class="feature">🔘 Button Messages</div>
                <div class="feature">📊 Logging</div>
            </div>
            
            <div class="info">
                <h3>🛠️ Status:</h3>
                <p><strong>Server Time:</strong> ${new Date().toLocaleString('id-ID')}</p>
                <p><strong>Environment:</strong> ${process.env.NODE_ENV || 'development'}</p>
                <p><strong>Version:</strong> 1.0.0</p>
                <a href="/status" class="link-button">📊 View API Status (JSON)</a>
            </div>
            
            <div class="footer">
                <p>🚀 Powered by Node.js & Express.js</p>
                <p>📍 OWHUB Project - WhatsApp Integration</p>
            </div>
        </div>
    </body>
    </html>
    `;
    
    res.send(html);
};

// API Status endpoint
export const handleStatusGet = (req, res) => {
    WhatsAppLogger.logApiCall('GET', '/status', null, 'success');
    
    const status = {
        status: 'active',
        message: 'WhatsApp Bot API is running',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: process.env.NODE_ENV || 'development',
        endpoints: {
            webhook_get: '/webhook (GET)',
            webhook_post: '/webhook (POST)',
            root: '/ (GET)',
            status: '/status (GET)'
        },
        features: [
            'Auto Reply dengan Template',
            'Button Messages',
            'Text Messages',
            'Comprehensive Logging',
            'Error Handling'
        ]
    };
    
    res.json(status);
};
