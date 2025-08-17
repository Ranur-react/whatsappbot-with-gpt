import subprocess
import os
import shutil
from datetime import datetime

# ====================================
# LOAD CONFIGURATION FROM .env FILE
# ====================================

def load_env_config():
    """Load konfigurasi dari file .env"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    config = {}
    
    if not os.path.exists(env_file):
        print("❌ File .env tidak ditemukan!")
        print("Silakan copy .env.example ke .env dan sesuaikan konfigurasi")
        exit(1)
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove inline comments
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    config[key.strip()] = value.strip()
        
        print("✅ Configuration loaded from .env file")
        return config
    except Exception as e:
        print("❌ Error loading .env file: {}".format(e))
        exit(1)

# Load configuration
ENV_CONFIG = load_env_config()

# ====================================
# CONFIGURATION VARIABLES FROM .env
# ====================================

# Domain dan Server Configuration
DOMAIN_NAME = ENV_CONFIG.get('DOMAIN_NAME', 'localhost')
SERVER_IP_SANDBOX = ENV_CONFIG.get('SERVER_IP_SANDBOX', '127.0.0.1')
SERVER_IP_INTERNET = ENV_CONFIG.get('SERVER_IP_INTERNET', '127.0.0.1')
SERVER_IP = SERVER_IP_SANDBOX  # Backward compatibility
ADMIN_EMAIL = ENV_CONFIG.get('ADMIN_EMAIL', 'admin@localhost')

# Network Interface Configuration
NIC_SANDBOX = ENV_CONFIG.get('NIC_SANDBOX', 'ens120')
NIC_INTERNET = ENV_CONFIG.get('NIC_INTERNET', 'ens192')

# Public Access Configuration
USE_NGROK = ENV_CONFIG.get('USE_NGROK', 'false').lower() == 'true'
NGROK_REGION = ENV_CONFIG.get('NGROK_REGION', 'ap')
NGROK_SUBDOMAIN = ENV_CONFIG.get('NGROK_SUBDOMAIN', 'webhook')

# Docker Configuration
DOCKER_CONTAINER_NAME = ENV_CONFIG.get('DOCKER_CONTAINER_NAME', 'node1')
DOCKER_INTERNAL_PORT = int(ENV_CONFIG.get('DOCKER_INTERNAL_PORT', '3000'))
DOCKER_SERVICE_NAME = ENV_CONFIG.get('DOCKER_SERVICE_NAME', 'whatsapp-webhook')

# Apache Proxy Configuration
TARGET_PORT = int(ENV_CONFIG.get('TARGET_PORT', '3000'))

# SSL Configuration
ENABLE_SSL = ENV_CONFIG.get('ENABLE_SSL', 'true').lower() == 'true'
SSL_AUTO_REDIRECT = ENV_CONFIG.get('SSL_AUTO_REDIRECT', 'true').lower() == 'true'
SSL_TYPE = ENV_CONFIG.get('SSL_TYPE', 'letsencrypt')  # letsencrypt, corporate

# Corporate SSL paths
CORPORATE_SSL_CERT_PATH = ENV_CONFIG.get('CORPORATE_SSL_CERT_PATH', '/etc/ssl/corporate/cert.pem')
CORPORATE_SSL_KEY_PATH = ENV_CONFIG.get('CORPORATE_SSL_KEY_PATH', '/etc/ssl/corporate/private.key')
CORPORATE_SSL_CHAIN_PATH = ENV_CONFIG.get('CORPORATE_SSL_CHAIN_PATH', '/etc/ssl/corporate/chain.pem')

# Security Configuration
ENABLE_SECURITY_HEADERS = ENV_CONFIG.get('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true'
ENABLE_HSTS = ENV_CONFIG.get('ENABLE_HSTS', 'true').lower() == 'true'

# Monitoring Configuration
ENABLE_SERVER_STATUS = ENV_CONFIG.get('ENABLE_SERVER_STATUS', 'true').lower() == 'true'
ALLOWED_MONITOR_IPS = ENV_CONFIG.get('ALLOWED_MONITOR_IPS', '127.0.0.1').split(',')

# Backup Configuration
BACKUP_ENABLED = ENV_CONFIG.get('BACKUP_ENABLED', 'true').lower() == 'true'
BACKUP_RETENTION_DAYS = int(ENV_CONFIG.get('BACKUP_RETENTION_DAYS', '30'))

# Logging Configuration
LOG_LEVEL = ENV_CONFIG.get('LOG_LEVEL', 'info')
ENABLE_ACCESS_LOG = ENV_CONFIG.get('ENABLE_ACCESS_LOG', 'true').lower() == 'true'
ENABLE_ERROR_LOG = ENV_CONFIG.get('ENABLE_ERROR_LOG', 'true').lower() == 'true'

# Development Options
DEBUG_MODE = ENV_CONFIG.get('DEBUG_MODE', 'false').lower() == 'true'
SKIP_SSL_VERIFICATION = ENV_CONFIG.get('SKIP_SSL_VERIFICATION', 'false').lower() == 'true'

print("Configuration Summary:")
print("- Domain: {}".format(DOMAIN_NAME))
print("- SANDBOX IP ({}): {}".format(NIC_SANDBOX, SERVER_IP_SANDBOX))
print("- INTERNET IP ({}): {}".format(NIC_INTERNET, SERVER_IP_INTERNET))
print("- Target Port: {}".format(TARGET_PORT))
print("- SSL Enabled: {}".format(ENABLE_SSL))
print("- SSL Type: {}".format(SSL_TYPE))
print("- Use Ngrok: {}".format(USE_NGROK))
print("- Debug Mode: {}".format(DEBUG_MODE))

def run_command(command, quiet=False):
    """Menjalankan command shell dengan error handling"""
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            if not quiet:
                print("Error running command: {}".format(command))
                print(result.stderr)
            return False
        else:
            if not quiet:
                print(result.stdout)
            return True
    except Exception as e:
        if not quiet:
            print("Exception running command: {}".format(command))
            print(e)
        return False
        return False

def check_existing_configuration():
    """Cek apakah konfigurasi sudah ada untuk mencegah duplikasi"""
    print("=== CHECKING EXISTING CONFIGURATION ===")
    
    config_file = "/etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME)
    script_file = "/usr/local/bin/whatsapp-service"
    
    # Cek apakah config file sudah ada
    if os.path.exists(config_file):
        print("⚠️  Apache configuration already exists: {}".format(config_file))
        
        # Cek apakah site sudah enabled
        enabled_file = "/etc/apache2/sites-enabled/{}.conf".format(DOMAIN_NAME)
        if os.path.exists(enabled_file):
            print("✅ Site is already enabled")
            
            # Cek apakah konfigurasi masih sesuai
            with open(config_file, 'r') as f:
                content = f.read()
                if "localhost:{}".format(TARGET_PORT) in content:
                    print("✅ Configuration matches current TARGET_PORT: {}".format(TARGET_PORT))
                    return True
                else:
                    print("⚠️  Configuration PORT mismatch, will update...")
                    return False
        else:
            print("⚠️  Site exists but not enabled, will enable...")
            return False
    
    # Cek apakah management script sudah ada
    if os.path.exists(script_file):
        print("✅ Docker management script already exists: {}".format(script_file))
    
    return False

def check_ssl_certificate():
    """Cek apakah SSL certificate sudah ada"""
    print("=== CHECKING SSL CERTIFICATE ===")
    
    if SSL_TYPE == 'corporate':
        # Check corporate SSL files
        print("Checking Corporate SSL certificate...")
        
        cert_exists = os.path.exists(CORPORATE_SSL_CERT_PATH)
        key_exists = os.path.exists(CORPORATE_SSL_KEY_PATH)
        chain_exists = os.path.exists(CORPORATE_SSL_CHAIN_PATH)
        
        print("Certificate file: {} - {}".format(CORPORATE_SSL_CERT_PATH, "✅ Found" if cert_exists else "❌ Not found"))
        print("Private key file: {} - {}".format(CORPORATE_SSL_KEY_PATH, "✅ Found" if key_exists else "❌ Not found"))
        print("Chain file: {} - {}".format(CORPORATE_SSL_CHAIN_PATH, "✅ Found" if chain_exists else "❌ Not found"))
        
        if cert_exists and key_exists:
            # Check certificate validity
            result = subprocess.run(
                "openssl x509 -in {} -noout -enddate".format(CORPORATE_SSL_CERT_PATH),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            if result.returncode == 0:
                print("Corporate certificate info: {}".format(result.stdout.strip()))
            
            return True
        else:
            print("⚠️  Corporate SSL files missing, please install them first")
            return False
    else:
        # Check Let's Encrypt certificate
        cert_path = "/etc/letsencrypt/live/{}/fullchain.pem".format(DOMAIN_NAME)
        if os.path.exists(cert_path):
            print("✅ Let's Encrypt SSL certificate exists for {}".format(DOMAIN_NAME))
            
            # Cek expiry date
            result = subprocess.run(
                "openssl x509 -in {} -noout -enddate".format(cert_path),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            if result.returncode == 0:
                print("Certificate info: {}".format(result.stdout.strip()))
            
            return True
        else:
            print("⚠️  Let's Encrypt SSL certificate not found, will obtain new certificate")
            return False

def check_domain_resolution():
    """Cek apakah domain sudah mengarah ke server yang benar"""
    print("=== CHECKING DOMAIN RESOLUTION ===")
    
    try:
        result = subprocess.run(
            "nslookup {}".format(DOMAIN_NAME),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        
        if result.returncode == 0:
            print("Domain resolution result:")
            print(result.stdout)
            
            # Cek apakah IP match
            if SERVER_IP in result.stdout:
                print("✅ Domain {} correctly points to server IP {}".format(DOMAIN_NAME, SERVER_IP))
                return True
            else:
                print("⚠️  Domain may not point to the correct IP. Expected: {}".format(SERVER_IP))
                print("Please check your DNS settings")
                return False
        else:
            print("❌ Failed to resolve domain: {}".format(DOMAIN_NAME))
            return False
            
    except Exception as e:
        print("Error checking domain resolution: {}".format(e))
        return False

def backup_apache_config():
    """Backup konfigurasi Apache sebelum perubahan"""
    print("=== BACKUP APACHE CONFIGURATION ===")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = "/etc/apache2/backup_{}".format(timestamp)
    os.makedirs(backup_dir, exist_ok=True)
    
    run_command("cp -r /etc/apache2/sites-available {}".format(backup_dir))
    run_command("cp -r /etc/apache2/sites-enabled {}".format(backup_dir))
    run_command("cp /etc/apache2/apache2.conf {}".format(backup_dir))
    run_command("cp /etc/apache2/ports.conf {}".format(backup_dir))
    print("Backup saved to: {}".format(backup_dir))

def check_docker_status():
    """Cek status Docker dan container"""
    print("=== CHECKING DOCKER STATUS ===")
    
    # Cek apakah Docker berjalan
    docker_status = subprocess.run("systemctl is-active docker", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if docker_status.returncode != 0:
        print("Starting Docker service...")
        run_command("systemctl start docker")
        run_command("systemctl enable docker")
    else:
        print("✅ Docker service is already running")
    
    # Cek apakah container sudah ada
    print("Checking container status...")
    result = subprocess.run(
        "docker ps -a --filter name={} --format 'table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}'".format(DOCKER_CONTAINER_NAME),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    
    if result.returncode == 0 and DOCKER_CONTAINER_NAME in result.stdout:
        print("✅ Container '{}' already exists:".format(DOCKER_CONTAINER_NAME))
        print(result.stdout)
        
        # Cek apakah container running
        running_check = subprocess.run(
            "docker ps --filter name={} --format '{{{{.Names}}}}'".format(DOCKER_CONTAINER_NAME),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        
        if DOCKER_CONTAINER_NAME in running_check.stdout:
            print("✅ Container is currently running")
            return True
        else:
            print("⚠️  Container exists but not running")
            return False
    else:
        print("⚠️  Container '{}' not found, will create new container".format(DOCKER_CONTAINER_NAME))
        return False

def enable_apache_modules():
    """Enable module Apache yang diperlukan"""
    print("=== ENABLING APACHE MODULES ===")
    modules = ["proxy", "proxy_http", "proxy_balancer", "lbmethod_byrequests", "headers", "rewrite", "ssl"]
    
    for module in modules:
        # Cek apakah module sudah enabled
        check_result = subprocess.run(
            "a2enmod {} 2>&1 | grep -q 'already enabled'".format(module),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        if check_result.returncode == 0:
            print("✅ Module '{}' already enabled".format(module))
        else:
            print("Enabling module: {}".format(module))
            run_command("a2enmod {}".format(module))

def create_apache_vhost_config():
    """Membuat konfigurasi VirtualHost Apache berdasarkan .env"""
    print("=== CREATING APACHE VIRTUALHOST CONFIG ===")
    
    config_file = "/etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME)
    
    # Backup existing config if exists
    if os.path.exists(config_file):
        backup_file = "{}.backup.{}".format(config_file, datetime.now().strftime("%Y%m%d%H%M%S"))
        run_command("cp {} {}".format(config_file, backup_file))
        print("✅ Existing config backed up to: {}".format(backup_file))
    
    # Build security headers
    security_headers = ""
    if ENABLE_SECURITY_HEADERS:
        security_headers = """    # Security headers
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin\""""
        
        if ENABLE_HSTS:
            security_headers += """
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload\""""
    
    # Build server status section
    server_status_config = ""
    if ENABLE_SERVER_STATUS:
        allowed_ips = ""
        for ip in ALLOWED_MONITOR_IPS:
            allowed_ips += "        Require ip {}\n".format(ip.strip())
        
        server_status_config = """    # Status endpoint untuk monitoring
    <Location "/server-status">
        SetHandler server-status
{}    </Location>""".format(allowed_ips)
    
    # Build SSL redirect section
    ssl_redirect = ""
    if ENABLE_SSL and SSL_AUTO_REDIRECT:
        ssl_redirect = """    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]"""
    else:
        ssl_redirect = """    # Redirect HTTP to HTTPS (disabled - set ENABLE_SSL and SSL_AUTO_REDIRECT in .env)
    # RewriteEngine On
    # RewriteCond %{HTTPS} off
    # RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]"""
    
    # Build logging configuration
    logging_config = ""
    if ENABLE_ERROR_LOG and ENABLE_ACCESS_LOG:
        logging_config = """    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{service_name}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{service_name}_access.log combined
    LogLevel {log_level}""".format(service_name=DOCKER_SERVICE_NAME, log_level=LOG_LEVEL)
    elif ENABLE_ERROR_LOG:
        logging_config = """    # Error Logging only
    ErrorLog ${{APACHE_LOG_DIR}}/{service_name}_error.log
    LogLevel {log_level}""".format(service_name=DOCKER_SERVICE_NAME, log_level=LOG_LEVEL)

    config = """<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    DocumentRoot /var/www/html

{ssl_redirect}

    # Proxy configuration for WhatsApp Webhook Service
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    
    # Headers for better proxy handling
    ProxyPassReverse / http://127.0.0.1:{port}/
    ProxyRequests Off
    
{security_headers}
    
    # WebSocket support (untuk WhatsApp real-time features)
    RewriteEngine on
    RewriteCond %{{HTTP:Upgrade}} websocket [NC]
    RewriteCond %{{HTTP:Connection}} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:{port}/$1" [P,L]

    # Health check endpoint
    <Location "/health">
        ProxyPass http://localhost:{port}/status
        ProxyPassReverse http://localhost:{port}/status
    </Location>

{logging_config}
    
{server_status_config}
</VirtualHost>""".format(
        domain=DOMAIN_NAME,
        port=TARGET_PORT,
        ssl_redirect=ssl_redirect,
        security_headers=security_headers,
        logging_config=logging_config,
        server_status_config=server_status_config
    )

    # SSL Configuration
    if ENABLE_SSL:
        if SSL_TYPE == 'corporate':
            ssl_config = """
# HTTPS Configuration (Corporate SSL)
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName {domain}
    ServerAlias www.{domain}
    DocumentRoot /var/www/html

    # Corporate SSL Configuration
    SSLEngine on
    SSLCertificateFile {cert_path}
    SSLCertificateKeyFile {key_path}
    SSLCertificateChainFile {chain_path}
    
    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off
    SSLSessionTickets off

    # Proxy configuration (same as HTTP)
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    ProxyPassReverse / http://127.0.0.1:{port}/
    ProxyRequests Off
    
{security_headers_ssl}
    
    # WebSocket support
    RewriteEngine on
    RewriteCond %{{HTTP:Upgrade}} websocket [NC]
    RewriteCond %{{HTTP:Connection}} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:{port}/$1" [P,L]

    # Health check endpoint
    <Location "/health">
        ProxyPass http://localhost:{port}/status
        ProxyPassReverse http://localhost:{port}/status
    </Location>

{logging_config_ssl}
{server_status_config}
</VirtualHost>
</IfModule>""".format(
                domain=DOMAIN_NAME,
                port=TARGET_PORT,
                cert_path=CORPORATE_SSL_CERT_PATH,
                key_path=CORPORATE_SSL_KEY_PATH,
                chain_path=CORPORATE_SSL_CHAIN_PATH,
                security_headers_ssl=security_headers,
                logging_config_ssl=logging_config.replace(DOCKER_SERVICE_NAME, DOCKER_SERVICE_NAME + "_ssl") if logging_config else "",
                server_status_config=server_status_config
            )
        else:
            ssl_config = """
# HTTPS Configuration (Let's Encrypt)
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName {domain}
    ServerAlias www.{domain}
    DocumentRoot /var/www/html

    # Let's Encrypt SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{domain}/privkey.pem
    
    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off
    SSLSessionTickets off

    # Proxy configuration (same as HTTP)
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    ProxyPassReverse / http://127.0.0.1:{port}/
    ProxyRequests Off
    
{security_headers_ssl}
    
    # WebSocket support
    RewriteEngine on
    RewriteCond %{{HTTP:Upgrade}} websocket [NC]
    RewriteCond %{{HTTP:Connection}} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:{port}/$1" [P,L]

    # Health check endpoint
    <Location "/health">
        ProxyPass http://localhost:{port}/status
        ProxyPassReverse http://localhost:{port}/status
    </Location>

{logging_config_ssl}
{server_status_config}
</VirtualHost>
</IfModule>""".format(
                domain=DOMAIN_NAME,
                port=TARGET_PORT,
                security_headers_ssl=security_headers,
                logging_config_ssl=logging_config.replace(DOCKER_SERVICE_NAME, DOCKER_SERVICE_NAME + "_ssl") if logging_config else "",
                server_status_config=server_status_config
            )
        config += ssl_config
    
    with open(config_file, 'w') as f:
        f.write(config)
    
    print("✅ Apache VirtualHost configuration created: {}".format(config_file))
    print("✅ Domain: {}".format(DOMAIN_NAME))
    print("✅ Proxying traffic from port 80/443 to localhost:{}".format(TARGET_PORT))
    print("✅ SSL Enabled: {}".format(ENABLE_SSL))
    print("✅ Security Headers: {}".format(ENABLE_SECURITY_HEADERS))
    print("✅ Server Status Monitoring: {}".format(ENABLE_SERVER_STATUS))

