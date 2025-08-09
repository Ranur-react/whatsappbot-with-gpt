# OWHUB WhatsApp Bot - Root Pages

## 🏠 Root Page (`/`)
Halaman landing yang menampilkan:
- ✅ Status server aktif
- 📋 Daftar endpoints yang tersedia  
- ✨ Fitur-fitur bot
- 🛠️ Informasi sistem
- 🔗 Link ke status API

## 📊 Status API (`/status`)
Endpoint JSON untuk monitoring yang mengembalikan:
```json
{
  "status": "active",
  "message": "WhatsApp Bot API is running",
  "timestamp": "2025-08-09T07:30:25.123Z",
  "uptime": 1234.567,
  "environment": "development",
  "endpoints": {
    "webhook_get": "/webhook (GET)",
    "webhook_post": "/webhook (POST)", 
    "root": "/ (GET)",
    "status": "/status (GET)"
  },
  "features": [
    "Auto Reply dengan Template",
    "Button Messages", 
    "Text Messages",
    "Comprehensive Logging",
    "Error Handling"
  ]
}
```

## 🎨 Design Features
- Responsive design
- Gradient background
- Animated status indicator
- Clean card layout
- Clickable status link
- Professional typography

## 📱 Akses
- **Development**: `http://localhost:3000`
- **Production**: `https://your-domain.com`

## 🔧 Logging
Semua akses ke root pages akan tercatat di console dengan format yang rapi menggunakan `WhatsAppLogger`.

## 🚀 Ready untuk Production
Halaman ini siap untuk:
- Health checks
- Load balancer monitoring  
- API documentation
- User-friendly landing page
