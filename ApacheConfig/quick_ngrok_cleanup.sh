#!/bin/bash

# ====================================
# QUICK NGROK CLEANUP COMMAND
# ====================================
# Script cepat untuk cleanup ngrok manual tanpa mengubah .env

echo "🗑️  QUICK NGROK CLEANUP"
echo "========================"

# Load setup_ngrok.sh functions
if [ -f "./setup_ngrok.sh" ]; then
    echo "Running complete ngrok cleanup..."
    chmod +x setup_ngrok.sh
    ./setup_ngrok.sh cleanup
    
    echo ""
    echo "Running cleanup verification..."
    chmod +x test_ngrok_cleanup.sh
    ./test_ngrok_cleanup.sh
    
    echo ""
    echo "✅ Quick cleanup completed!"
    echo "Ngrok has been removed from the system"
else
    echo "❌ setup_ngrok.sh not found!"
    echo "Please run this script from the ApacheConfig directory"
fi
