#!/bin/bash
echo "=== FIXING APACHE CONFIG MANUALLY ==="

# Fix the current broken config
sed -i 's/Require ip 127.0.0.1\\n        Require ip 10.100.129.51\\n/        Require ip 127.0.0.1\n        Require ip 10.100.129.51\n/g' /etc/apache2/sites-available/botdev-owhub.totalbp.com.conf

echo "=== TESTING APACHE CONFIG ==="
apache2ctl configtest

if [ $? -eq 0 ]; then
    echo "✅ Apache config is now valid!"
    echo "=== RELOADING APACHE ==="
    systemctl reload apache2
    echo "✅ Apache reloaded successfully!"
else
    echo "❌ Apache config still has errors"
    echo "Content around the error:"
    grep -n -A5 -B5 "server-status" /etc/apache2/sites-available/botdev-owhub.totalbp.com.conf
fi
