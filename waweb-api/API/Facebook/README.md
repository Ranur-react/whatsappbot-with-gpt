# WhatsApp Webhook API Sederhana

API webhook sederhana untuk WhatsApp Business API yang membalas setiap pesan masuk dengan "Hallo".

## Setup

1. **Environment Variables**
   Pastikan file `.env` memiliki variabel berikut:
   ```
   WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
   GRAPH_API_TOKEN=your_facebook_graph_api_token
   ```

2. **Endpoint Webhook**
   - GET `/webhook` - Untuk verifikasi webhook
   - POST `/webhook` - Untuk menerima pesan masuk

## Cara Kerja

1. WhatsApp mengirim pesan masuk ke endpoint POST `/webhook`
2. API mengekstrak informasi pesan (pengirim, teks, dll)
3. API membalas dengan pesan "Hallo" menggunakan `sendTextMessage`
4. Log aktivitas ditampilkan di console

## Fungsi Utama

- `handleWebhookGet()` - Verifikasi webhook WhatsApp
- `handleWebhookPost()` - Proses pesan masuk dan balas otomatis
- `sendTextMessage()` - Mengirim pesan teks
- `sendButtonMessage()` - Mengirim pesan dengan tombol
- `sendTemplateMessage()` - Mengirim template message

## Testing

Untuk testing webhook secara lokal, gunakan ngrok:
```bash
ngrok http 3000
```

Kemudian set webhook URL di WhatsApp Business API console ke: `https://your-ngrok-url.ngrok.io/webhook`

## Customization

Untuk mengubah balasan otomatis, edit bagian ini di `handleWebhookPost()`:
```javascript
// Balas dengan "Hallo"
await sendTextMessage(businessPhoneNumberId, userId, 'Hallo');
```

Ganti 'Hallo' dengan pesan yang diinginkan.
