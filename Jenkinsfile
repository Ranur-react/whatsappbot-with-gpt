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
                            sh 'git config pull.rebase true'
                            sh 'git pull origin tbp.owhub.1'
                        }
                    } else {
                        sh 'git clone -b tbp.owhub.1 https://github.com/Ranur-react/whatsappbot-with-gpt.git'
                    }
                }
            }
        }
        // stage('Copy .env File') {
        //     steps {
        //         script {
        //             sh 'cat /mnt/env-aset/wabot/owhub.env'
        //             sh 'cp /mnt/env-aset/wabot/owhub.env whatsappbot-with-gpt/waweb-api/.env'
        //             sh 'cat whatsappbot-with-gpt/waweb-api/.env'
        //         }
        //     }
        // }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'env_wa', variable: 'ENV_FILE')]) {
                        sh 'sudo cp $ENV_FILE whatsappbot-with-gpt/waweb-api/.env'
                        sh 'sudo chmod 644 whatsappbot-with-gpt/waweb-api/.env'
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
                    sh 'docker build --dns=8.8.8.8 --dns=1.1.1.1 -t waweb-api .'
                    
                }
            }
        }
        stage('Run New Container') {
            steps {
                sh 'docker run -d --name node1 -p 3000:3000 waweb-api'
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
