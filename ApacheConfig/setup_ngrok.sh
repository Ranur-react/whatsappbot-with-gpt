#!/bin/bash

# ====================================
# NGROK SETUP SCRIPT FOR WHATSAPP WEBHOOK
# ====================================
# Script untuk setup ngrok tunnel agar webhook bisa diakses Facebook
# dari internet sebelum HAProxy enterprise dipasang

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_header() {
    echo -e "${BLUE}$1${NC}"
}


# Load environment variables
load_env() {
    if [ -f .env ]; then
        export $(grep -v '^#' .env | grep -v '^$' | xargs)
        echo_info "Environment variables loaded from .env"
    else
        echo_error ".env file not found!"
        exit 1
    fi
}

# Install ngrok if not installed
install_ngrok() {
    echo_header "=== INSTALLING NGROK ==="
    
    if command -v ngrok &> /dev/null; then
        echo_info "ngrok is already installed"
        ngrok version
        return 0
    fi
    
    echo_info "Installing ngrok..."
    
    # Download ngrok
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -O /tmp/ngrok.tgz
    
    # Extract and install
    sudo tar -xzf /tmp/ngrok.tgz -C /usr/local/bin/
    sudo chmod +x /usr/local/bin/ngrok
    
    # Cleanup
    rm /tmp/ngrok.tgz
    
    echo_info "ngrok installed successfully"
    ngrok version
}

# Configure ngrok
configure_ngrok() {
    echo_header "=== CONFIGURING NGROK ==="
    
    # Check if authtoken is provided
    if [ -z "$NGROK_AUTHTOKEN" ]; then
        echo_warn "NGROK_AUTHTOKEN not found in .env"
        echo_warn "Please get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken"
        echo_warn "Then add NGROK_AUTHTOKEN=your_token_here to .env file"
        
        read -p "Enter your ngrok authtoken (or press Enter to skip): " token
        if [ ! -z "$token" ]; then
            echo "" >> .env
            echo "# Ngrok Configuration" >> .env
            echo "NGROK_AUTHTOKEN=$token" >> .env
            export NGROK_AUTHTOKEN=$token
        else
            echo_warn "Skipping ngrok authentication setup"
            return 1
        fi
    fi
    
    # Authenticate ngrok
    ngrok config add-authtoken $NGROK_AUTHTOKEN
    echo_info "ngrok authenticated successfully"
    
    # Create ngrok configuration file
    mkdir -p ~/.ngrok2
    cat > ~/.ngrok2/ngrok.yml << EOF
version: "2"
authtoken: ${NGROK_AUTHTOKEN}
region: ${NGROK_REGION:-ap}
console_ui: true
console_ui_color: transparent
tunnels:
  whatsapp-webhook:
    proto: https
    addr: "botdev-owhub.totalbp.com:443"
    host_header: "botdev-owhub.totalbp.com"
    bind_tls: true
    inspect: true
    metadata: "WhatsApp Webhook Service - TotalBP"
EOF
    
    echo_info "ngrok configuration created"
}

# Start ngrok tunnel
start_ngrok() {
    echo_header "=== STARTING NGROK TUNNEL ==="
    
    # Check if ngrok is already running
    if pgrep -f "ngrok" > /dev/null; then
        echo_warn "ngrok is already running"
        echo_info "Current tunnels:"
        curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | .public_url' 2>/dev/null || echo "Unable to get tunnel info"
        return 0
    fi
    
    # Start ngrok in background
    echo_info "Starting ngrok tunnel..."
    nohup ngrok start whatsapp-webhook > /var/log/ngrok.log 2>&1 &
    
    # Wait for ngrok to start
    echo_info "Waiting for ngrok to establish tunnel..."
    sleep 5
    
    # Get tunnel URL
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | jq -r '.tunnels[] | select(.proto=="https") | .public_url' 2>/dev/null)
        
        if [ ! -z "$TUNNEL_URL" ] && [ "$TUNNEL_URL" != "null" ]; then
            echo_info "✅ ngrok tunnel established successfully!"
            echo_info "Public URL: $TUNNEL_URL"
            echo_info "Webhook URL: $TUNNEL_URL/webhook"
            
            # Save tunnel URL to file for reference
            echo "$TUNNEL_URL" > /tmp/ngrok_tunnel_url.txt
            echo "$TUNNEL_URL/webhook" > /tmp/ngrok_webhook_url.txt
            
            return 0
        fi
        
        echo_warn "Attempt $attempt/$max_attempts: Waiting for tunnel..."
        sleep 2
        ((attempt++))
    done
    
    echo_error "Failed to establish ngrok tunnel"
    echo_error "Check ngrok logs: tail -f /var/log/ngrok.log"
    return 1
}

# Stop ngrok
stop_ngrok() {
    echo_header "=== STOPPING NGROK TUNNEL ==="
    
    if pgrep -f "ngrok" > /dev/null; then
        pkill -f "ngrok"
        echo_info "ngrok tunnel stopped"
        
        # Clean up temp files
        rm -f /tmp/ngrok_tunnel_url.txt /tmp/ngrok_webhook_url.txt
    else
        echo_warn "ngrok is not running"
    fi
}

