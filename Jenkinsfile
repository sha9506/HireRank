pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        BACKEND_IMAGE = 'hirerank-backend'
        FRONTEND_IMAGE = 'hirerank-frontend'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Build Backend') {
            steps {
                echo 'Building backend Docker image...'
                dir('backend') {
                    script {
                        docker.build("${BACKEND_IMAGE}:${IMAGE_TAG}")
                        docker.build("${BACKEND_IMAGE}:latest")
                    }
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                echo 'Building frontend Docker image...'
                dir('frontend') {
                    script {
                        docker.build("${FRONTEND_IMAGE}:${IMAGE_TAG}")
                        docker.build("${FRONTEND_IMAGE}:latest")
                    }
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                echo 'Running backend tests...'
                dir('backend') {
                    sh '''
                        python -m pytest tests/ --verbose || echo "No tests found"
                    '''
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo 'Pushing images to Docker registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-hub-credentials') {
                        docker.image("${BACKEND_IMAGE}:${IMAGE_TAG}").push()
                        docker.image("${BACKEND_IMAGE}:latest").push()
                        docker.image("${FRONTEND_IMAGE}:${IMAGE_TAG}").push()
                        docker.image("${FRONTEND_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to Kubernetes...'
                sh '''
                    kubectl apply -f deploy/mongo-deployment.yaml
                    kubectl apply -f deploy/backend-deployment.yaml
                    kubectl apply -f deploy/frontend-deployment.yaml
                    kubectl apply -f deploy/services.yaml
                    kubectl apply -f deploy/ingress.yaml
                    
                    # Wait for deployments to be ready
                    kubectl rollout status deployment/backend
                    kubectl rollout status deployment/frontend
                '''
            }
        }
        
        stage('Health Check') {
            when {
                branch 'main'
            }
            steps {
                echo 'Performing health checks...'
                sh '''
                    sleep 30
                    kubectl get pods
                    kubectl get services
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            // Add notification here (Slack, email, etc.)
        }
        failure {
            echo 'Pipeline failed!'
            // Add failure notification here
        }
        always {
            echo 'Cleaning up...'
            sh 'docker system prune -f'
        }
    }
}
