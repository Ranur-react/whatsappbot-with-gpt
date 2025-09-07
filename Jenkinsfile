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
                sh 'docker run -d --name node1 --network=host --dns=8.8.8.8 --dns=1.1.1.1 --dns=208.67.222.222 waweb-api'
            }
        }
        stage('Network Diagnostics') {
            steps {
                script {
                    echo "🔍 Running network diagnostics..."
                    sleep(10) // Wait for container to fully start
                    
                    sh '''
                    echo "=== Container Network Info ==="
                    docker exec node1 cat /etc/resolv.conf
                    docker exec node1 ip route show
                    
                    echo "=== DNS Resolution Test ==="
                    docker exec node1 nslookup graph.facebook.com || echo "❌ DNS resolution failed"
                    
                    echo "=== Network Connectivity Test ==="
                    docker exec node1 ping -c 3 8.8.8.8 || echo "❌ Ping to 8.8.8.8 failed"
                    
                    echo "=== Facebook API Test ==="
                    docker exec node1 curl -I https://graph.facebook.com/v18.0 --connect-timeout 10 || echo "❌ Facebook API connection failed"
                    '''
                }
            }
        }
        stage('Expose via Ngrok') {
            steps {
                script {
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
                                sh 'curl -f http://localhost:4040/api/tunnels || echo "⚠️  Ngrok API not responding"'
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
                    echo "🔍 Starting container monitoring for 1 minute..."
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)"'
                    
                    try {
                        sh 'docker logs node1'
                    } catch (Exception e) {
                        echo "Could not get initial logs: ${e}"
                    }
                    
                    script {
                        try {
                            timeout(time: 60, unit: 'SECONDS') {
                                sh '''
                                echo "=== STARTING LIVE LOGS MONITORING ==="
                                docker logs -f node1 &
                                LOGS_PID=$!
                                sleep 60
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
                    sh 'docker logs --tail=30 node1 || echo "Could not get final logs"'
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)" || echo "Containers not found"'
                    
                    if (fileExists('ngrok_url.txt')) {
                        def url = readFile('ngrok_url.txt').trim()
                        echo "📱 Your WhatsApp Bot is live at: ${url}"
                    }
                } catch (Exception e) {
                    echo "Could not display final status: ${e}"
                }
            }
        }
        success {
            echo '✅ Deployment successful! WhatsApp Bot is ready at: https://ungraphical-uranous-tambra.ngrok-free.app'
        }
        failure {
            script {
                try {
                    echo "🔍 Error Analysis:"
                    sh 'docker logs --tail=50 node1 || echo "No node1 logs"'
                    sh 'docker logs --tail=20 ngrok-tunnel || echo "No ngrok logs"'
                } catch (Exception e) {
                    echo "Could not display error logs: ${e}"
                }
            }
        }
    }
}
