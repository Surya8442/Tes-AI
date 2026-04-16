pipeline {
agent any

tools {
    jdk 'JDK17'
}

environment {
    DOCKER_USER = "surya8442"
    IMAGE_NAME = "tes-ai-app"
    IMAGE_TAG = "v1"

    DOCKER_CREDS = "Docker_cred"
    NEXUS_CREDS = "nexus_cred"

    NEXUS_URL = "http://65.2.49.196:8081"
    NEXUS_REPO = "tes-ai-repo"

    SONARQUBE_ENV = "sonar-server"

    AWS_REGION = "ap-south-1"
    EKS_CLUSTER = "mycluster"

    NOTIFY_EMAIL = "suryakandipalli@gmail.com"
}

stages {

    stage('Checkout') {
        steps {
            git branch: 'main', url: 'https://github.com/Surya8442/Tes-AI.git'
        }
    }

    stage('Verify Python') {
        steps {
            sh 'python3 --version'
            sh 'pip3 --version'
        }
    }

    stage('Install Dependencies') {
        steps {
            sh 'pip3 install -r requirements.txt'
        }
    }

    stage('SonarQube Analysis') {
        steps {
            withSonarQubeEnv("${SONARQUBE_ENV}") {
                sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=tes-ai \
                    -Dsonar.sources=backend \
                    -Dsonar.host.url=$SONAR_HOST_URL \
                    -Dsonar.login=$SONAR_AUTH_TOKEN
                '''
            }
        }
    }

    stage('Quality Gate') {
        steps {
            timeout(time: 2, unit: 'MINUTES') {
                waitForQualityGate abortPipeline: true
            }
        }
    }

    stage('Package Artifact') {
        steps {
            sh 'zip -r tes-ai.zip .'
        }
    }

    stage('Upload to Nexus') {
        steps {
            withCredentials([usernamePassword(
                credentialsId: "${NEXUS_CREDS}",
                usernameVariable: 'USER',
                passwordVariable: 'PASS'
            )]) {
                sh '''
                    curl -u $USER:$PASS --upload-file tes-ai.zip \
                    $NEXUS_URL/repository/$NEXUS_REPO/tes-ai.zip
                '''
            }
        }
    }

    stage('Build Docker Image') {
        steps {
            sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
        }
    }

    stage('Push to DockerHub') {
        steps {
            withCredentials([usernamePassword(
                credentialsId: "${DOCKER_CREDS}",
                usernameVariable: 'USER',
                passwordVariable: 'PASS'
            )]) {
                sh '''
                    echo $PASS | docker login -u $USER --password-stdin
                    docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKER_USER/$IMAGE_NAME:$IMAGE_TAG
                    docker push $DOCKER_USER/$IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }

    stage('Deploy to EKS') {
        steps {
            sh '''
                aws eks --region $AWS_REGION update-kubeconfig --name $EKS_CLUSTER
                kubectl apply -f deployment.yml
                kubectl rollout status deployment tes-ai
            '''
        }
    }
}

post {

    success {
        emailext(
            to: "${NOTIFY_EMAIL}",
            subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
```

TES-AI Deployment Successful 🚀

Docker Image:
${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}

Cluster:
${EKS_CLUSTER}

Build URL:
${env.BUILD_URL}
"""
)
}

```
    failure {
        emailext(
            to: "${NOTIFY_EMAIL}",
            subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
```

TES-AI Pipeline Failed ❌

Check Logs:
${env.BUILD_URL}
"""
)
}

```
    always {
        echo 'Cleaning workspace...'
        cleanWs()
    }
}
```

}
