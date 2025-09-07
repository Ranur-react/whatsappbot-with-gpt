# Jenkins Docker WSL Setup Guide

## **Step-by-Step Konfigurasi Jenkins di Docker (WSL)**

### **Prerequisites: Setup Docker Engine di WSL**

#### 1. **Update package dan install dependencies**
```bash
sudo apt update
sudo apt install ca-certificates curl gnupg
```

#### 2. **Tambahkan Docker GPG key**
```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

#### 3. **Tambahkan repository Docker**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### 4. **Install Docker Engine**
```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### 5. **Enable systemd di WSL (jika belum aktif)**
```bash
sudo nano /etc/wsl.conf
```
Tambahkan:
```ini
[boot]
systemd=true
```

#### 6. **Restart WSL dari Windows PowerShell**
```powershell
wsl --shutdown
wsl --update
```
Lalu buka kembali Ubuntu WSL.

#### 7. **Verifikasi systemd aktif**
```bash
ps -p 1 -o comm=
```
Output harus: `systemd`

#### 8. **Start Docker daemon**
```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl status docker
```

#### 9. **(Optional) Agar bisa menjalankan docker tanpa sudo**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### **Jenkins Installation Steps**

#### 1. **Pull Jenkins Docker Image**
```bash
docker pull jenkins/jenkins:lts
```

#### 2. **Buat Folder untuk Jenkins Data**
```bash
mkdir -p ~/jenkins_home
```

#### 3. **Jalankan Jenkins Container**
```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```
- Port 8080: akses web Jenkins
- Port 50000: untuk agent/remote build

#### 4. **Akses Jenkins Web UI**
- Buka browser: `http://localhost:8080`
- Ambil initial admin password:
  ```bash
  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```

#### 5. **Install Plugin yang Dibutuhkan**
- Melalui UI Jenkins, install plugin:
  - Docker
  - Git
  - Pipeline
  - Blue Ocean (optional)

#### 6. **Konfigurasi Credentials & Repository**
- Tambahkan credentials (SSH key/token) untuk akses repo
- Tambahkan repository Git pada Jenkins

#### 7. **Buat Pipeline untuk Auto Build/Deploy**
- Buat `Jenkinsfile` di repo Anda, contoh sederhana:
  ```groovy
  pipeline {
    agent any
    stages {
      stage('Build') {
        steps {
          sh 'docker build -t myapp:latest .'
        }
      }
      stage('Deploy') {
        steps {
          sh 'docker run -d --name myapp myapp:latest'
        }
      }
    }
  }
  ```
- Pastikan Docker tersedia di Jenkins container (atau gunakan Docker agent)

#### 8. **Trigger Otomatis**
- Atur webhook di GitHub/GitLab ke Jenkins
- Atur polling SCM di Jenkins jika perlu

---

**Referensi Resmi:**  
- [Jenkins Docker Documentation](https://www.jenkins.io/doc/book/installing/docker/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Engine Installation](https://docs.docker.com/engine/install/ubuntu/)

---

### **Troubleshooting Tips**
- Jika Docker daemon tidak bisa start, pastikan systemd aktif di WSL
- Untuk cek status Docker: `sudo systemctl status docker`
- Untuk restart Docker: `sudo systemctl restart docker`
- Jika ada error "Cannot connect to Docker daemon", pastikan Docker service sudah running
