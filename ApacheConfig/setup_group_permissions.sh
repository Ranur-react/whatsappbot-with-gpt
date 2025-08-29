#!/bin/bash

# ====================================
# WEBHOOK GROUP PERMISSION SETUP
# ====================================
# Script untuk membuat group khusus dan mengatur permission user

set -e

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
    echo -e "${BLUE}$1${NC}"
}

# Configuration
GROUP_NAME="webhook-owhub"
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

create_webhook_group() {
    echo_header "=== Creating Webhook Group ==="
    
    # Check if group already exists
    if getent group "$GROUP_NAME" > /dev/null 2>&1; then
        echo_info "Group '$GROUP_NAME' already exists"
    else
        echo_info "Creating group: $GROUP_NAME"
        sudo groupadd "$GROUP_NAME"
        echo_info "✅ Group '$GROUP_NAME' created successfully"
    fi
}

add_user_to_group() {
    local username=$1
    
    echo_info "Adding user '$username' to group '$GROUP_NAME'"
    
    # Check if user exists
    if ! id "$username" > /dev/null 2>&1; then
        echo_error "User '$username' does not exist"
        return 1
    fi
    
    # Add user to group
    sudo usermod -a -G "$GROUP_NAME" "$username"
    echo_info "✅ User '$username' added to group '$GROUP_NAME'"
    
    # Verify membership
    if groups "$username" | grep -q "$GROUP_NAME"; then
        echo_info "✅ Verified: '$username' is now member of '$GROUP_NAME'"
    else
        echo_error "Failed to add '$username' to group '$GROUP_NAME'"
        return 1
    fi
}

set_group_permissions() {
    echo_header "=== Setting Group Permissions ==="
    
    # Files and their permissions for group access
    declare -A file_permissions=(
        ["config2.py"]="750"          # Owner: rwx, Group: r-x, Others: ---
        ["setup_ngrok.sh"]="750"      # Owner: rwx, Group: r-x, Others: ---
        ["test_ngrok_cleanup.sh"]="750"
        ["quick_ngrok_cleanup.sh"]="750"
        ["set_permissions.sh"]="750"
        [".env"]="640"                # Owner: rw-, Group: r--, Others: ---
    )
    
    for file in "${!file_permissions[@]}"; do
        local filepath="$SCRIPT_DIR/$file"
        local perm="${file_permissions[$file]}"
        
        if [ -f "$filepath" ]; then
            # Set group ownership
            sudo chgrp "$GROUP_NAME" "$filepath"
            
            # Set permissions
            chmod "$perm" "$filepath"
            
            echo_info "✅ $file - Group: $GROUP_NAME, Permission: $perm"
        else
            echo_warn "⚠️  File not found: $file"
        fi
    done
}

remove_user_from_group() {
    local username=$1
    
    echo_info "Removing user '$username' from group '$GROUP_NAME'"
    
    # Check if user exists and is member of group
    if ! id "$username" > /dev/null 2>&1; then
        echo_error "User '$username' does not exist"
        return 1
    fi
    
    if ! groups "$username" | grep -q "$GROUP_NAME"; then
        echo_warn "User '$username' is not a member of group '$GROUP_NAME'"
        return 0
    fi
    
    # Remove user from group
    sudo gpasswd -d "$username" "$GROUP_NAME"
    echo_info "✅ User '$username' removed from group '$GROUP_NAME'"
}

list_group_members() {
    echo_header "=== Group Members ==="
    
    if getent group "$GROUP_NAME" > /dev/null 2>&1; then
        local members=$(getent group "$GROUP_NAME" | cut -d: -f4)
        
        if [ -n "$members" ]; then
            echo_info "Members of group '$GROUP_NAME':"
            echo "$members" | tr ',' '\n' | while read -r user; do
                [ -n "$user" ] && echo "  - $user"
            done
        else
            echo_warn "Group '$GROUP_NAME' has no members"
        fi
    else
        echo_error "Group '$GROUP_NAME' does not exist"
    fi
}

show_file_permissions() {
    echo_header "=== Current File Permissions ==="
    
    local files=("config2.py" "setup_ngrok.sh" "test_ngrok_cleanup.sh" "quick_ngrok_cleanup.sh" ".env")
    
    for file in "${files[@]}"; do
        local filepath="$SCRIPT_DIR/$file"
        if [ -f "$filepath" ]; then
            ls -la "$filepath"
        fi
    done
}

show_usage() {
    echo "Webhook Group Permission Manager"
    echo "Usage: $0 {create|add|remove|list|permissions|setup}"
    echo ""
    echo "Commands:"
    echo "  create                    - Create webhook group"
    echo "  add <username>           - Add user to webhook group"
    echo "  remove <username>        - Remove user from webhook group"  
    echo "  list                     - List group members"
    echo "  permissions              - Show current file permissions"
    echo "  setup <user1> [user2...] - Complete setup with users"
    echo ""
    echo "Examples:"
    echo "  $0 setup user1 user2     - Create group and add multiple users"
    echo "  $0 add newuser          - Add single user to existing group"
}

# Main script logic
case "${1:-}" in
    create)
        create_webhook_group
        set_group_permissions
        ;;
        
    add)
        if [ -z "$2" ]; then
            echo_error "Username required"
            show_usage
            exit 1
        fi
        create_webhook_group  # Ensure group exists
        add_user_to_group "$2"
        ;;
        
    remove)
        if [ -z "$2" ]; then
            echo_error "Username required"
            show_usage
            exit 1
        fi
        remove_user_from_group "$2"
        ;;
        
    list)
        list_group_members
        ;;
        
    permissions)
        show_file_permissions
        ;;
        
    setup)
        if [ $# -lt 2 ]; then
            echo_error "At least one username required"
            show_usage
            exit 1
        fi
        
        echo_header "=== Complete Webhook Group Setup ==="
        
        # Create group and set permissions
        create_webhook_group
        set_group_permissions
        
        # Add all specified users
        shift  # Remove 'setup' argument
        for username in "$@"; do
            add_user_to_group "$username"
        done
        
        echo ""
        list_group_members
        echo ""
        show_file_permissions
        
        echo ""
        echo_info "🎉 Group setup completed!"
        echo_info "Users need to log out and log back in for group changes to take effect"
        ;;
        
    *)
        show_usage
        exit 1
        ;;
esac
