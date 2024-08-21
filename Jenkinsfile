pipeline {
    agent {
        node { label 'jenkinsworker00' }
    }
    
    environment {
        
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials'
        HARBOR_CREDENTIALS = 'harbor-paas-credentials'
        DOCKER_HUB_IMAGE_NAME = 'indigopaas/slat'
        HARBOR_IMAGE_NAME = 'datacloud-middleware/slat'
        COMPONENT_NAME = 'slat'
    }
    
    stages {
        stage('Build and Tag Docker Image') {
            
            steps {
                script {
                    // Build Docker image
                    def dockerImage = docker.build("${COMPONENT_NAME}:${env.BRANCH_NAME}", "-f docker/Dockerfile .")

                    sh("docker tag ${COMPONENT_NAME}:${env.BRANCH_NAME} ${HARBOR_IMAGE_NAME}:${env.BRANCH_NAME}")
                    sh("docker tag ${COMPONENT_NAME}:${env.BRANCH_NAME} ${DOCKER_HUB_IMAGE_NAME}:${env.BRANCH_NAME}")
                }
            }
        }
        
        stage('Push to Docker Hub and Harbor') {
            parallel {
                stage('Push to Docker Hub') {
                    steps {
                        script {
                            // Retrieve the Docker image object from the previous stage
                            def dockerhubImage = docker.image("${DOCKER_HUB_IMAGE_NAME}:${env.BRANCH_NAME}")
                            
                            // Login to Docker Hub
                            docker.withRegistry('https://index.docker.io/v1/', DOCKER_HUB_CREDENTIALS) {
                                // Push the Docker image to Docker Hub
                                dockerhubImage.push()
                            }
                        }
                    }
                }
                
                stage('Push to Harbor') {
                    steps {
                        script {
                            // Retrieve the Docker image object from the previous stage
                            def harborImage = docker.image("${HARBOR_IMAGE_NAME}:${env.BRANCH_NAME}")
                            
                            // Login to Harbor
                            docker.withRegistry('https://harbor.cloud.infn.it', HARBOR_CREDENTIALS) {
                                // Push the Docker image to Harbor
                                harborImage.push()
                            }
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Docker image build and push successful!'
        }
        failure {
            echo 'Docker image build and push failed!'
        }
    }
}
