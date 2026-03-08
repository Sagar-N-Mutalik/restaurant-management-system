pipeline{
    agent any
    environment{
        DOCKER_IMAGE = 'sagarnm/restaurant-app'
        DOCKER_TAG="{env.BUILD_ID}"
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials-id')
        EC2_IP = '100.53.23.255'
        SSH_CREDENTIALS = credentials('ec2-ssh-credentials-id')
    }

    stages{
        stage('checkout'){
            steps{
                checkout scm
            }
        }
        stage('run test'){
            steps{
                echo 'running django tests...'
                sh 'docker build -t test-image .'
                sh 'docker run --rm test-image python manage.py test'
            }
        }
        stage('build docker image'){
            steps{
                echo 'building docker image...'
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }
        stage('push to docker registry'){
            steps{
                echo 'pushing to docker registry...'
                sh "echo \$DOCKER_CREDENTIALS_PSW | docker login -u \$DOCKER_CREDENTIALS_USR --password-stdin"
                sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker push ${DOCKER_IMAGE}:latest"
            }
        }
        stage('Deploy to AWS EC2') {
            steps {
                echo 'Deploying to AWS...'
                sshagent(['ec2-ssh-key-id']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${EC2_IP} '
                            docker pull ${DOCKER_IMAGE}:latest &&
                            docker stop restaurant-app || true &&
                            docker rm restaurant-app || true &&
                            docker run -d -p 80:8000 --name restaurant-app ${DOCKER_IMAGE}:latest
                        '
                    """
                }
            }
        }
    }
}