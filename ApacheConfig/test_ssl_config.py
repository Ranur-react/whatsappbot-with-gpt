#!/usr/bin/env python3
"""
Quick test script untuk memverifikasi konfigurasi SSL Corporate
"""
import os
import sys

# Load environment configuration
def load_env_config():
    """Load konfigurasi dari file .env"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    config = {}
    
    if not os.path.exists(env_file):
        print("❌ File .env tidak ditemukan!")
        return None
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove inline comments
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print("❌ Error reading .env file: {}".format(str(e)))
        return None
    
    return config

def test_ssl_files(config):
    """Test apakah file SSL Corporate sudah ada"""
    if config.get('SSL_TYPE') != 'corporate':
        print("⚠️  SSL_TYPE bukan corporate: {}".format(config.get('SSL_TYPE')))
        return False
    
    ssl_files = {
        'Certificate': config.get('CORPORATE_SSL_CERT_PATH'),
        'Private Key': config.get('CORPORATE_SSL_KEY_PATH'),
        'Chain': config.get('CORPORATE_SSL_CHAIN_PATH')
    }
    
    print("🔍 Checking Corporate SSL files...")
    all_exist = True
    
    for name, path in ssl_files.items():
        if not path:
            print("❌ {}: Path not configured".format(name))
            all_exist = False
            continue
            
        if os.path.exists(path):
            print("✅ {}: {} (exists)".format(name, path))
        else:
            print("❌ {}: {} (not found)".format(name, path))
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("SSL CORPORATE CONFIGURATION TEST")
    print("=" * 60)
    
    # Load configuration
    config = load_env_config()
    if not config:
        sys.exit(1)
    
    # Display current configuration
    print("\nCurrent Configuration:")
    print("- Domain: {}".format(config.get('DOMAIN_NAME', 'Not set')))
    print("- SSL Enabled: {}".format(config.get('ENABLE_SSL', 'Not set')))
    print("- SSL Type: {}".format(config.get('SSL_TYPE', 'Not set')))
    
    # Test SSL files
    print("\n" + "=" * 60)
    if test_ssl_files(config):
        print("\n✅ ALL SSL FILES FOUND!")
        print("Ready to run config2.py with Corporate SSL")
    else:
        print("\n❌ SOME SSL FILES MISSING!")
        print("Please upload the corporate SSL files before running config2.py")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Ensure all SSL files are uploaded to the server")
    print("2. Run: python3 config2.py")
    print("3. Script will detect corporate SSL and configure automatically")
    print("=" * 60)

if __name__ == "__main__":
    main()
