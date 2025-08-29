# ====================================
# FILE PERMISSION COMMANDS REFERENCE
# ====================================

# 1. BASIC PERMISSION SETUP
# ==========================

# Make executable for owner only
chmod 700 config2.py
chmod 700 setup_ngrok.sh

# Make executable for owner + group
chmod 750 config2.py
chmod 750 setup_ngrok.sh

# Secure .env file (readable by owner only)
chmod 600 .env

# 2. USER-SPECIFIC PERMISSIONS
# =============================

# Change ownership to specific user
sudo chown username:username config2.py
sudo chown username:username setup_ngrok.sh
sudo chown username:username .env

# Set executable for specific user only
sudo chown myuser:myuser script.sh
chmod 700 script.sh

# 3. GROUP-SPECIFIC PERMISSIONS
# ==============================

# Create a specific group for webhook scripts
sudo groupadd webhook-users

# Add users to the group
sudo usermod -a -G webhook-users user1
sudo usermod -a -G webhook-users user2

# Set group ownership
sudo chgrp webhook-users config2.py
sudo chgrp webhook-users setup_ngrok.sh

# Set permissions for group access
chmod 750 config2.py  # Owner: rwx, Group: r-x, Others: ---
chmod 640 .env        # Owner: rw-, Group: r--, Others: ---

# 4. ADVANCED PERMISSION CONTROL
# ===============================

# Use ACL (Access Control Lists) for fine-grained control
# Install ACL tools: sudo apt install acl

# Give specific user execute permission
setfacl -m u:username:rx config2.py

# Give specific group execute permission
setfacl -m g:groupname:rx setup_ngrok.sh

# View ACL permissions
getfacl config2.py

# 5. SUDO-BASED EXECUTION CONTROL
# ================================

# Create sudoers entry for specific script execution
# sudo visudo
# Add line: username ALL=(ALL) NOPASSWD: /path/to/config2.py

# 6. PERMISSION VERIFICATION
# ==========================

# Check current permissions
ls -la config2.py setup_ngrok.sh .env

# Check file ownership
stat config2.py

# Check which users can access
namei -l /path/to/config2.py

# 7. SECURITY BEST PRACTICES
# ===========================

# Production recommendations:
chmod 700 config2.py      # Critical scripts - owner only
chmod 600 .env           # Config files - owner read/write only
chmod 750 setup_ngrok.sh  # Utility scripts - owner + group
chmod 644 README.md       # Documentation - readable by all

# Development recommendations:
chmod 755 config2.py      # Scripts - executable by all (dev only)
chmod 644 .env           # Config - readable by group (dev only)

# Emergency access removal:
chmod 000 script.sh       # Remove all permissions
chmod 600 script.sh       # Restore owner read/write only
