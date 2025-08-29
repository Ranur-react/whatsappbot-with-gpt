# WhatsApp Webhook File Permission Management

## 🔐 File Permission Setup untuk User Tertentu

### **Quick Commands**
```bash
# Set executable untuk owner saja
chmod 700 config2.py
chmod 700 setup_ngrok.sh
chmod 600 .env

# Set executable untuk owner + group
chmod 750 config2.py  
chmod 640 .env

# Change ownership ke user specific
sudo chown username:username config2.py
sudo chown username:username .env
```

### **1. Automatic Security Setup**
Script otomatis mengatur permission yang aman:
```bash
python3 config2.py  # Otomatis set secure permissions
```

### **2. Manual Permission Setup**
```bash
chmod +x set_permissions.sh
./set_permissions.sh
```

### **3. Group-based Permission Management**
```bash
# Setup group untuk multiple users
chmod +x setup_group_permissions.sh
./setup_group_permissions.sh setup user1 user2 user3

# Add single user ke group
./setup_group_permissions.sh add newuser

# List group members
./setup_group_permissions.sh list
```

## 🛡️ Permission Levels

| File | Owner | Group | Others | Purpose |
|------|--------|--------|---------|---------|
| `.env` | `rw-` | `r--` | `---` | Config file - sensitive data |
| `config2.py` | `rwx` | `r-x` | `---` | Main script - critical execution |
| `setup_ngrok.sh` | `rwx` | `r-x` | `---` | Utility script - group access |
| `*.sh` scripts | `rwx` | `r-x` | `---` | Helper scripts - group access |

## 🎯 Use Cases

### **Single User (Production)**
```bash
chmod 700 config2.py      # Owner only
chmod 600 .env           # Owner only
```

### **Team Access (Development)**
```bash
./setup_group_permissions.sh setup dev1 dev2 admin1
```

### **Emergency Access Removal**
```bash
chmod 000 config2.py     # Remove all access
```

### **Restore Default Permissions**
```bash
./set_permissions.sh     # Interactive restoration
```

## 🔍 Permission Verification

### **Check Current Permissions**
```bash
ls -la config2.py setup_ngrok.sh .env
stat config2.py
```

### **Verify Group Membership**
```bash
groups username
./setup_group_permissions.sh list
```

### **Test File Access**
```bash
# Test as different user
sudo -u username ./config2.py
```

## 🚨 Security Best Practices

1. **Production Environment**:
   - Use `700` for critical scripts (owner only)
   - Use `600` for config files (owner read/write only)
   - Never use `755` for sensitive scripts

2. **Development Environment**:
   - Use `750` for scripts (owner + group)
   - Use `640` for config files (owner + group read)
   - Create dedicated group for team access

3. **Emergency Protocols**:
   - Remove all permissions: `chmod 000 file`
   - Emergency owner-only: `chmod 600 file`
   - Quick permission check: `ls -la`

## ⚙️ Advanced Permission Control

### **ACL (Access Control Lists)**
```bash
# Install ACL tools
sudo apt install acl

# Give specific user execute permission
setfacl -m u:username:rx config2.py

# Give specific group execute permission  
setfacl -m g:groupname:rx setup_ngrok.sh

# View ACL permissions
getfacl config2.py
```

### **Sudo-based Execution**
```bash
# Allow specific user to run script as root
sudo visudo
# Add: username ALL=(ALL) NOPASSWD: /path/to/config2.py
```

## 📁 File Structure with Permissions
```
ApacheConfig/
├── config2.py                    (700) - Main configuration script
├── setup_ngrok.sh                (750) - Ngrok management  
├── test_ngrok_cleanup.sh         (750) - Cleanup verification
├── quick_ngrok_cleanup.sh        (750) - Quick cleanup
├── set_permissions.sh            (750) - Permission management
├── setup_group_permissions.sh    (750) - Group management
├── .env                          (600) - Sensitive configuration
└── PERMISSION_REFERENCE.md       (644) - Documentation
```

Sistem permission ini memastikan hanya user yang berwenang yang bisa menjalankan script critical untuk WhatsApp webhook deployment! 🔐
