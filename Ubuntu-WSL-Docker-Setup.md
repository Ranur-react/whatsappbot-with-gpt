# Setup Ubuntu WSL + Docker - Alternatif Lebih Ringan

## Perbandingan Resource Usage

| Aspek | WSL2 | Hyper-V |
|-------|------|---------|
| RAM Base | 200-500MB | 2GB+ |
| Storage | 2-4GB | 6-10GB |
| Boot Time | 2-3 detik | 30-60 detik |
| CPU Overhead | <5% | 10-15% |
| Integration | Native | Network-based |

## Spesifikasi Minimal WSL

### Host Requirements (Lebih Ringan)
- **RAM Host**: 4GB (vs 8GB untuk Hyper-V)
- **Storage**: 10GB kosong
- **CPU**: Any 64-bit processor
- **Windows**: Windows 10 Build 19041+ atau Windows 11

### WSL Resource Allocation
- **RAM WSL**: 1-2GB (dynamic)
- **Storage**: 10GB virtual disk (sparse)
- **CPU**: Shared dengan host

## Setup WSL + Docker (Metode Termudah)

### 1. Install WSL2

```powershell
# Jalankan sebagai Administrator di PowerShell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart komputer
Restart-Computer
```

### 2. Download dan Install WSL2 Kernel Update
```powershell
# Download WSL2 kernel update dari Microsoft
# https://aka.ms/wsl2kernel
# Install file yang didownload
```

### 3. Set WSL2 sebagai Default
```powershell
wsl --set-default-version 2
```

### 4. Install Ubuntu dari Microsoft Store
```powershell
# Option 1: Via Microsoft Store
# Buka Microsoft Store → Search "Ubuntu" → Install "Ubuntu"

# Option 2: Via Command Line
winget install Canonical.Ubuntu
```

### 5. Setup Ubuntu WSL
```bash
# First time setup - buat user dan password
# Username: admin (atau sesuai preferensi)
# Password: [password yang kuat]

# Update sistem
sudo apt update && sudo apt upgrade -y
```

## Install Docker di WSL2

### Method 1: Docker Desktop (Recommended - Paling Mudah)

