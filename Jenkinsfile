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
                            // Stash any local changes before pulling
                            sh 'git stash'
                            sh 'git config pull.rebase true'
                            sh 'git pull origin tbp.owhub.1'
                            // Apply stashed changes back if needed
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
                        sh 'cat whatsappbot-with-gpt/waweb-api/.env' 
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
                        echo "Container node1 was not running or could not be stopped/removed: ${e}"
                    }
                    try {
                        sh 'docker stop ngrok-tunnel'
                        sh 'docker rm ngrok-tunnel'
                    } catch (Exception e) {
                        echo "Container ngrok-tunnel was not running or could not be stopped/removed: ${e}"
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
                    sh 'docker build --network=host -t waweb-api .'
                }
            }
        }
        stage('Run New Container') {
            steps {
                // Gunakan network yang konsisten
                sh 'docker run -d --name node1 --network=host --dns=8.8.8.8 --dns=1.1.1.1 waweb-api'
            }
        }
        stage('Expose via Ngrok') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'ngrok-auth-token', variable: 'NGROK_TOKEN')]) {
                        // Pull ngrok image
                        sh 'docker pull ngrok/ngrok:latest'
                        
                        // Start ngrok dengan custom domain
                        sh '''
                        docker run -d --name ngrok-tunnel --net=host \
                        -e NGROK_AUTHTOKEN=$NGROK_TOKEN \
                        ngrok/ngrok:latest http --url=ungraphical-uranous-tambra.ngrok-free.app 3000
                        '''
                        
                        sleep(10)
                        
                        // Check ngrok status dan tampilkan URL
                        script {
                            try {
                                sh 'docker logs ngrok-tunnel'
                                
                                def customUrl = "https://ungraphical-uranous-tambra.ngrok-free.app"
                                echo "🌐 WhatsApp Bot is accessible at: ${customUrl}"
                                echo "🚀 Ngrok tunnel established successfully!"
                                
                                sh "echo '${customUrl}' > ngrok_url.txt"
                                sh "echo 'WhatsApp Bot URL: ${customUrl}' > deployment_info.txt"
                                
                                // Verify ngrok API
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
                    echo "📊 Container Status:"
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)"'
                    
                    echo "📋 Initial Container Logs:"
                    try {
                        sh 'docker logs node1'
                    } catch (Exception e) {
                        echo "Could not get initial logs: ${e}"
                    }
                    
                    echo "📈 Monitoring live logs for 60 seconds..."
                    script {
                        try {
                            timeout(time: 60, unit: 'SECONDS') {
                                sh '''
                                echo "=== STARTING LIVE LOGS MONITORING ==="
                                docker logs -f node1 &
                                LOGS_PID=$!
                                
                                # Monitor selama 60 detik
                                sleep 60
                                
                                # Kill logs process
                                kill $LOGS_PID 2>/dev/null || true
                                echo "=== LOGS MONITORING COMPLETED ==="
                                '''
                            }
                        } catch (Exception e) {
                            echo "Logs monitoring completed or interrupted: ${e}"
                        }
                    }
                    
                    echo "✅ Container monitoring completed"
                    echo "📊 Final Container Status:"
                    sh 'docker ps | grep -E "(node1|ngrok-tunnel)"'
                    
                    // Health check
                    echo "🏥 Health Check:"
                    script {
                        try {
                            sh 'curl -f http://localhost:3000/health 2>/dev/null || curl -f http://localhost:3000 2>/dev/null || echo "⚠️  Health check failed - container might still be starting"'
                        } catch (Exception e) {
                            echo "Health check: ${e}"
                        }
                    }
                }
            }
        }
        stage('Network Diagnostics') {
            steps {
                script {
                    echo "🔍 Running network diagnostics..."
                    
                    // Test DNS resolution dari container
                    sh '''
                    docker exec node1 nslookup graph.facebook.com || echo "DNS resolution failed"
                    docker exec node1 ping -c 3 8.8.8.8 || echo "Ping to 8.8.8.8 failed"
                    docker exec node1 curl -I https://graph.facebook.com/v18.0 --connect-timeout 10 || echo "Facebook API connection failed"
                    '''
                    
                    // Check container network
                    sh 'docker exec node1 cat /etc/resolv.conf'
                    sh 'docker exec node1 ip route show'
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline execution completed'
            script {
                try {
                    echo "📋 Final Container Logs Summary:"
                    sh 'docker logs --tail=20 node1 || echo "Could not get final logs"'
                    echo "📊 Container Status:"
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
            script {
                try {
                    echo "🎉 Deployment completed successfully!"
                    echo "🌐 Application accessible at: https://ungraphical-uranous-tambra.ngrok-free.app"
                    echo "🏠 Local access: http://localhost:3000"
                    sh 'docker inspect node1 --format="Container Status: {{.State.Status}}" || echo "Could not get container status"'
                } catch (Exception e) {
                    echo "Could not display success details: ${e}"
                }
            }
        }
        failure {
            echo '❌ Deployment failed. Check logs for details.'
            script {
                try {
                    echo "🔍 Error Analysis:"
                    sh 'docker logs --tail=50 node1 || echo "No node1 container logs available"'
                    sh 'docker logs --tail=20 ngrok-tunnel || echo "No ngrok-tunnel container logs available"'
                    sh 'docker ps -a | grep -E "(node1|ngrok-tunnel)" || echo "No containers found"'
                } catch (Exception e) {
                    echo "Could not display error logs: ${e}"
                }
            }
        }
    }
}
