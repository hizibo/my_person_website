pipeline {
    agent any
    
    environment {
        DOCKER_HOST = 'unix:///var/run/docker.sock'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git(
                    url: 'git@github.com:hizibo/my_person_website.git',
                    credentialsId: 'github-ssh',
                    branch: 'main'
                )
            }
        }
        
        stage('Build and Deploy') {
            steps {
                sh '''
                    # 只删除非 MySQL 服务，保持 MySQL 容器运行
                    docker-compose rm -sf backend frontend xmind-service
                    # 重新构建并启动（MySQL 保持不变，数据卷持久化）
                    docker-compose build --no-cache
                    docker-compose up -d
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    sleep 30
                    curl -f http://localhost:80 || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