#### Download dan Install Docker Desktop
1. Download dari [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install dengan opsi **"Use WSL2 instead of Hyper-V"**
3. Restart komputer
4. Buka Docker Desktop
5. Settings → Resources → WSL Integration
6. Enable integration dengan Ubuntu distribution

#### Verify Docker
```bash
# Di Ubuntu WSL terminal
docker --version
docker run hello-world
```

### Method 2: Docker Engine Native (Lebih Ringan)

```bash
# Install Docker Engine di WSL Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Auto-start Docker (optional)
echo 'sudo service docker start' >> ~/.bashrc
```

## Setup Development Environment

### Install Development Tools
```bash
# Essential tools
sudo apt install -y curl wget git nano htop net-tools unzip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python (jika diperlukan)
sudo apt install -y python3 python3-pip

# Verify installations
node --version
npm --version
docker --version
```

### Setup Ngrok
```bash
# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Setup authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## Konfigurasi WSL untuk Optimal Performance

### WSL Configuration File
```bash
# Buat file .wslconfig di Windows User Directory
# C:\Users\[YourUsername]\.wslconfig
```

```ini
[wsl2]
memory=2GB          # Batasi RAM maksimal WSL
processors=2        # Batasi CPU cores
swap=1GB           # Swap file
swapFile=C:\\temp\\wsl-swap.vhdx

[experimental]
autoMemoryReclaim=gradual    # Auto cleanup memory
```

### Ubuntu WSL Config
```bash
# Edit /etc/wsl.conf di dalam WSL
sudo nano /etc/wsl.conf
```

```ini
[boot]
systemd=true        # Enable systemd (untuk Docker service)

[interop]
enabled=true
appendWindowsPath=true

[network]
generateHosts=true
generateResolvConf=true
```

## Setup Proyek WhatsApp Bot di WSL

### Clone dan Setup Proyek
```bash
# Navigate ke direktori project
cd /mnt/e/SourceCode

# Atau clone fresh
git clone https://github.com/your-repo/whatsappbot-with-gpt.git
cd whatsappbot-with-gpt

# Install dependencies jika Node.js project
npm install

# Build Docker image
docker build -t whatsapp-bot .

# Run container
docker run -d -p 3000:3000 --name whatsapp-bot whatsapp-bot

# Expose dengan ngrok
ngrok http 3000
```

### Access dari Windows
```bash
# WSL memiliki shared network dengan Windows
# Aplikasi di WSL port 3000 bisa diakses dari Windows di:
# http://localhost:3000
# atau
# http://127.0.0.1:3000
```

## File System Integration

### Akses File Windows dari WSL
```bash
# Windows drives tersedia di /mnt/
cd /mnt/c/Users/YourUsername/
cd /mnt/e/SourceCode/

# Edit file Windows langsung dari WSL
nano /mnt/e/SourceCode/whatsappbot-with-gpt/package.json
```

### Akses File WSL dari Windows
```powershell
# WSL filesystem tersedia di Windows Explorer:
# \\wsl$\Ubuntu\home\username\
# atau
# \\wsl.localhost\Ubuntu\home\username\
```

## Performance Monitoring

### Monitor Resource Usage
```bash
# Check WSL memory usage
free -h

# Check Docker stats
docker stats

# Check running processes
htop

# Check disk usage
df -h
```

### Windows Task Manager
- WSL akan muncul sebagai "Vmmem" process
- Monitor memory usage dari sini

## Troubleshooting WSL

### Common Issues dan Solutions

#### 1. WSL Not Starting
```powershell
# Restart WSL
wsl --shutdown
wsl

# Reset WSL distribution
wsl --unregister Ubuntu
# Re-install dari Microsoft Store
```

#### 2. Docker Issues
```bash
# Restart Docker service
sudo service docker restart

# Check Docker status
sudo service docker status

# Manual Docker daemon start
sudo dockerd
```

#### 3. Memory Issues
```bash
# Clear cache
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# Restart WSL untuk reset memory
```

#### 4. Network Issues
```bash
# Reset network
sudo service networking restart

# Check IP
ip addr show eth0
```

## Advantages WSL vs Hyper-V

### WSL Advantages:
✅ **Startup**: Instant (2-3 detik)  
✅ **Memory**: Dynamic, mulai dari 200MB  
✅ **File Access**: Direct Windows integration  
✅ **Performance**: Near-native Linux performance  
✅ **Networking**: Shared dengan Windows  
✅ **Backup**: Simple, just copy directory  

### Hyper-V Disadvantages:
❌ **Startup**: 30-60 detik boot time  
❌ **Memory**: Fixed 2GB+ allocation  
❌ **File Access**: Requires network sharing  
❌ **Performance**: VM overhead ~10-15%  
❌ **Networking**: Requires configuration  
❌ **Backup**: Full VM export needed  

## Development Workflow dengan WSL

### Daily Usage
```bash
# Start development (dari Windows Terminal)
wsl

# Navigate to project
cd /mnt/e/SourceCode/whatsappbot-with-gpt

# Start services
docker-compose up -d

# Run ngrok
ngrok http 3000

# Development server running!
```

### IDE Integration
- **VS Code**: Install "Remote - WSL" extension
- **Edit files**: Directly dari Windows atau via WSL
- **Terminal**: Integrated WSL terminal di VS Code

## Kesimpulan

**WSL2 adalah pilihan terbaik untuk:**
- Development dengan resource terbatas
- Quick prototyping dan testing
- Integration dengan Windows workflow
- Multiple project development

**Gunakan Hyper-V hanya jika:**
- Butuh full VM isolation
- Testing production-like environment
- Multiple OS requirements
- Learning server administration

Untuk proyek WhatsApp Bot Anda, **WSL2 + Docker** akan memberikan experience terbaik dengan resource minimal.
