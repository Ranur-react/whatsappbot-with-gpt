# WhatsApp Webhook Apache Configuration

Script untuk setup otomatis Apache reverse proxy untuk WhatsApp webhook service dengan Docker menggunakan file environment (.env) untuk konfigurasi yang aman dan mudah.

## 🔧 **Setup Configuration**

### 1. Konfigurasi Environment

Copy file template dan sesuaikan dengan environment Anda:

```bash
cp .env.example .env
nano .env
```

### 2. Konfigurasi Wajib di .env

Edit file `.env` dan sesuaikan nilai-nilai berikut:

```bash
# Domain dan Server Configuration
DOMAIN_NAME=botdev-owhub.totalbp.com    # Domain produksi Anda
SERVER_IP=10.100.129.51                 # IP server internal
ADMIN_EMAIL=admin@totalbp.com           # Email untuk SSL certificate

# Docker Configuration  
DOCKER_CONTAINER_NAME=node1             # Nama container Docker
TARGET_PORT=3000                        # Port aplikasi Node.js
```

### 3. Konfigurasi SSL (Opsional)

```bash
# SSL Configuration
ENABLE_SSL=true                 # Aktifkan SSL/HTTPS
SSL_AUTO_REDIRECT=true          # Auto redirect HTTP ke HTTPS
SKIP_SSL_VERIFICATION=false     # Skip verifikasi domain (development only)
```

### 4. Konfigurasi Security & Monitoring

```bash
# Security Configuration
ENABLE_SECURITY_HEADERS=true           # Header keamanan
ENABLE_HSTS=true                       # HTTPS Strict Transport Security

# Monitoring Configuration  
ENABLE_SERVER_STATUS=true              # Apache server status
ALLOWED_MONITOR_IPS=127.0.0.1,10.100.129.51  # IP yang boleh monitoring
```

## 🚀 Quick Start

### 1. Edit Konfigurasi
Buka file `config2.py` dan edit bagian konfigurasi:

```python
# KONFIGURASI UTAMA - EDIT SESUAI KEBUTUHAN
DOCKER_CONTAINER_NAME = "node1"
DOCKER_INTERNAL_PORT = 3000
TARGET_PORT = 3000  # Port yang akan di-proxy ke port 80
DOMAIN_NAME = "webhook.yourdomain.com"  # Ganti dengan domain Anda
ADMIN_EMAIL = "admin@yourdomain.com"  # Email untuk SSL certificate
```

### 2. Jalankan Script
```bash
sudo python3 config2.py
```

### 3. Start WhatsApp Service
```bash
sudo whatsapp-service start
```

## 🔧 Konfigurasi Detail

### Mengubah Target Port
Jika Anda ingin mengalihkan dari port 3000 ke port lain:

1. **Edit `config2.py`**:
   ```python
   TARGET_PORT = 8080  # Ganti ke port yang diinginkan
   ```

2. **Jalankan ulang script**:
   ```bash
   sudo python3 config2.py
   ```

3. **Restart service**:
   ```bash
   sudo whatsapp-service restart
   ```

### Pilihan Port Alternatif
```python
# Alternatif port yang bisa digunakan:
TARGET_PORT = 3000  # Default Node.js WhatsApp service
TARGET_PORT = 3001  # Node.js app alternatif
TARGET_PORT = 8080  # Development server
TARGET_PORT = 5000  # Python Flask/FastAPI
TARGET_PORT = 9000  # Custom service
```

## 🐳 Docker Management

### Commands yang Tersedia
```bash
# Start container
sudo whatsapp-service start

# Stop container
sudo whatsapp-service stop

# Restart container
sudo whatsapp-service restart

# Check status
sudo whatsapp-service status

# View logs
sudo whatsapp-service logs

# Access container shell
sudo whatsapp-service shell
```

