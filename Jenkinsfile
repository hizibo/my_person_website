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
                // 清理workspace中的未跟踪文件，防止残留旧代码导致构建失败
                sh 'git clean -fdx'
            }
        }
        
        stage('Detect Changes') {
            steps {
                script {
                    // 获取与上次构建的差异
                    def changes = sh(script: 'git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD', returnStdout: true).trim()
                    
                    echo "Changed files:\n${changes}"
                    
                    // 检测各服务是否有改动
                    env.NEED_BACKEND = changes.contains('backend/') ? 'true' : 'false'
                    env.NEED_FRONTEND = changes.contains('frontend/') ? 'true' : 'false'
                    env.NEED_PYTHON_TOOLS = changes.contains('python-services/') ? 'true' : 'false'
                    
                    echo "Need rebuild - backend: ${env.NEED_BACKEND}, frontend: ${env.NEED_FRONTEND}, python-tools: ${env.NEED_PYTHON_TOOLS}"
                    
                    // 如果没有任何服务改动，跳过构建
                    if (env.NEED_BACKEND == 'false' && env.NEED_FRONTEND == 'false' && env.NEED_PYTHON_TOOLS == 'false') {
                        env.SKIP_BUILD = 'true'
                        echo "No service changes detected, skipping build."
                    }
                }
            }
        }
        
        stage('Build and Deploy') {
            when { 
                expression { env.SKIP_BUILD != 'true' } 
            }
            steps {
                sh '''
                    SERVICES=""
                    [ "$NEED_BACKEND" = "true" ] && SERVICES="$SERVICES backend"
                    [ "$NEED_FRONTEND" = "true" ] && SERVICES="$SERVICES frontend"
                    [ "$NEED_PYTHON_TOOLS" = "true" ] && SERVICES="$SERVICES python-tools"
                    
                    echo "Rebuilding services: $SERVICES"
                    
                    # 停止需要重建的服务
                    for svc in $SERVICES; do
                        docker-compose stop $svc || true
                    done
                    
                    # 增量构建 + 启动
                    docker-compose up -d --build $SERVICES
                    
                    # 等待后端就绪（如果重建了 backend）
                    if [ "$NEED_BACKEND" = "true" ]; then
                        for i in $(seq 1 30); do
                            curl -sf http://localhost:8080/api/plan/list 2>/dev/null && break
                            sleep 3
                        done
                    fi
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh 'curl -f http://localhost:80 || exit 1'
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
