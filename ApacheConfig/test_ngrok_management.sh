#!/bin/bash

# =================================================================
# NGROK MANAGEMENT TEST SCRIPT
# =================================================================
# Script untuk testing otomatis manajemen ngrok dengan USE_NGROK flag
# 
# Usage: ./test_ngrok_management.sh
# 
# Author: WhatsApp Webhook Team
# Version: 1.0
# =================================================================

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    echo "❌ .env file not found!"
    exit 1
fi
 
echo "==============================================="
echo "🧪 TESTING NGROK MANAGEMENT AUTOMATION"
echo "==============================================="
echo "Current USE_NGROK setting: $USE_NGROK"
echo ""

# Function to check ngrok status
check_ngrok_processes() {
    local active_count=$(pgrep -f "ngrok" | wc -l)
    echo "Active ngrok processes: $active_count"
    
    if [ $active_count -gt 0 ]; then
        echo "📊 Running ngrok processes:"
        pgrep -f "ngrok" | while read pid; do
            echo "  - PID: $pid ($(ps -p $pid -o comm=))"
        done
    else
        echo "✅ No ngrok processes found"
    fi
    return $active_count
}

# Function to test configuration change
test_config_change() {
    local new_setting=$1
    echo ""
    echo "🔄 Testing USE_NGROK=$new_setting"
    echo "---------------------------------------"
    
    # Update .env file
    sed -i "s/USE_NGROK=.*/USE_NGROK=$new_setting/" .env
    echo "✓ Updated .env: USE_NGROK=$new_setting"
    
    # Run config script
    echo "🚀 Running python3 config2.py..."
    python3 config2.py 2>&1 | grep -E "(Ngrok|NGROK|tunnel|stopped|started)" | head -10
    
    # Wait a bit for processes to settle
    sleep 3
    
    # Check result
    echo ""
    echo "📋 Result after configuration change:"
    check_ngrok_processes
    local result_processes=$?
    
    if [ "$new_setting" = "true" ] && [ $result_processes -gt 0 ]; then
        echo "✅ SUCCESS: Ngrok is running (expected for USE_NGROK=true)"
        return 0
    elif [ "$new_setting" = "false" ] && [ $result_processes -eq 0 ]; then
        echo "✅ SUCCESS: Ngrok is stopped (expected for USE_NGROK=false)"
        return 0
    else
        echo "❌ FAILED: Unexpected ngrok state"
        return 1
    fi
}

# Main test sequence
main_test() {
    echo "🏁 Starting automated ngrok management test..."
    echo ""
    
    # Initial state
    echo "📊 Initial state:"
    check_ngrok_processes
    
    # Test 1: Enable ngrok
    if ! test_config_change "true"; then
        echo "❌ Test 1 FAILED: Could not start ngrok"
        return 1
    fi
    
    echo ""
    echo "⏳ Waiting 5 seconds between tests..."
    sleep 5
    
    # Test 2: Disable ngrok  
    if ! test_config_change "false"; then
        echo "❌ Test 2 FAILED: Could not stop ngrok"
        return 1
    fi
    
    echo ""
    echo "⏳ Final verification in 3 seconds..."
    sleep 3
    
    # Final verification
    echo ""
    echo "🔍 Final verification:"
    check_ngrok_processes
    local final_count=$?
    
    if [ $final_count -eq 0 ]; then
        echo ""
        echo "🎉 ALL TESTS PASSED!"
        echo "✅ Ngrok management automation is working correctly"
        echo "✅ USE_NGROK=false successfully stops all ngrok processes"
        return 0
    else
        echo ""
        echo "❌ FINAL TEST FAILED!"
        echo "❌ Some ngrok processes are still running"
        echo "⚠️  Manual cleanup may be required: pkill -f ngrok"
        return 1
    fi
}

# Execute tests
echo "🔧 Making setup_ngrok.sh executable..."
chmod +x setup_ngrok.sh

# Backup current .env setting
ORIGINAL_SETTING=$USE_NGROK
echo "💾 Backing up original USE_NGROK setting: $ORIGINAL_SETTING"

# Run tests
if main_test; then
    echo ""
    echo "==============================================="
    echo "✅ TEST SUITE COMPLETED SUCCESSFULLY"
    echo "==============================================="
    EXIT_CODE=0
else
    echo ""
    echo "==============================================="
    echo "❌ TEST SUITE FAILED"
    echo "==============================================="
    echo "Manual troubleshooting steps:"
    echo "1. Check ngrok processes: pgrep -f ngrok"
    echo "2. Kill manually: pkill -f ngrok"
    echo "3. Verify setup_ngrok.sh: ./setup_ngrok.sh status"
    EXIT_CODE=1
fi

# Restore original setting
echo ""
echo "🔄 Restoring original USE_NGROK setting..."
sed -i "s/USE_NGROK=.*/USE_NGROK=$ORIGINAL_SETTING/" .env
echo "✅ Restored: USE_NGROK=$ORIGINAL_SETTING"

echo ""
echo "📋 Test Summary:"
echo "- Original setting: $ORIGINAL_SETTING"
echo "- Test results: $([ $EXIT_CODE -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
echo "- Configuration restored: ✅"

exit $EXIT_CODE
