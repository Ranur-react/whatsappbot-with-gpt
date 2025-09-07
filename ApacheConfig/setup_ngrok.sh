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

# Cleanup function for complete ngrok removal
cleanup_ngrok() {
    echo_header "=== COMPLETE NGROK CLEANUP ==="
    
    # Stop any running ngrok processes
    stop_ngrok
    
    # Kill any remaining ngrok processes
    echo_info "Killing any remaining ngrok processes..."
    sudo pkill -f ngrok 2>/dev/null || true
    sudo killall ngrok 2>/dev/null || true
    
    # Remove ngrok binary and system files
    echo_info "Removing ngrok installation..."
    sudo apt remove --purge ngrok -y 2>/dev/null || true
    sudo rm -f /usr/local/bin/ngrok 2>/dev/null || true
    sudo rm -f /usr/bin/ngrok 2>/dev/null || true
    
    # Remove ngrok configuration
    echo_info "Removing ngrok configuration..."
    rm -rf ~/.ngrok2 2>/dev/null || true
    rm -rf ~/.config/ngrok 2>/dev/null || true
    rm -f ~/ngrok.yml 2>/dev/null || true
    
    # Remove ngrok repository and keys
    echo_info "Removing ngrok repository..."
    sudo rm -f /etc/apt/sources.list.d/ngrok.list 2>/dev/null || true
    sudo rm -f /etc/apt/trusted.gpg.d/ngrok.asc 2>/dev/null || true
    
    # Update apt cache
    echo_info "Updating package cache..."
    sudo apt update 2>/dev/null || true
    
    # Remove any ngrok related files in current directory
    echo_info "Removing local ngrok files..."
    rm -f ngrok.log 2>/dev/null || true
    rm -f nohup.out 2>/dev/null || true
    rm -f .ngrok_url 2>/dev/null || true
    rm -f .ngrok_pid 2>/dev/null || true
    
    # Clean up any ngrok systemd services (if any)
    sudo systemctl stop ngrok 2>/dev/null || true
    sudo systemctl disable ngrok 2>/dev/null || true
    sudo rm -f /etc/systemd/system/ngrok.service 2>/dev/null || true
    sudo systemctl daemon-reload 2>/dev/null || true
    
    echo_info "✅ Complete ngrok cleanup finished!"
    echo_warn "All ngrok files, processes, and configurations removed"
}

# Uninstall ngrok completely
uninstall_ngrok() {
    echo_header "=== UNINSTALLING NGROK ==="
    
    # Confirm uninstall
    read -p "Are you sure you want to completely remove ngrok? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warn "Uninstall cancelled"
        return 0
    fi
    
    cleanup_ngrok
    
    echo_info "🗑️  Ngrok has been completely uninstalled from the system"
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
        echo_info "Ngrok is already installed: $(ngrok version)"
        return 0
    fi
    
    echo_info "Installing ngrok..."
    
    # Install ngrok using official repository
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
        | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
        && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
        | sudo tee /etc/apt/sources.list.d/ngrok.list \
        && sudo apt update \
        && sudo apt install ngrok -y
    
    if command -v ngrok &> /dev/null; then
        echo_info "✅ Ngrok installed successfully: $(ngrok version)"
    else
        echo_error "❌ Ngrok installation failed"
        exit 1
    fi
}

# Configure ngrok
configure_ngrok() {
    echo_header "=== CONFIGURING NGROK ==="
    
    # Add authtoken - your actual token
    echo_info "Adding ngrok authtoken..."
    ngrok config add-authtoken 31P0rvQ8QZ707JvEFXkBV9noZIk_2bZK5JkQYGVmuEywj9MeC
    
    if [ $? -eq 0 ]; then
        echo_info "✅ Authtoken configured successfully"
    else
        echo_error "❌ Failed to configure authtoken"
        exit 1
    fi
        echo_warn "Then add NGROK_AUTHTOKEN=your_token_here to .env file"
        
        read -p "Enter your ngrok authtoken (or press Enter to skip): " token
    
    # Create ngrok configuration file for Docker container
    mkdir -p ~/.ngrok2
    cat > ~/.ngrok2/ngrok.yml << EOF
version: "2"
authtoken: 31P0rvQ8QZ707JvEFXkBV9noZIk_2bZK5JkQYGVmuEywj9MeC
region: ${NGROK_REGION:-ap}
console_ui: true
console_ui_color: transparent
tunnels:
  whatsapp-webhook:
    proto: http
    addr: "localhost:${DOCKER_INTERNAL_PORT:-3000}"
    host_header: rewrite
    bind_tls: true
    inspect: true
    metadata: "WhatsApp Webhook Service - TotalBP OWHUB"
    subdomain: "${NGROK_SUBDOMAIN:-totalbp-owhub-webhook}"
EOF
    
    echo_info "✅ Ngrok configuration created for Docker container port ${DOCKER_INTERNAL_PORT:-3000}"
}
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
    
    # Start ngrok in background - pointing to Docker container
    echo_info "Starting ngrok tunnel for Docker container on port ${DOCKER_INTERNAL_PORT:-3000}..."
    
    # Use simple command like provided: ngrok http http://localhost:3000
    nohup ngrok http http://localhost:${DOCKER_INTERNAL_PORT:-3000} --region=${NGROK_REGION:-ap} --subdomain=${NGROK_SUBDOMAIN:-totalbp-owhub-webhook} > /var/log/ngrok.log 2>&1 &
    
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
        install)
            install_ngrok
            ;;
        configure)
            load_env
            configure_ngrok
            ;;
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
        test)
            load_env
            echo_header "=== TESTING DOCKER & NGROK CONNECTIVITY ==="
            ./test_docker_ngrok.sh
            ;;
        guide)
            load_env
            show_setup_guide
            ;;
        install)
            install_ngrok
            ;;
        cleanup)
            cleanup_ngrok
            ;;
        uninstall)
            uninstall_ngrok
            ;;
        *)
            echo "WhatsApp Webhook Ngrok Manager"
            echo "Usage: $0 {install|configure|start|stop|restart|status|test|guide|cleanup|uninstall}"
            echo ""
            echo "Commands:"
            echo "  install   - Install ngrok from official repository"
            echo "  configure - Configure ngrok with authtoken"
            echo "  start     - Start ngrok tunnel for Docker container"
            echo "  stop      - Stop ngrok tunnel"
            echo "  restart   - Restart ngrok tunnel"
            echo "  status    - Show ngrok status and tunnel URLs"
            echo "  test      - Test Docker container and ngrok connectivity"
            echo "  cleanup   - Clean up all ngrok processes and temp files"
            echo "  uninstall - Completely remove ngrok from system"
            echo "  guide     - Show WhatsApp webhook setup guide"
            echo ""
            echo "Docker Configuration:"
            echo "  - Container: ${DOCKER_CONTAINER_NAME:-node1}"
            echo "  - Port: ${DOCKER_INTERNAL_PORT:-3000}"
            echo "  - Webhook: http://localhost:${DOCKER_INTERNAL_PORT:-3000}/webhook"
            echo ""
            echo "Network Configuration:"
            echo "  - SANDBOX (ens120): Internal development & testing"
            echo "  - INTERNET (ens192): Public access via ngrok tunnel"
            echo "  - Future: HAProxy for enterprise routing"
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
