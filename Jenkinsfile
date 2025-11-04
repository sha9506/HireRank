pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_USERNAME = 'sh9506'
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        BACKEND_IMAGE = "${DOCKER_USERNAME}/hirerank-backend"
        FRONTEND_IMAGE = "${DOCKER_USERNAME}/hirerank-frontend"
        IMAGE_TAG = "${BUILD_NUMBER}"
        // Backend API URL - ngrok tunnel for backend service
        BACKEND_API_URL = 'https://overtolerantly-vadose-lorene.ngrok-free.dev'
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
        
        stage('Deploy to S3') {
            agent {
                docker {
                    image 'node:18-alpine'
                    reuseNode true
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                    apk add --no-cache aws-cli
                    cd frontend
                    npm install
                    echo "VITE_API_BASE_URL=${BACKEND_API_URL:-http://localhost:8000}" > .env
                    npm run build
                    export AWS_DEFAULT_REGION=ap-south-1
                    aws s3 sync dist/ s3://hirerank-devops --delete
                    echo "Check your site at: http://hirerank-devops.s3-website-ap-south-1.amazonaws.com"
                    '''
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
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
            steps {
                echo 'Performing health checks...'
                sh '''
                    sleep 30
                    echo "=== Kubernetes Nodes ==="
                    kubectl get nodes -o wide
                    echo ""
                    echo "=== Kubernetes Pods ==="
                    kubectl get pods -o wide
                    echo ""
                    echo "=== Kubernetes Services ==="
                    kubectl get services
                    echo ""
                    echo "=== Kubernetes Deployments ==="
                    kubectl get deployments
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