### Manual Docker Commands
```bash
# Start container manually
docker run -d --name node1 \
  --restart unless-stopped \
  -p 3000:3000 \
  -v $(pwd)/waweb-api:/app \
  -w /app \
  node:18-alpine \
  sh -c "npm install && npm start"

# Check logs
docker logs -f node1

# Stop container
docker stop node1 && docker rm node1
```

## 🌐 Apache Virtual Host

### HTTP Configuration
- Traffic dari port 80 akan di-proxy ke `localhost:TARGET_PORT`
- Support WebSocket untuk real-time features
- Security headers included
- Custom logging

### HTTPS Configuration (Setelah SSL)
- Automatic redirect HTTP ke HTTPS
- Modern SSL configuration
- HSTS headers
- Same proxy configuration

## 📁 File Locations

### Configuration Files
```
/etc/apache2/sites-available/webhook.yourdomain.com.conf
/usr/local/bin/whatsapp-service
```

### Log Files
```
/var/log/apache2/whatsapp-webhook_error.log
/var/log/apache2/whatsapp-webhook_access.log
/var/log/apache2/whatsapp-webhook_ssl_error.log
/var/log/apache2/whatsapp-webhook_ssl_access.log
```

### Backup Files
```
/etc/apache2/backup_YYYYMMDDHHMMSS/
```

## 🔒 SSL Certificate

### Automatic Setup
Script akan menanyakan apakah Anda ingin setup SSL:
```bash
IMPORTANT: Make sure webhook.yourdomain.com points to this server's IP address
Continue with SSL setup? (y/N):
```

### Manual SSL Setup
```bash
sudo certbot --apache -d webhook.yourdomain.com
```

### SSL Renewal (Automatic)
```bash
# Check auto-renewal
sudo systemctl status certbot.timer

# Manual renewal test
sudo certbot renew --dry-run
```

## 🔍 Troubleshooting

### Check Apache Status
```bash
sudo systemctl status apache2
sudo apache2ctl configtest
```

### Check Docker Status
```bash
sudo systemctl status docker
docker ps -a
docker logs node1
```

### Check Port Usage
```bash
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :3000
```

### View Logs
```bash
# Apache logs
sudo tail -f /var/log/apache2/whatsapp-webhook_error.log

# Docker logs
sudo whatsapp-service logs
```

### Common Issues

1. **Port already in use**:
   ```bash
   sudo lsof -i :3000
   sudo kill -9 <PID>
   ```

2. **Domain not pointing to server**:
   - Check DNS settings
   - Use `nslookup webhook.yourdomain.com`

3. **SSL certificate issues**:
   ```bash
   sudo certbot certificates
   sudo certbot delete --cert-name webhook.yourdomain.com
   ```

## 📊 Monitoring

### Check Service Health
```bash
# Apache status
curl -I http://localhost/server-status

# WhatsApp service status
curl -I http://localhost/status

# SSL certificate expiry
sudo certbot certificates
```

### Performance Monitoring
```bash
# Apache connections
sudo apache2ctl status

# System resources
htop
docker stats node1
```

## 🔄 Migration & Updates

### Changing Domain
1. Edit `DOMAIN_NAME` in `config2.py`
2. Run `sudo python3 config2.py`
3. Update DNS records
4. Obtain new SSL certificate

### Changing Port
1. Edit `TARGET_PORT` in `config2.py`
2. Run `sudo python3 config2.py`
3. Restart services

### Backup Before Changes
Script automatically creates backup in:
```
/etc/apache2/backup_YYYYMMDDHHMMSS/
```

## 💡 Tips

1. **Always test configuration**:
   ```bash
   sudo apache2ctl configtest
   ```

2. **Monitor logs during setup**:
   ```bash
   sudo tail -f /var/log/apache2/error.log
   ```

3. **Use staging environment first** before production

4. **Keep backups** of working configurations

5. **Update regularly**:
   ```bash
   sudo apt update && sudo apt upgrade
   docker pull node:18-alpine
   ```
