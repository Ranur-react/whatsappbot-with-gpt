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
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'env_wa', variable: 'ENV_FILE')]) {
                        sh 'chmod -R 755 whatsappbot-with-gpt/'
                        sh 'cp $ENV_FILE whatsappbot-with-gpt/waweb-api/.env'api/.env'
                        sh 'cat whatsappbot-with-gpt/waweb-api/.env' 
                    }
                }
            }
        }
        stage('Container Renewal') {tage('Container Renewal') {
            steps {
                script {ipt {
                    try {{
                        sh 'docker stop node1'h 'docker stop node1'
                        sh 'docker rm node1'
                    } catch (Exception e) {
                        echo "Container node1 was not running or could not be stopped/removed: ${e}"e1 was not running or could not be stopped/removed: ${e}"
                    }
                }
            }
        }
        stage('Image Renewal') {tage('Image Renewal') {
            steps {
                script {ipt {
                    try {{
                        sh 'docker rmi waweb-api'h 'docker rmi waweb-api'
                    } catch (Exception e) {
                        echo "Image waweb-api could not be removed: ${e}"pi could not be removed: ${e}"
                    }
                }
            }
        }
        stage('Build Docker New Image') {tage('Build Docker New Image') {
            steps {
                dir('whatsappbot-with-gpt') {('whatsappbot-with-gpt') {
                    sh 'docker build --dns=8.8.8.8 --dns=1.1.1.1 -t waweb-api .'8.8.8 --dns=1.1.1.1 -t waweb-api .'
                    
                }
            }
        }
        stage('Run New Container') {tage('Run New Container') {
            steps {
                sh 'docker run -d --name node1 -p 3000:3000 waweb-api''docker run -d --name node1 -p 3000:3000 waweb-api'
            }
        }
    }
    post {ost {
        always {ways {
            echo 'This will always run' 'This will always run'
        }
        success {uccess {
            echo 'This will run only if successful''This will run only if successful'
        }
        failure {ailure {
            echo 'This will run only if failed''This will run only if failed'
        }
    }
}