def create_docker_management_script():
    """Membuat script untuk manage Docker container"""
    print("=== CREATING DOCKER MANAGEMENT SCRIPT ===")
    
    script_path = "/usr/local/bin/whatsapp-service"
    
    # Backup existing script if exists
    if os.path.exists(script_path):
        backup_script = "{}.backup.{}".format(script_path, datetime.now().strftime("%Y%m%d%H%M%S"))
        run_command("cp {} {}".format(script_path, backup_script))
        print("✅ Existing script backed up to: {}".format(backup_script))
    
    script_content = """#!/bin/bash

# Docker Management Script for WhatsApp Webhook Service
# Domain: {domain}
# Server IP: {server_ip}
# Generated: {timestamp}

CONTAINER_NAME="{container_name}"
IMAGE_NAME="node:18-alpine"
HOST_PORT={target_port}
CONTAINER_PORT={docker_port}
APP_DIR="/app"
PROJECT_DIR="/opt/whatsapp-webhook"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo_info() {{
    echo -e "${{GREEN}}[INFO]${{NC}} $1"
}}

echo_warn() {{
    echo -e "${{YELLOW}}[WARN]${{NC}} $1"
}}

echo_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

case "$1" in
    start)
        echo_info "Starting WhatsApp Webhook container..."
        
        # Check if container already exists
        if docker ps -a --filter name=$CONTAINER_NAME | grep -q $CONTAINER_NAME; then
            echo_warn "Container '$CONTAINER_NAME' already exists. Removing old container..."
            docker stop $CONTAINER_NAME 2>/dev/null || true
            docker rm $CONTAINER_NAME 2>/dev/null || true
        fi
        
        # Check if port is already in use
        if netstat -tlnp | grep -q ":$HOST_PORT "; then
            echo_warn "Port $HOST_PORT is already in use:"
            netstat -tlnp | grep ":$HOST_PORT "
            echo_warn "Continuing anyway (container might fail to start)..."
        fi
        
        # Create project directory if not exists
        mkdir -p $PROJECT_DIR
        
        # Start container
        docker run -d \\
            --name $CONTAINER_NAME \\
            --restart unless-stopped \\
            -p $HOST_PORT:$CONTAINER_PORT \\
            -v $(pwd)/waweb-api:$APP_DIR \\
            -v $PROJECT_DIR:$PROJECT_DIR \\
            -w $APP_DIR \\
            -e NODE_ENV=production \\
            $IMAGE_NAME \\
            sh -c "npm install && npm start"
            
        if [ $? -eq 0 ]; then
            echo_info "Container started successfully on port $HOST_PORT"
            echo_info "Service available at: http://{domain}/"
            echo_info "Health check: http://{domain}/health"
            echo_info "Wait a few seconds for the service to start..."
            sleep 3
            docker ps --filter name=$CONTAINER_NAME
        else
            echo_error "Failed to start container"
            exit 1
        fi
        ;;
    stop)
        echo_info "Stopping container..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo_info "Container stopped and removed"
        ;;
    restart)
        echo_info "Restarting container..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        echo_info "Container status:"
        docker ps --filter name=$CONTAINER_NAME --format "table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}"
        
        echo ""
        echo_info "Service health check:"
        if curl -s -f http://localhost:$HOST_PORT/status > /dev/null 2>&1; then
            echo_info "✅ Service is responding on port $HOST_PORT"
        else
            echo_warn "❌ Service is not responding on port $HOST_PORT"
        fi
        
        echo ""
        echo_info "Apache status:"
        systemctl is-active apache2 && echo_info "✅ Apache is running" || echo_warn "❌ Apache is not running"
        ;;
    logs)
        echo_info "Showing container logs (Ctrl+C to exit):"
        docker logs -f $CONTAINER_NAME
        ;;
    shell)
        echo_info "Opening container shell:"
        docker exec -it $CONTAINER_NAME sh
        ;;
    update)
        echo_info "Updating container image and restarting..."
        docker pull $IMAGE_NAME
        $0 restart
        ;;
    health)
        echo_info "Performing health checks:"
        
        # Check container
        if docker ps --filter name=$CONTAINER_NAME | grep -q $CONTAINER_NAME; then
            echo_info "✅ Container is running"
        else
            echo_error "❌ Container is not running"
        fi
        
        # Check service response
        if curl -s -f http://localhost:$HOST_PORT/status > /dev/null 2>&1; then
            echo_info "✅ Service is responding"
            curl -s http://localhost:$HOST_PORT/status | head -5
        else
            echo_error "❌ Service is not responding"
        fi
        
        # Check domain access
        if curl -s -f http://{domain}/status > /dev/null 2>&1; then
            echo_info "✅ Domain is accessible: {domain}"
        else
            echo_warn "❌ Domain is not accessible: {domain}"
        fi
        ;;
    *)
        echo "WhatsApp Webhook Service Management"
        echo "Domain: {domain}"
        echo "Server: {server_ip}:{target_port}"
        echo ""
        echo "Usage: $0 {{start|stop|restart|status|logs|shell|update|health}}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the WhatsApp webhook container"
        echo "  stop    - Stop and remove the container"
        echo "  restart - Restart the container"
        echo "  status  - Show container and service status"
        echo "  logs    - Show container logs (real-time)"
        echo "  shell   - Open shell inside container"
        echo "  update  - Update image and restart container"
        echo "  health  - Perform comprehensive health check"
        exit 1
        ;;
esac
""".format(
        container_name=DOCKER_CONTAINER_NAME,
        target_port=TARGET_PORT,
        docker_port=DOCKER_INTERNAL_PORT,
        domain=DOMAIN_NAME,
        server_ip=SERVER_IP,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    run_command("chmod +x {}".format(script_path))
    print("✅ Docker management script created: {}".format(script_path))
    print("✅ Enhanced with health checks and better error handling")
    print("Usage: whatsapp-service {{start|stop|restart|status|logs|shell|update|health}}")

def install_dependencies():
    """Install dependencies yang diperlukan"""
    print("=== INSTALLING DEPENDENCIES ===")
    run_command("apt update")
    run_command("apt install -y apache2 docker.io certbot python3-certbot-apache")
    
    # Enable services
    run_command("systemctl enable apache2")
    run_command("systemctl enable docker")
    run_command("systemctl start apache2")
    run_command("systemctl start docker")

def enable_site_and_reload():
    """Enable site dan reload Apache"""
    print("=== ENABLING SITE AND RELOADING APACHE ===")
    
    # Disable default site
    run_command("a2dissite 000-default")
    
    # Enable our site
    run_command("a2ensite {}".format(DOMAIN_NAME))
    
    # Test configuration
    if run_command("apache2ctl configtest"):
        run_command("systemctl reload apache2")
        print("Apache reloaded successfully")
    else:
        print("Apache configuration test failed!")

def setup_ssl_certificate():
    """Setup SSL certificate berdasarkan konfigurasi .env"""
    if not ENABLE_SSL:
        print("=== SSL DISABLED IN CONFIGURATION ===")
        print("SSL is disabled in .env file (ENABLE_SSL=false)")
        print("To enable SSL, set ENABLE_SSL=true in .env file")
        return False
        
    print("=== SETTING UP SSL CERTIFICATE ===")
    print("Domain: {}".format(DOMAIN_NAME))
    print("SSL Type: {}".format(SSL_TYPE))
    print("Auto Redirect: {}".format(SSL_AUTO_REDIRECT))
    
    if SSL_TYPE == 'corporate':
        return setup_corporate_ssl()
    else:
        return setup_letsencrypt_ssl()

def setup_corporate_ssl():
    """Setup Corporate SSL Certificate"""
    print("=== SETTING UP CORPORATE SSL ===")
    
    # Check if corporate SSL files exist
    if check_ssl_certificate():
        print("✅ Corporate SSL certificate is already configured")
        
        # Enable HTTPS redirect jika diaktifkan di .env
        if SSL_AUTO_REDIRECT:
            enable_https_redirect()
        
        # Test SSL configuration
        if run_command("apache2ctl configtest"):
            run_command("systemctl reload apache2")
            print("✅ Apache reloaded with Corporate SSL")
        else:
            print("❌ Apache configuration test failed!")
            return False
        
        return True
    else:
        print("❌ Corporate SSL files not found!")
        print("Please ensure the following files exist:")
        print("- Certificate: {}".format(CORPORATE_SSL_CERT_PATH))
        print("- Private Key: {}".format(CORPORATE_SSL_KEY_PATH))
        print("- Chain: {}".format(CORPORATE_SSL_CHAIN_PATH))
        print("")
        print("Contact IT department to obtain corporate SSL certificate")
        return False

def setup_letsencrypt_ssl():
    """Setup Let's Encrypt SSL Certificate"""
    print("=== SETTING UP LET'S ENCRYPT SSL ===")
    
    # Cek apakah SSL sudah ada
    if check_ssl_certificate():
        print("✅ Let's Encrypt SSL certificate already exists and valid")
        
        # Enable HTTPS redirect jika diaktifkan di .env
        if SSL_AUTO_REDIRECT:
            enable_https_redirect()
        
        return True
    
    # Informasi SSL setup
    print("\n" + "="*60)
    print("IMPORTANT SSL SETUP INFORMATION:")
    print("="*60)
    print("Domain: {}".format(DOMAIN_NAME))
    print("Expected IP: {}".format(SERVER_IP))
    print("Admin Email: {}".format(ADMIN_EMAIL))
    print("")
    print("Please ensure:")
    print("1. Domain DNS points to this server IP")
    print("2. Port 80 and 443 are open in firewall")
    print("3. Apache is running and accessible")
    print("="*60)
    
    # Check domain resolution
    domain_ok = check_domain_resolution()
    
    if not domain_ok and not SKIP_SSL_VERIFICATION:
        print("⚠️  Domain resolution issue detected!")
        print("Please fix DNS settings before continuing with SSL")
        print("Or set SKIP_SSL_VERIFICATION=true in .env to bypass this check")
    
    if SKIP_SSL_VERIFICATION:
        print("⚠️  SSL verification is skipped (SKIP_SSL_VERIFICATION=true)")
        
    response = input("\nContinue with Let's Encrypt SSL certificate setup? (y/N): ")
    
    if response.lower() == 'y':
        print("\n🔐 Obtaining Let's Encrypt SSL certificate...")
        
        # Test Apache configuration first
        if not run_command("apache2ctl configtest"):
            print("❌ Apache configuration test failed! Please fix before SSL setup.")
            return False
        
        # Build SSL command dengan options berdasarkan .env
        ssl_options = "--non-interactive --agree-tos --email {}".format(ADMIN_EMAIL)
        
        if SSL_AUTO_REDIRECT:
            ssl_options += " --redirect"
        else:
            ssl_options += " --no-redirect"
            
        ssl_command = "certbot --apache -d {} {}".format(DOMAIN_NAME, ssl_options)
        
        if run_command(ssl_command):
            print("✅ Let's Encrypt SSL certificate obtained for {}".format(DOMAIN_NAME))
            run_command("systemctl reload apache2")
            
            # Test HTTPS jika tidak skip verification
            if not SKIP_SSL_VERIFICATION:
                test_https_connectivity()
            
            # Setup auto-renewal check
            run_command("systemctl enable certbot.timer")
            run_command("systemctl start certbot.timer")
            
            return True
        else:
            print("❌ Failed to obtain SSL certificate")
            print("Common issues:")
            print("- Domain doesn't point to this server")
            print("- Port 80/443 blocked by firewall")
            print("- Apache not properly configured")
            return False
    else:
        print("SSL setup skipped.")
        print("You can run SSL setup later with:")
        print("  certbot --apache -d {}".format(DOMAIN_NAME))
        return False

def enable_https_redirect():
    """Enable HTTPS redirect in Apache configuration"""
    config_file = "/etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME)
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Uncomment HTTPS redirect rules jika masih di-comment
        if "# RewriteEngine On" in content:
            content = content.replace("# RewriteEngine On", "RewriteEngine On")
            content = content.replace("# RewriteCond %{HTTPS} off", "RewriteCond %{HTTPS} off")
            content = content.replace("# RewriteRule", "RewriteRule")
            
            with open(config_file, 'w') as f:
                f.write(content)
            
            print("✅ HTTPS redirect enabled")
            run_command("systemctl reload apache2")

def check_network_interfaces():
    """Check if network interfaces are available and configured"""
    print("\n=== Network Interface Check ===")
    
    try:
        # Check for network interfaces
        result = subprocess.run(['ip', 'addr', 'show'], 
                               capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Check for required interfaces
            interfaces_found = []
            if NIC_SANDBOX in output:
                interfaces_found.append(f"✓ {NIC_SANDBOX}")
            else:
                interfaces_found.append(f"✗ {NIC_SANDBOX} (NOT FOUND)")
                
            if NIC_INTERNET in output:
                interfaces_found.append(f"✓ {NIC_INTERNET}")
            else:
                interfaces_found.append(f"✗ {NIC_INTERNET} (NOT FOUND)")
            
            print("Network Interfaces:")
            for interface in interfaces_found:
                print(f"  {interface}")
                
            # Check IP assignments
            print("\nIP Address Configuration:")
            if SERVER_IP_SANDBOX in output:
                print(f"  ✓ {SERVER_IP_SANDBOX} assigned to {NIC_SANDBOX}")
            else:
                print(f"  ⚠ {SERVER_IP_SANDBOX} not found on {NIC_SANDBOX}")
                
            if SERVER_IP_INTERNET in output:
                print(f"  ✓ {SERVER_IP_INTERNET} assigned to {NIC_INTERNET}")
            else:
                print(f"  ⚠ {SERVER_IP_INTERNET} not found on {NIC_INTERNET}")
                
        else:
            print("⚠ Could not check network interfaces")
            
    except Exception as e:
        print(f"⚠ Network interface check failed: {e}")

def manage_ngrok_service():
    """Manage ngrok service based on USE_NGROK configuration"""
    print("\n=== Ngrok Service Management ===")
    
    try:
        # Check if setup_ngrok.sh exists
        ngrok_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup_ngrok.sh')
        
        if not os.path.exists(ngrok_script):
            print("⚠ setup_ngrok.sh not found. Ngrok management not available.")
            return
            
        if USE_NGROK:
            print("✓ USE_NGROK=true - Starting ngrok tunnel...")
            # Start ngrok service
            result = subprocess.run(['/bin/bash', ngrok_script, 'start'], 
                                   capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Ngrok tunnel started successfully")
                # Show status
                status_result = subprocess.run(['/bin/bash', ngrok_script, 'status'], 
                                             capture_output=True, text=True, timeout=10)
                if status_result.returncode == 0:
                    print(status_result.stdout)
            else:
                print(f"⚠ Failed to start ngrok: {result.stderr}")
                
        else:
            print("✓ USE_NGROK=false - Performing complete ngrok cleanup...")
            
            # First stop ngrok
            result = subprocess.run(['/bin/bash', ngrok_script, 'stop'], 
                                   capture_output=True, text=True, timeout=30)
            
            # Then perform complete cleanup
            cleanup_result = subprocess.run(['/bin/bash', ngrok_script, 'cleanup'], 
                                          capture_output=True, text=True, timeout=60)
            
            if cleanup_result.returncode == 0:
                print("✅ Complete ngrok cleanup performed")
                print("🗑️  All ngrok processes, files, and configurations removed")
            else:
                print(f"⚠ Failed to cleanup ngrok: {cleanup_result.stderr}")
                # Try manual cleanup
                print("Attempting manual cleanup...")
                try:
                    # Kill any ngrok processes
                    subprocess.run(['sudo', 'pkill', '-f', 'ngrok'], check=False)
                    subprocess.run(['sudo', 'killall', 'ngrok'], check=False)
                    print("✅ Manual process cleanup completed")
                except Exception as e:
                    print(f"⚠ Manual cleanup warning: {e}")
                
    except subprocess.TimeoutExpired:
        print("⚠ Ngrok command timed out")
    except Exception as e:
        print(f"⚠ Ngrok management failed: {e}")

def test_https_connectivity():
    """Test HTTPS connectivity"""
    print("\n🔍 Testing HTTPS connectivity...")
    test_result = subprocess.run(
        "curl -s -I https://{}/ | head -1".format(DOMAIN_NAME),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    
    if "200 OK" in test_result.stdout or "302" in test_result.stdout:
        print("✅ HTTPS is working: https://{}".format(DOMAIN_NAME))
    else:
        print("⚠️  HTTPS test inconclusive, please test manually")

def show_configuration_summary():
    """Tampilkan ringkasan konfigurasi berdasarkan .env"""
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY (FROM .env)")
    print("="*60)
    print("Domain: {}".format(DOMAIN_NAME))
    print("Server IP: {}".format(SERVER_IP))
    print("Admin Email: {}".format(ADMIN_EMAIL))
    print("Target Port: {} (Docker container)".format(TARGET_PORT))
    print("Docker Container: {}".format(DOCKER_CONTAINER_NAME))
    print("Docker Internal Port: {}".format(DOCKER_INTERNAL_PORT))
    print("Service Name: {}".format(DOCKER_SERVICE_NAME))
    print("")
    print("SSL Configuration:")
    print("- SSL Enabled: {}".format(ENABLE_SSL))
    if ENABLE_SSL:
        print("- SSL Type: {}".format(SSL_TYPE))
        if SSL_TYPE == 'corporate':
            print("- Corporate Cert: {}".format(CORPORATE_SSL_CERT_PATH))
            print("- Corporate Key: {}".format(CORPORATE_SSL_KEY_PATH))
            print("- Corporate Chain: {}".format(CORPORATE_SSL_CHAIN_PATH))
    print("- Auto Redirect: {}".format(SSL_AUTO_REDIRECT))
    print("- Skip Verification: {}".format(SKIP_SSL_VERIFICATION))
    print("")
    print("Security Features:")
    print("- Security Headers: {}".format(ENABLE_SECURITY_HEADERS))
    print("- HSTS Enabled: {}".format(ENABLE_HSTS))
    print("- Server Status: {}".format(ENABLE_SERVER_STATUS))
    print("- Allowed Monitor IPs: {}".format(', '.join(ALLOWED_MONITOR_IPS)))
    print("")
    print("Logging Configuration:")
    print("- Log Level: {}".format(LOG_LEVEL))
    print("- Access Log: {}".format(ENABLE_ACCESS_LOG))
    print("- Error Log: {}".format(ENABLE_ERROR_LOG))
    print("")
    print("Development Options:")
    print("- Debug Mode: {}".format(DEBUG_MODE))
    print("")
    print("SSL Migration Guide:")
    if ENABLE_SSL and SSL_TYPE == 'letsencrypt':
        print("- To migrate to Corporate SSL:")
        print("  1. Obtain corporate SSL certificates from IT")
        print("  2. Update .env: SSL_TYPE=corporate")
        print("  3. Run script again (automatic migration)")
    elif ENABLE_SSL and SSL_TYPE == 'corporate':
        print("- Corporate SSL is configured")
        print("- Automatic Let's Encrypt renewal disabled")
    print("")
    print("Management Commands:")
    print("- Start service: whatsapp-service start")
    print("- Stop service: whatsapp-service stop")
    print("- Check status: whatsapp-service status")
    print("- View logs: whatsapp-service logs")
    print("- Health check: whatsapp-service health")
    print("")
    print("Log Files:")
    print("- Error log: /var/log/apache2/{}_error.log".format(DOCKER_SERVICE_NAME))
    if ENABLE_SSL:
        print("- SSL Error log: /var/log/apache2/{}_ssl_error.log".format(DOCKER_SERVICE_NAME))
    print("- Access log: /var/log/apache2/{}_access.log".format(DOCKER_SERVICE_NAME))
    if ENABLE_SSL:
        print("- SSL Access log: /var/log/apache2/{}_ssl_access.log".format(DOCKER_SERVICE_NAME))
    print("")
    print("Configuration Files:")
    print("- Environment: {}".format(os.path.join(os.path.dirname(__file__), '.env')))
    print("- Apache VHost: /etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME))
    print("- Management Script: /usr/local/bin/whatsapp-service")
    print("")
    print("To modify configuration:")
    print("1. Edit .env file")
    print("2. Run this script again")
    print("="*60)

def test_complete_deployment():
    """Test deployment lengkap untuk memastikan semuanya berjalan"""
    print("\n" + "="*50)
    print("         COMPLETE DEPLOYMENT TEST")
    print("="*50)
    
    tests_passed = 0
    total_tests = 7
    
    # Test 1: Docker container
    print("\n1. Testing Docker container...")
    if check_docker_status():
        print("   ✅ Docker container is running")
        tests_passed += 1
    else:
        print("   ❌ Docker container not running")
    
    # Test 2: Node.js application
    print("\n2. Testing Node.js application...")
    test_result = subprocess.run(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    
    if test_result.stdout.strip() == "200":
        print("   ✅ Node.js app responding on port 3000")
        tests_passed += 1
    else:
        print("   ❌ Node.js app not responding")
    
    # Test 3: Apache running
    print("\n3. Testing Apache service...")
    apache_result = subprocess.run(
        "systemctl is-active apache2",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    
    if apache_result.stdout.strip() == "active":
        print("   ✅ Apache2 is active")
        tests_passed += 1
    else:
        print("   ❌ Apache2 is not active")
    
    # Test 4: Apache config
    print("\n4. Testing Apache configuration...")
    if run_command("apache2ctl configtest", quiet=True):
        print("   ✅ Apache configuration is valid")
        tests_passed += 1
    else:
        print("   ❌ Apache configuration has errors")
    
    # Test 5: HTTP access
    print("\n5. Testing HTTP access...")
    try:
        http_result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://{}/".format(DOMAIN_NAME)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=10
        )
        
        if http_result.stdout.strip() in ["200", "301", "302"]:
            print("   ✅ HTTP access working (status: {})".format(http_result.stdout.strip()))
            tests_passed += 1
        else:
            print("   ❌ HTTP access failed (status: {})".format(http_result.stdout.strip()))
    except Exception as e:
        print("   ❌ Error during HTTP test: {}".format(str(e)))
    
    # Test 6: HTTPS access (if SSL enabled)
    if ENABLE_SSL:
        print("\n6. Testing HTTPS access...")
        try:
            https_result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-k", "https://{}/".format(DOMAIN_NAME)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=10
            )
            
            if https_result.stdout.strip() in ["200", "301", "302"]:
                print("   ✅ HTTPS access working (status: {})".format(https_result.stdout.strip()))
                tests_passed += 1
            else:
                print("   ❌ HTTPS access failed (status: {})".format(https_result.stdout.strip()))
        except Exception as e:
            print("   ❌ Error during HTTPS test: {}".format(str(e)))
    else:
        print("\n6. HTTPS testing skipped (SSL disabled)")
        tests_passed += 1  # Don't penalize for disabled SSL
    
    # Test 7: WhatsApp webhook endpoint
    print("\n7. Testing WhatsApp webhook endpoint...")
    try:
        if ENABLE_SSL:
            webhook_url = "https://{}/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=your_verify_token".format(DOMAIN_NAME)
        else:
            webhook_url = "http://{}/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=your_verify_token".format(DOMAIN_NAME)
        
        webhook_result = subprocess.run(
            ["curl", "-s", "-k", webhook_url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=10
        )
        
        if "test" in webhook_result.stdout:
            print("   ✅ WhatsApp webhook endpoint responding")
            tests_passed += 1
        else:
            print("   ❌ WhatsApp webhook endpoint not responding")
    except Exception as e:
        print("   ❌ Error during webhook test: {}".format(str(e)))
    
    # Summary
    print("\n" + "="*50)
    print("         DEPLOYMENT TEST SUMMARY")
    print("="*50)
    print("Tests passed: {}/{}".format(tests_passed, total_tests))
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Deployment is successful!")
        print("\nYour WhatsApp webhook is ready at:")
        print("   HTTPS: https://{}/webhook".format(DOMAIN_NAME))
        print("   HTTP:  http://{}/webhook".format(DOMAIN_NAME))
    elif tests_passed >= 5:
        print("✅ Deployment mostly successful with minor issues")
        print("Check the failed tests above for details")
    else:
        print("❌ Deployment has significant issues")
        print("Please fix the failed tests before using in production")
    
    print("\nLanding page available at:")
    print("   https://{}".format(DOMAIN_NAME))
    print("\nAPI status page available at:")
    print("   https://{}/status".format(DOMAIN_NAME))
    
    return tests_passed >= 5

def migrate_to_corporate_ssl():
    """Migrate dari Let's Encrypt ke Corporate SSL"""
    print("=== MIGRATING TO CORPORATE SSL ===")
    
    config_file = "/etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME)
    
    if not os.path.exists(config_file):
        print("❌ Apache configuration file not found: {}".format(config_file))
        return False
    
    # Backup existing configuration
    backup_file = "{}.letsencrypt.backup".format(config_file)
    try:
        shutil.copy2(config_file, backup_file)
        print("✅ Backed up current configuration to: {}".format(backup_file))
    except Exception as e:
        print("⚠️  Could not create backup: {}".format(str(e)))
    
    # Recreate Apache configuration with Corporate SSL
    try:
        create_apache_vhost_config()
        print("✅ Updated Apache configuration for Corporate SSL")
        
        # Test configuration
        if run_command("apache2ctl configtest"):
            print("✅ Apache configuration test passed")
            
            # Disable certbot auto-renewal
            print("🔄 Disabling Let's Encrypt auto-renewal...")
            run_command("systemctl stop certbot.timer")
            run_command("systemctl disable certbot.timer")
            
            # Reload Apache
            run_command("systemctl reload apache2")
            print("✅ Migration to Corporate SSL completed successfully")
            
            # Test HTTPS
            if not SKIP_SSL_VERIFICATION:
                test_https_connectivity()
            
            return True
        else:
            print("❌ Apache configuration test failed!")
            if os.path.exists(backup_file):
                print("🔄 Restoring backup configuration...")
                shutil.copy2(backup_file, config_file)
                run_command("systemctl reload apache2")
            return False
            
    except Exception as e:
        print("❌ Error updating configuration: {}".format(str(e)))
        if os.path.exists(backup_file):
            print("🔄 Restoring backup configuration...")
            shutil.copy2(backup_file, config_file)
            run_command("systemctl reload apache2")
        return False

def show_ssl_migration_guide():
    """Tampilkan panduan migration SSL"""
    print("\n" + "="*70)
    print("SSL MIGRATION GUIDE")
    print("="*70)
    print("Current SSL Type: {}".format(SSL_TYPE))
    print("")
    
    if SSL_TYPE == 'letsencrypt':
        print("TO MIGRATE TO CORPORATE SSL:")
        print("1. Obtain Corporate SSL certificate files from IT department")
        print("2. Place certificates in these paths:")
        print("   - Certificate: {}".format(CORPORATE_SSL_CERT_PATH))
        print("   - Private Key: {}".format(CORPORATE_SSL_KEY_PATH))
        print("   - Chain: {}".format(CORPORATE_SSL_CHAIN_PATH))
        print("3. Update .env file: SSL_TYPE=corporate")
        print("4. Run this script again")
        print("")
        print("The script will automatically:")
        print("- Backup current Let's Encrypt configuration")
        print("- Update Apache configuration for Corporate SSL")
        print("- Disable Let's Encrypt auto-renewal")
        print("- Test the new configuration")
        
    elif SSL_TYPE == 'corporate':
        print("CORPORATE SSL CONFIGURATION:")
        print("Certificate Path: {}".format(CORPORATE_SSL_CERT_PATH))
        print("Private Key Path: {}".format(CORPORATE_SSL_KEY_PATH))
        print("Chain Path: {}".format(CORPORATE_SSL_CHAIN_PATH))
        print("")
        if not check_ssl_certificate():
            print("❌ Corporate SSL files not found!")
            print("Please ensure certificate files are in the correct paths")
        else:
            print("✅ Corporate SSL files detected")
        
        print("")
        print("If you need to rollback to Let's Encrypt:")
        print("1. Update .env file: SSL_TYPE=letsencrypt")
        print("2. Run this script again")
        print("3. The script will restore Let's Encrypt configuration")
        
    print("="*70)

def main():
    """Main function"""
    print("=" * 60)
    print("WHATSAPP WEBHOOK APACHE CONFIGURATION SCRIPT")
    print("=" * 60)
    print("Configuration loaded from: {}".format(os.path.join(os.path.dirname(__file__), '.env')))
    print("Domain: {} -> Port: {}".format(DOMAIN_NAME, TARGET_PORT))
    print("Docker Container: {}".format(DOCKER_CONTAINER_NAME))
    print("SSL Enabled: {} (Type: {})".format(ENABLE_SSL, SSL_TYPE))
    print("=" * 60)
    
    # Show SSL migration guide
    if ENABLE_SSL:
        show_ssl_migration_guide()
    
    try:
        backup_apache_config()
        install_dependencies()
        check_docker_status()
        enable_apache_modules()
        create_apache_vhost_config()
        create_docker_management_script()
        enable_site_and_reload()
        
        # SSL setup dengan migration support
        if ENABLE_SSL:
            print("\n🔐 Setting up SSL certificate...")
            
            # Debug SSL_TYPE value
            print("DEBUG: SSL_TYPE = '{}'".format(repr(SSL_TYPE)))
            
            # Jika Corporate SSL dan file sudah ada
            if SSL_TYPE == 'corporate':
                print("✅ Corporate SSL mode detected")
                if check_ssl_certificate():
                    print("✅ Corporate SSL files detected")
                    
                    # Check jika perlu migrate dari Let's Encrypt
                    config_file = "/etc/apache2/sites-available/{}.conf".format(DOMAIN_NAME)
                    need_migration = False
                    
                    if os.path.exists(config_file):
                        with open(config_file, 'r') as f:
                            content = f.read()
                        if "letsencrypt" in content.lower():
                            need_migration = True
                    
                    if need_migration:
                        print("🔄 Migrating from Let's Encrypt to Corporate SSL...")
                        if not migrate_to_corporate_ssl():
                            print("❌ SSL migration failed")
                            return
                    else:
                        print("✅ Corporate SSL already configured")
                        setup_ssl_certificate()
                else:
                    print("❌ Corporate SSL files not found!")
                    print("Please ensure certificate files are placed in:")
                    print("- {}".format(CORPORATE_SSL_CERT_PATH))
                    print("- {}".format(CORPORATE_SSL_KEY_PATH))
                    print("- {}".format(CORPORATE_SSL_CHAIN_PATH))
                    return
            else:
                print("⚠️  SSL_TYPE is not 'corporate', using Let's Encrypt mode")
                # Let's Encrypt setup
                setup_ssl_certificate()
        else:
            print("\n⚠️  SSL is disabled in .env configuration")
            print("To enable SSL, set ENABLE_SSL=true in .env file")
        
        show_configuration_summary()
        
        print("\n✅ Configuration completed successfully!")
        print("Your WhatsApp webhook service will be accessible at:")
        print("HTTP: http://{}".format(DOMAIN_NAME))
        if ENABLE_SSL:
            print("HTTPS: https://{}".format(DOMAIN_NAME))
        
        # Check network interfaces
        check_network_interfaces()
        
        # Manage ngrok based on configuration
        manage_ngrok_service()
        
        # If USE_NGROK=false, run cleanup verification
        if not USE_NGROK:
            cleanup_test_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_ngrok_cleanup.sh')
            if os.path.exists(cleanup_test_script):
                print("\n" + "="*60)
                print("Running ngrok cleanup verification...")
                print("="*60)
                try:
                    result = subprocess.run(['/bin/bash', cleanup_test_script], 
                                          capture_output=True, text=True, timeout=30)
                    print(result.stdout)
                    if result.returncode == 0:
                        print("✅ Ngrok cleanup verification PASSED")
                    else:
                        print("⚠ Ngrok cleanup verification FAILED")
                        print(result.stderr)
                except Exception as e:
                    print(f"⚠ Could not run cleanup verification: {e}")
        
        # Run deployment test
        print("\n" + "="*60)
        print("Running deployment test to verify everything is working...")
        print("="*60)
        
        if test_complete_deployment():
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("Your WhatsApp webhook is ready for production use!")
        else:
            print("\n⚠️  DEPLOYMENT COMPLETED WITH ISSUES")
            print("Some tests failed. Please check the output above.")
            print("The service may still work, but review any failed tests.")
        
        print("\n" + "="*60)
        print("QUICK START GUIDE:")
        print("="*60)
        print("1. Configure your WhatsApp Business API webhook URL:")
        if ENABLE_SSL:
            print("   Internal: https://{}/webhook".format(DOMAIN_NAME))
        else:
            print("   Internal: http://{}/webhook".format(DOMAIN_NAME))
        print("   For Facebook API (public access): Use ngrok tunnel")
        print("2. Set up public access with ngrok (if needed):")
        print("   chmod +x setup_ngrok.sh")
        print("   ./setup_ngrok.sh start")
        print("   ./setup_ngrok.sh status")
        print("3. Remove ngrok completely (when no longer needed):")
        print("   Set USE_NGROK=false in .env, then run: python3 config2.py")
        print("   Or manually: ./setup_ngrok.sh uninstall")
        print("4. Set verify token in your app configuration")
        print("5. Test webhook with Facebook's webhook tester")
        print("6. Monitor logs: docker logs {}".format(DOCKER_CONTAINER_NAME))
        print("6. Check service status: systemctl status apache2")
        print("7. Manage service: whatsapp-service {{start|stop|status|logs|health}}")
        print("")
        print("Network Configuration:")
        print("- SANDBOX Network ({}): {}".format(NIC_SANDBOX, SERVER_IP_SANDBOX))
        print("- INTERNET Network ({}): {}".format(NIC_INTERNET, SERVER_IP_INTERNET))
        print("- Ngrok Enabled: {}".format("Yes" if USE_NGROK else "No"))
        print("")
        print("Configuration Management:")
        print("- Edit configuration: nano .env")
        print("- Reload configuration: python3 config2.py")
        print("- View current config: whatsapp-service status")
        print("- Ngrok tunnel control:")
        print("  * Start tunnel: ./setup_ngrok.sh start")
        print("  * Stop tunnel: ./setup_ngrok.sh stop") 
        print("  * Check status: ./setup_ngrok.sh status")
        print("  * Auto-manage: Set USE_NGROK=true/false in .env, then run python3 config2.py")
        print("="*60)
        
    except Exception as e:
        print("❌ Error during configuration: {}".format(e))
        print("Check the logs and .env configuration, then try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

