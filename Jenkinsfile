pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                sh 'make setup'
            }
        }

        stage('Lint') {
            steps {
                sh 'make lint'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'make test'
            }
        }

        stage('Train & Evaluate') {
            steps {
                sh 'make train'
            }
        }

        stage('Model Quality Gate') {
            steps {
                sh 'make validate'
            }
        }

        stage('Build Image') {
            steps {
                sh 'make build IMAGE_TAG=${IMAGE_TAG}'
            }
        }

        stage('Deploy') {
            steps {
                sh 'make deploy IMAGE_TAG=${IMAGE_TAG}'
            }
        }

        stage('Smoke Test') {
            steps {
                sh 'make smoke'
            }
        }
    }

    post {
        success {
            echo "Deployed build ${env.BUILD_NUMBER} -- open http://localhost:5050"
        }
        failure {
            echo "Pipeline failed -- previous deployment (if any) was left untouched."
        }
    }
}
