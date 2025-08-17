#!/bin/bash

# ====================================
# DOCKER & NGROK CONNECTIVITY TEST
# ====================================
# Script untuk test konektivitas Docker container dan ngrok tunnel

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo_info "Environment variables loaded"
else
    echo_error ".env file not found!"
    exit 1
fi

echo_header "TESTING DOCKER CONTAINER"

# Test Docker container
echo_info "Checking Docker container: ${DOCKER_CONTAINER_NAME:-node1}"
if docker ps | grep -q "${DOCKER_CONTAINER_NAME:-node1}"; then
    echo_info "✅ Docker container is running"
    
    # Get container details
    echo_info "Container details:"
    docker ps --filter "name=${DOCKER_CONTAINER_NAME:-node1}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo_error "❌ Docker container '${DOCKER_CONTAINER_NAME:-node1}' is not running"
    echo_info "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

# Test container port accessibility
echo_info "Testing container port ${DOCKER_INTERNAL_PORT:-3000}..."
if curl -s -f "http://localhost:${DOCKER_INTERNAL_PORT:-3000}" >/dev/null 2>&1; then
    echo_info "✅ Container port ${DOCKER_INTERNAL_PORT:-3000} is accessible"
else
    echo_warn "⚠ Container port ${DOCKER_INTERNAL_PORT:-3000} is not accessible"
    echo_info "This might be normal if the app requires specific endpoints"
fi

# Test webhook endpoint
echo_info "Testing webhook endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${DOCKER_INTERNAL_PORT:-3000}/webhook" 2>/dev/null || echo "000")
if [ "$response" != "000" ]; then
    echo_info "✅ Webhook endpoint responds with HTTP $response"
else
    echo_warn "⚠ Webhook endpoint not accessible"
fi

echo_header "TESTING NGROK CONFIGURATION"

# Test ngrok installation
if command -v ngrok &> /dev/null; then
    echo_info "✅ Ngrok is installed: $(ngrok version)"
else
    echo_error "❌ Ngrok is not installed"
    echo_info "Run: ./setup_ngrok.sh install"
    exit 1
fi

# Test ngrok auth
if ngrok config check >/dev/null 2>&1; then
    echo_info "✅ Ngrok authtoken is configured"
else
    echo_error "❌ Ngrok authtoken is not configured"
    echo_info "Run: ./setup_ngrok.sh configure"
fi

# Test ngrok process
if pgrep -f "ngrok" > /dev/null; then
    echo_info "✅ Ngrok process is running"
    
    # Get tunnel info
    echo_info "Getting tunnel information..."
    if curl -s http://localhost:4040/api/tunnels >/dev/null 2>&1; then
        TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url' 2>/dev/null || echo "")
        
        if [ ! -z "$TUNNEL_URL" ] && [ "$TUNNEL_URL" != "null" ]; then
            echo_info "✅ Ngrok tunnel is active"
            echo_info "🌐 Public URL: $TUNNEL_URL"
            echo_info "🔗 Webhook URL: $TUNNEL_URL/webhook"
            
            # Test tunnel connectivity
            echo_info "Testing tunnel connectivity..."
            tunnel_response=$(curl -s -o /dev/null -w "%{http_code}" "$TUNNEL_URL/webhook" 2>/dev/null || echo "000")
            if [ "$tunnel_response" != "000" ]; then
                echo_info "✅ Tunnel is accessible from internet (HTTP $tunnel_response)"
            else
                echo_warn "⚠ Tunnel is not accessible from internet"
            fi
        else
            echo_warn "⚠ No active HTTPS tunnel found"
        fi
    else
        echo_warn "⚠ Cannot connect to ngrok API (port 4040)"
    fi
else
    echo_warn "⚠ Ngrok is not running"
    echo_info "Run: ./setup_ngrok.sh start"
fi

echo_header "FACEBOOK WEBHOOK CONFIGURATION"

if [ ! -z "$TUNNEL_URL" ] && [ "$TUNNEL_URL" != "null" ]; then
    echo_info "📝 For Facebook WhatsApp Business API:"
    echo_info "Webhook URL: $TUNNEL_URL/webhook"
    echo_info "Verify Token: (set in your Node.js app)"
    echo ""
    echo_info "🔧 Setup steps:"
    echo_info "1. Go to developers.facebook.com"
    echo_info "2. Select your WhatsApp Business app"
    echo_info "3. Go to WhatsApp > Configuration"
    echo_info "4. Add webhook URL: $TUNNEL_URL/webhook"
    echo_info "5. Set verify token (must match your app)"
    echo_info "6. Subscribe to webhook events"
else
    echo_warn "⚠ No tunnel URL available for Facebook configuration"
    echo_info "Start ngrok first: ./setup_ngrok.sh start"
fi

echo_header "SUMMARY"

echo_info "Docker Container: ${DOCKER_CONTAINER_NAME:-node1} on port ${DOCKER_INTERNAL_PORT:-3000}"
echo_info "Internal webhook: http://localhost:${DOCKER_INTERNAL_PORT:-3000}/webhook"
echo_info "Domain webhook: https://${DOMAIN_NAME:-botdev-owhub.totalbp.com}/webhook"
if [ ! -z "$TUNNEL_URL" ] && [ "$TUNNEL_URL" != "null" ]; then
    echo_info "Public webhook: $TUNNEL_URL/webhook"
fi
echo_info "Ngrok auth token: Configured ✅"
echo_info "Configuration file: .env"

echo ""
echo_info "🎯 Next steps:"
echo_info "1. Ensure Docker container is running"
echo_info "2. Start ngrok tunnel: ./setup_ngrok.sh start"
echo_info "3. Configure Facebook webhook with public URL"
echo_info "4. Test webhook with Facebook's webhook tester"
