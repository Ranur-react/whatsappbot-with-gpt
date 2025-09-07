pipeline {
    agent any

    stages {
        stage('Clone or Pull') {
            steps {
                script {
                    if (fileExists('whatsappbot-with-gpt')) {
                        dir('whatsappbot-with-gpt') {
                            sh 'git fetch'
                            sh 'git checkout tbp.owhub.1'
                            sh 'git stash'
                            sh 'git config pull.rebase true'
                            sh 'git pull origin tbp.owhub.1'
                            script {
                                try {
                                    sh 'git stash pop'
                                } catch (Exception e) {
                                    echo "No stash to pop or merge conflict: ${e}"
                                }
                            }
                        }
                    } else {
                        sh 'git clone -b tbp.owhub.1 https://github.com/Ranur-react/whatsappbot-with-gpt.git'
                    }
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'env_wa', variable: 'ENV_FILE')]) {
                        sh 'chmod -R 755 whatsappbot-with-gpt/'
                        sh 'cp $ENV_FILE whatsappbot-with-gpt/waweb-api/.env'
                        echo "✅ .env file copied successfully"
                    }
                }
            }
        }
        stage('Container Renewal') {
            steps {
                script {
                    try {
                        sh 'docker stop node1'
                        sh 'docker rm node1'
                    } catch (Exception e) {
                        echo "Container node1 was not running: ${e}"
                    }
                    try {
                        sh 'docker stop ngrok-tunnel'
                        sh 'docker rm ngrok-tunnel'
                    } catch (Exception e) {
                        echo "Container ngrok-tunnel was not running: ${e}"
                    }
                }
            }
        }
        stage('Image Renewal') {
            steps {
                script {
                    try {
                        sh 'docker rmi waweb-api'
                    } catch (Exception e) {
                        echo "Image waweb-api could not be removed: ${e}"
                    }
                }
            }
        }
        stage('Build Docker New Image') {
            steps {
                dir('whatsappbot-with-gpt') {
                    sh 'docker build --network=host --no-cache -t waweb-api .'
                }
            }
        }
        stage('Run New Container') {
            steps {
                script {
                    // Create custom bridge network with proper DNS
                    sh '''
                    docker network create --driver bridge \
                    --subnet=172.20.0.0/16 \
                    --gateway=172.20.0.1 \
                    --opt com.docker.network.driver.mtu=1500 \
                    wabot-network || echo "Network already exists"
                    '''
                    
                    // Run container with custom network and explicit DNS
                    sh '''
                    docker run -d --name node1 \
                    --network=wabot-network \
                    --dns=8.8.8.8 \
                    --dns=1.1.1.1 \
                    --dns=208.67.222.222 \
                    --dns-search=. \
                    --dns-opt=ndots:1 \
                    -p 3000:3000 \
                    -e NODE_OPTIONS="--dns-result-order=ipv4first" \
                    --restart=unless-stopped \
                    waweb-api
                    '''
                    
                    // Wait for container to start
                    sleep(15)
                    
                    echo "🔍 Checking container status..."
                    sh 'docker ps | grep node1 || echo "❌ Container node1 is not running"'
                    
                    // Get container status
                    def containerStatus = sh(script: 'docker inspect node1 --format="{{.State.Status}}"', returnStdout: true).trim()
                    echo "📊 Container Status: ${containerStatus}"
                    
                    if (containerStatus != "running") {
                        echo "❌ Container failed to start. Getting logs..."
                        sh 'docker logs node1'
                        error("Container node1 failed to start properly")
                    } else {
                        echo "✅ Container node1 is running successfully"
                    }
                }
            }
        }
        stage('Network Diagnostics & Fix') {
            steps {
                script {
                    echo "🔍 Running network diagnostics and fixes..."
                    
                    // Check if container is still running before diagnostics
                    def containerRunning = sh(script: 'docker ps -q -f name=node1', returnStdout: true).trim()
                    if (!containerRunning) {
                        echo "❌ Container node1 is not running. Skipping diagnostics."
                        sh 'docker logs node1'
                        return
                    }
                    
                    sh '''
                    echo "=== Container Network Info ==="
                    docker exec node1 cat /etc/resolv.conf || echo "❌ Could not read resolv.conf"
                    docker exec node1 ip route show || echo "❌ Could not show routes"
                    
                    echo "=== Updating DNS in Container ==="
                    docker exec node1 sh -c "echo 'nameserver 8.8.8.8' > /tmp/resolv.conf.new"
                    docker exec node1 sh -c "echo 'nameserver 1.1.1.1' >> /tmp/resolv.conf.new"
                    docker exec node1 sh -c "echo 'nameserver 208.67.222.222' >> /tmp/resolv.conf.new"
                    docker exec node1 sh -c "echo 'search .' >> /tmp/resolv.conf.new"
                    docker exec node1 sh -c "cp /tmp/resolv.conf.new /etc/resolv.conf" || echo "Could not update resolv.conf"
                    
                    echo "=== Updated DNS Configuration ==="
                    docker exec node1 cat /etc/resolv.conf
                    
                    echo "=== DNS Resolution Test ==="
                    docker exec node1 nslookup graph.facebook.com 8.8.8.8 || echo "❌ DNS resolution failed"
                    docker exec node1 dig @8.8.8.8 graph.facebook.com || echo "❌ Dig failed"
                    
                    echo "=== Network Connectivity Test ==="
                    docker exec node1 ping -c 3 8.8.8.8 || echo "❌ Ping to 8.8.8.8 failed"
                    
                    echo "=== Facebook API Test ==="
                    docker exec node1 curl -I https://graph.facebook.com/v18.0 --connect-timeout 10 --max-time 30 || echo "❌ Facebook API connection failed"
                    
                    echo "=== Direct IP Test ==="
                    docker exec node1 curl -I https://157.240.12.35/v18.0 --connect-timeout 10 -H "Host: graph.facebook.com" || echo "❌ Direct IP connection failed"
                    '''
                }
            }
        }
        stage('Expose via Ngrok') {
            steps {
                script {
                    // Only proceed if main container is running
                    def containerRunning = sh(script: 'docker ps -q -f name=node1', returnStdout: true).trim()
                    if (!containerRunning) {
                        echo "❌ Container node1 is not running. Skipping ngrok setup."
                        return
                    }
                    
                    withCredentials([string(credentialsId: 'ngrok-auth-token', variable: 'NGROK_TOKEN')]) {
                        sh 'docker pull ngrok/ngrok:latest'
                        
                        sh '''
                        docker run -d --name ngrok-tunnel --net=host \
                        -e NGROK_AUTHTOKEN=$NGROK_TOKEN \
                        ngrok/ngrok:latest http --url=ungraphical-uranous-tambra.ngrok-free.app 3000
                        '''
                        
                        sleep(10)
                        
                        script {
                            try {
                                def customUrl = "https://ungraphical-uranous-tambra.ngrok-free.app"
                                echo "🌐 WhatsApp Bot is accessible at: ${customUrl}"
                                sh "echo '${customUrl}' > ngrok_url.txt"
                                
                                // Test ngrok tunnel
                                sh 'curl -f http://localhost:4040/api/tunnels || echo "⚠️  Ngrok API not responding"'
                                sh "curl -I ${customUrl} --connect-timeout 10 || echo '⚠️  Ngrok tunnel not responding'"
                                
                            } catch (Exception e) {
                                echo "Error checking ngrok status: ${e}"
                                sh 'docker logs ngrok-tunnel'
                            }
                        }
                    }
                }
            }
        }
        stage('Monitor Container Logs') {
            steps {
                script {
                    echo "🔍 Starting container monitoring for 2 minutes..."
                    
                    // Check container status first
                    def containerRunning = sh(script: 'docker ps -q -f name=node1', returnStdout: true).trim()
                    if (!containerRunning) {
                        echo "❌ Container node1 is not running. Cannot monitor logs."
                        sh 'docker logs node1 || echo "No logs available"'
                        return
                    }
                    
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)"'
                    
                    try {
                        sh 'docker logs --tail=50 node1'
                    } catch (Exception e) {
                        echo "Could not get initial logs: ${e}"
                    }
                    
                    script {
                        try {
                            timeout(time: 120, unit: 'SECONDS') {
                                sh '''
                                echo "=== STARTING LIVE LOGS MONITORING (2 minutes) ==="
                                docker logs -f node1 &
                                LOGS_PID=$!
                                sleep 120
                                kill $LOGS_PID 2>/dev/null || true
                                echo "=== LOGS MONITORING COMPLETED ==="
                                '''
                            }
                        } catch (Exception e) {
                            echo "Logs monitoring completed: ${e}"
                        }
                    }
                    
                    echo "🏥 Health Check:"
                    script {
                        try {
                            sh 'curl -f http://localhost:3000/health 2>/dev/null || curl -f http://localhost:3000 2>/dev/null || echo "⚠️ Health check failed"'
                            
                            // Test sending a template message
                            echo "🧪 Testing Facebook API connectivity from container..."
                            sh 'docker exec node1 curl -f https://graph.facebook.com/v18.0 --connect-timeout 5 || echo "⚠️ Facebook API still not accessible"'
                            
                        } catch (Exception e) {
                            echo "Health check: ${e}"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    echo "📋 Final Container Logs:"
                    sh 'docker logs --tail=50 node1 || echo "Could not get final logs"'
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)" || echo "Containers not found"'
                    
                    if (fileExists('ngrok_url.txt')) {
                        def url = readFile('ngrok_url.txt').trim()
                        echo "📱 Your WhatsApp Bot is live at: ${url}"
                    }
                    
                    // Debug info
                    echo "🔧 Debug Information:"
                    sh 'docker inspect node1 --format="{{.State.Status}}: {{.State.Error}}" || echo "Could not inspect container"'
                    sh 'docker exec node1 cat /etc/resolv.conf || echo "Could not read final DNS config"'
                    
                } catch (Exception e) {
                    echo "Could not display final status: ${e}"
                }
            }
        }
        success {
            echo '✅ Deployment successful! WhatsApp Bot is ready at: https://ungraphical-uranous-tambra.ngrok-free.app'
            echo '🔧 Test your bot by sending a message to the WhatsApp number'
        }
        failure {
            script {
                try {
                    echo "🔍 Error Analysis:"
                    sh 'docker logs --tail=100 node1 || echo "No node1 logs"'
                    sh 'docker logs --tail=20 ngrok-tunnel || echo "No ngrok logs"'
                    sh 'docker network ls | grep wabot || echo "Network info not available"'
                } catch (Exception e) {
                    echo "Could not display error logs: ${e}"
                }
            }
        }
    }
}