# Show ngrok status
status_ngrok() {
    echo_header "=== NGROK STATUS ==="
    
    if pgrep -f "ngrok" > /dev/null; then
        echo_info "✅ ngrok is running"
        
        # Get tunnel info
        TUNNEL_INFO=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo_info "Active tunnels:"
            echo "$TUNNEL_INFO" | jq -r '.tunnels[] | "  - \(.proto)://\(.config.addr) -> \(.public_url)"' 2>/dev/null || echo "  Unable to parse tunnel info"
            
            WEBHOOK_URL=$(echo "$TUNNEL_INFO" | jq -r '.tunnels[] | select(.proto=="https") | .public_url' 2>/dev/null)
            if [ ! -z "$WEBHOOK_URL" ] && [ "$WEBHOOK_URL" != "null" ]; then
                echo_info "📱 WhatsApp Webhook URL: $WEBHOOK_URL/webhook"
            fi
        else
            echo_warn "Unable to get tunnel information"
        fi
        
        echo_info "🌐 ngrok web interface: http://localhost:4040"
    else
        echo_warn "❌ ngrok is not running"
    fi
    
    echo_info "Network interfaces:"
    echo_info "  - SANDBOX (ens120): ${SERVER_IP_SANDBOX:-10.100.129.51}"
    echo_info "  - INTERNET (ens192): ${SERVER_IP_INTERNET:-10.100.120.51}"
}

# Show setup guide
show_setup_guide() {
    echo_header "=== WHATSAPP WEBHOOK SETUP GUIDE ==="
    echo ""
    echo_info "Current Network Configuration:"
    echo_info "  - Internal Domain: botdev-owhub.totalbp.com"
    echo_info "  - SANDBOX IP (ens120): ${SERVER_IP_SANDBOX:-10.100.129.51}"
    echo_info "  - INTERNET IP (ens192): ${SERVER_IP_INTERNET:-10.100.120.51}"
    echo ""
    
    if [ -f /tmp/ngrok_webhook_url.txt ]; then
        WEBHOOK_URL=$(cat /tmp/ngrok_webhook_url.txt)
        echo_info "🌍 PUBLIC WEBHOOK URL (for Facebook):"
        echo_info "  $WEBHOOK_URL"
        echo ""
        echo_info "📝 Facebook Developer Configuration:"
        echo_info "  1. Go to https://developers.facebook.com"
        echo_info "  2. Select your WhatsApp Business app"
        echo_info "  3. Go to WhatsApp > Configuration"
        echo_info "  4. Set Webhook URL: $WEBHOOK_URL"
        echo_info "  5. Set Verify Token: (as configured in your Node.js app)"
        echo_info "  6. Subscribe to webhook events"
    else
        echo_warn "No active ngrok tunnel found"
        echo_info "Run: $0 start"
    fi
    
    echo ""
    echo_info "🔧 Management Commands:"
    echo_info "  $0 start    - Start ngrok tunnel"
    echo_info "  $0 stop     - Stop ngrok tunnel"
    echo_info "  $0 status   - Show current status"
    echo_info "  $0 restart  - Restart ngrok tunnel"
    echo_info "  $0 guide    - Show this setup guide"
    echo ""
    echo_warn "⚠️  IMPORTANT NOTES:"
    echo_warn "  - ngrok tunnel is temporary for development/testing"
    echo_warn "  - For production, use HAProxy with proper domain routing"
    echo_warn "  - Keep ngrok running while testing Facebook webhook"
    echo_warn "  - Monitor ngrok logs: tail -f /var/log/ngrok.log"
}

# Main script logic
main() {
    case "$1" in
        start)
            load_env
            install_ngrok
            configure_ngrok
            start_ngrok
            echo ""
            show_setup_guide
            ;;
        stop)
            stop_ngrok
            ;;
        restart)
            load_env
            stop_ngrok
            sleep 2
            start_ngrok
            echo ""
            show_setup_guide
            ;;
        status)
            load_env
            status_ngrok
            ;;
        guide)
            load_env
            show_setup_guide
            ;;
        install)
            install_ngrok
            ;;
        *)
            echo "WhatsApp Webhook Ngrok Manager"
            echo "Usage: $0 {start|stop|restart|status|guide|install}"
            echo ""
            echo "Commands:"
            echo "  start    - Install and start ngrok tunnel"
            echo "  stop     - Stop ngrok tunnel"
            echo "  restart  - Restart ngrok tunnel"
            echo "  status   - Show ngrok status and tunnel URLs"
            echo "  guide    - Show WhatsApp webhook setup guide"
            echo "  install  - Install ngrok only"
            echo ""
            echo "Network Configuration:"
            echo "  - SANDBOX (ens120): Local development"
            echo "  - INTERNET (ens192): Public access (via ngrok)"
            echo "  - HAProxy: Will be configured later for production"
            exit 1
            ;;
    esac
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo_warn "Running as root. Some ngrok operations may need user permissions."
fi

# Run main function
main "$@"
