#!/bin/bash

# ====================================
# FILE PERMISSION SETUP SCRIPT
# ====================================
# Script untuk mengatur permission file agar hanya user tertentu yang bisa eksekusi

echo "🔐 Setting up file permissions for WhatsApp webhook scripts"
echo "=========================================================="

# Get current user
CURRENT_USER=$(whoami)
echo "Current user: $CURRENT_USER"

# List of script files to secure
SCRIPT_FILES=(
    "config2.py"
    "setup_ngrok.sh"
    "test_ngrok_cleanup.sh"
    "quick_ngrok_cleanup.sh"
    "test_ngrok_management.sh"
)

# Function to set permissions for owner only
set_owner_only_permissions() {
    local file=$1
    if [ -f "$file" ]; then
        # Set permissions: owner can read/write/execute, others cannot
        chmod 700 "$file"
        echo "✅ $file - executable by owner ($CURRENT_USER) only"
    else
        echo "⚠️  $file - file not found"
    fi
}

# Function to set permissions for specific user
set_user_permissions() {
    local file=$1
    local username=$2
    
    if [ -f "$file" ]; then
        # Change ownership to specific user
        sudo chown "$username:$username" "$file"
        # Set permissions: owner only
        chmod 700 "$file"
        echo "✅ $file - executable by $username only"
    else
        echo "⚠️  $file - file not found"
    fi
}

# Function to set permissions for specific group
set_group_permissions() {
    local file=$1
    local groupname=$2
    
    if [ -f "$file" ]; then
        # Change group ownership
        sudo chgrp "$groupname" "$file"
        # Set permissions: owner and group can execute
        chmod 750 "$file"
        echo "✅ $file - executable by group $groupname"
    else
        echo "⚠️  $file - file not found"
    fi
}

echo ""
echo "Choose permission setup:"
echo "1. Current user only ($CURRENT_USER)"
echo "2. Specific user only"
echo "3. Specific group"
echo "4. Custom setup"
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Setting permissions for current user only..."
        for file in "${SCRIPT_FILES[@]}"; do
            set_owner_only_permissions "$file"
        done
        
        # Secure .env file (read/write for owner only, no execute)
        if [ -f ".env" ]; then
            chmod 600 ".env"
            echo "✅ .env - readable by owner ($CURRENT_USER) only"
        fi
        ;;
        
    2)
        read -p "Enter username: " target_user
        if id "$target_user" &>/dev/null; then
            echo "Setting permissions for user: $target_user"
            for file in "${SCRIPT_FILES[@]}"; do
                set_user_permissions "$file" "$target_user"
            done
            
            # Secure .env file for specific user
            if [ -f ".env" ]; then
                sudo chown "$target_user:$target_user" ".env"
                chmod 600 ".env"
                echo "✅ .env - readable by $target_user only"
            fi
        else
            echo "❌ User $target_user does not exist"
            exit 1
        fi
        ;;
        
    3)
        read -p "Enter group name: " target_group
        if getent group "$target_group" &>/dev/null; then
            echo "Setting permissions for group: $target_group"
            for file in "${SCRIPT_FILES[@]}"; do
                set_group_permissions "$file" "$target_group"
            done
            
            # Secure .env file for specific group
            if [ -f ".env" ]; then
                sudo chgrp "$target_group" ".env"
                chmod 640 ".env"
                echo "✅ .env - readable by group $target_group"
            fi
        else
            echo "❌ Group $target_group does not exist"
            exit 1
        fi
        ;;
        
    4)
        echo "Custom permission setup:"
        echo "Available files:"
        for i in "${!SCRIPT_FILES[@]}"; do
            echo "  $((i+1)). ${SCRIPT_FILES[i]}"
        done
        
        read -p "Enter file number: " file_num
        if [ $file_num -gt 0 ] && [ $file_num -le ${#SCRIPT_FILES[@]} ]; then
            selected_file="${SCRIPT_FILES[$((file_num-1))]}"
            
            echo "Permission options for $selected_file:"
            echo "700 - Owner: rwx, Group: ---, Others: ---"
            echo "750 - Owner: rwx, Group: r-x, Others: ---"
            echo "755 - Owner: rwx, Group: r-x, Others: r-x"
            read -p "Enter permission (e.g., 700): " perm
            
            if [ -f "$selected_file" ]; then
                chmod "$perm" "$selected_file"
                echo "✅ $selected_file - permission set to $perm"
            fi
        else
            echo "❌ Invalid file number"
        fi
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📋 Current file permissions:"
ls -la config2.py setup_ngrok.sh .env 2>/dev/null || echo "Some files may not exist yet"

echo ""
echo "🔒 Security recommendations:"
echo "- .env file should be 600 (owner read/write only)"
echo "- Script files should be 700 (owner execute only) for production"
echo "- Use 750 if you need group access for team members"
echo "- Never use 755 for sensitive scripts in production"

echo ""
echo "✅ Permission setup completed!"
