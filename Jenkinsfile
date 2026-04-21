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
                    # ① 只停止非 MySQL 服务（容器保留，数据卷不丢失）
                    docker-compose stop backend frontend xmind-service || true
                    # ② 增量构建 + 启动非 MySQL 服务（--build 只重建有改动的镜像）
                    docker-compose up -d --build backend frontend xmind-service
                    # ③ 等待后端就绪
                    for i in $(seq 1 30); do
                      curl -sf http://localhost:8080/api/plan/list 2>/dev/null && break
                      sleep 3
                    done
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
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
