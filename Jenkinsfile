

pipeline {
    agent any

    stages {
        stage('Clone or Pull') {
            steps {
                script {
                    if (fileExists('whatsappbot-with-gpt')) {
                        dir('whatsappbot-with-gpt') {
                            sh 'git fetch'
                            sh 'git checkout main'
                            sh 'git config pull.rebase true'
                            sh 'git pull origin main'
                        }
                    } else {
                        sh 'git clone -b main https://github.com/Ranur-react/whatsappbot-with-gpt.git'
                    }
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    sh 'cat /mnt/env-aset/wabot/absekol.env'
                    sh 'cp /mnt/env-aset/wabot/absekol.env whatsappbot-with-gpt/waweb-api/.env'
                    sh 'cat whatsappbot-with-gpt/waweb-api/.env'
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
                    sh 'docker build -t waweb-api .'
                }
            }
        }
        stage('Run New Container') {
            steps {
                sh 'docker run -d --name node1 -p 211:22 -p 3000:3000 waweb-api'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
    }
}
