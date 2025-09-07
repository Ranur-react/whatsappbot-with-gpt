#!/bin/bash

# ====================================
# NGROK CLEANUP VERIFICATION TEST
# ====================================
# Script untuk memverifikasi bahwa ngrok benar-benar bersih setelah USE_NGROK=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

echo_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

echo_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

echo "======================================"
echo "NGROK CLEANUP VERIFICATION TEST"
echo "======================================"

TOTAL_TESTS=0
PASSED_TESTS=0

# Test 1: Check for running ngrok processes
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for running ngrok processes..."
if pgrep -f ngrok > /dev/null; then
    echo_fail "Ngrok processes are still running"
    ps aux | grep ngrok | grep -v grep
else
    echo_pass "No ngrok processes found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 2: Check for ngrok binary
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for ngrok binary installation..."
if command -v ngrok &> /dev/null; then
    echo_fail "Ngrok binary still exists at: $(which ngrok)"
else
    echo_pass "Ngrok binary not found (uninstalled)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 3: Check for ngrok configuration files
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for ngrok configuration files..."
CONFIG_FOUND=false

if [ -d ~/.ngrok2 ]; then
    echo_fail "Ngrok config directory ~/.ngrok2 still exists"
    CONFIG_FOUND=true
fi

if [ -d ~/.config/ngrok ]; then
    echo_fail "Ngrok config directory ~/.config/ngrok still exists"
    CONFIG_FOUND=true
fi

if [ -f ~/ngrok.yml ]; then
    echo_fail "Ngrok config file ~/ngrok.yml still exists"
    CONFIG_FOUND=true
fi

if [ "$CONFIG_FOUND" = false ]; then
    echo_pass "No ngrok configuration files found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 4: Check for ngrok repository files
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for ngrok repository configuration..."
REPO_FOUND=false

if [ -f /etc/apt/sources.list.d/ngrok.list ]; then
    echo_fail "Ngrok repository file still exists"
    REPO_FOUND=true
fi

if [ -f /etc/apt/trusted.gpg.d/ngrok.asc ]; then
    echo_fail "Ngrok GPG key still exists"
    REPO_FOUND=true
fi

if [ "$REPO_FOUND" = false ]; then
    echo_pass "No ngrok repository files found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 5: Check for local ngrok files
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for local ngrok files..."
LOCAL_FOUND=false

for file in ngrok.log nohup.out .ngrok_url .ngrok_pid; do
    if [ -f "$file" ]; then
        echo_fail "Local file $file still exists"
        LOCAL_FOUND=true
    fi
done

if [ "$LOCAL_FOUND" = false ]; then
    echo_pass "No local ngrok files found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 6: Check for ngrok systemd services
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for ngrok systemd services..."
if [ -f /etc/systemd/system/ngrok.service ]; then
    echo_fail "Ngrok systemd service file still exists"
else
    echo_pass "No ngrok systemd service found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 7: Check network connections on ngrok ports
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Checking for ngrok network connections..."
if netstat -tlnp 2>/dev/null | grep -E ':4040|:8080' | grep -q ngrok; then
    echo_fail "Ngrok network connections still active"
    netstat -tlnp | grep ngrok
else
    echo_pass "No ngrok network connections found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 8: Verify Docker container accessibility (should work without ngrok)
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo_test "Testing Docker container accessibility..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ | grep -q "200\|404"; then
    echo_pass "Docker container accessible on localhost:3000"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo_fail "Docker container not accessible"
fi

echo ""
echo "======================================"
echo "CLEANUP TEST RESULTS"
echo "======================================"
echo "Tests Passed: $PASSED_TESTS/$TOTAL_TESTS"

if [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
    echo_pass "🎉 ALL TESTS PASSED - Ngrok completely cleaned up!"
    echo_pass "System is clean and ready for production HAProxy deployment"
    exit 0
else
    FAILED_TESTS=$((TOTAL_TESTS - PASSED_TESTS))
    echo_fail "❌ $FAILED_TESTS tests failed - Cleanup incomplete"
    echo_fail "Please run manual cleanup or check remaining files"
    exit 1
fi
