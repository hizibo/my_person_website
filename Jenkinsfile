pipeline {
    agent any

    environment {
        PROJECT_DIR = '/opt/my-toolbox'
        SERVER_IP   = '175.178.98.241'
    }

    // 构建参数
    parameters {
        booleanParam(name: 'FORCE_REBUILD', defaultValue: false, description: '强制全量重建（忽略变更检测）')
        booleanParam(name: 'SKIP_TEST', defaultValue: false, description: '跳过后端单元测试')
        string(name: 'BRANCH', defaultValue: 'main', description: 'Git 分支')
    }

    // 触发器：每分钟检查 SCM 变更
    triggers {
        pollSCM('H/1 * * * *')
    }

    stages {
        // ========== Stage 1: 拉取代码 ==========
        stage('拉取代码') {
            steps {
                git(
                    url: 'git@github.com:hizibo/my_person_website.git',
                    credentialsId: 'github-ssh',
                    branch: "${params.BRANCH}"
                )
                sh 'git clean -fdx'
                sh 'echo "当前提交: $(git log -1 --oneline)"'
            }
        }

        // ========== Stage 2: 变更检测 ==========
        stage('变更检测') {
            steps {
                script {
                    if (params.FORCE_REBUILD) {
                        env.NEED_BACKEND = 'true'
                        env.NEED_FRONTEND = 'true'
                        env.NEED_PYTHON = 'true'
                        env.SKIP_BUILD = 'false'
                        echo '⚡ 强制全量重建模式'
                    } else {
                        def changes = sh(script: 'git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD', returnStdout: true).trim()
                        echo "变更文件:\n${changes}"

                        env.NEED_BACKEND = changes.contains('backend/') ? 'true' : 'false'
                        env.NEED_FRONTEND = changes.contains('frontend/') ? 'true' : 'false'
                        env.NEED_PYTHON = changes.contains('python-services/') ? 'true' : 'false'

                        // docker-compose.yml 或 Jenkinsfile 变更也触发全量重建
                        if (changes.contains('docker-compose.yml') || changes.contains('Jenkinsfile')) {
                            env.NEED_BACKEND = 'true'
                            env.NEED_FRONTEND = 'true'
                            env.NEED_PYTHON = 'true'
                        }

                        if (env.NEED_BACKEND == 'false' && env.NEED_FRONTEND == 'false' && env.NEED_PYTHON == 'false') {
                            env.SKIP_BUILD = 'true'
                            echo '✅ 无服务变更，跳过构建'
                        } else {
                            env.SKIP_BUILD = 'false'
                            echo "需要重建 → 后端: ${env.NEED_BACKEND}, 前端: ${env.NEED_FRONTEND}, Python: ${env.NEED_PYTHON}"
                        }
                    }
                }
            }
        }

        // ========== Stage 3: 构建并部署 ==========
        stage('构建并部署') {
            when {
                expression { env.SKIP_BUILD != 'true' }
            }
            steps {
                sh '''
                    SERVICES=""
                    [ "$NEED_BACKEND" = "true" ] && SERVICES="$SERVICES backend"
                    [ "$NEED_FRONTEND" = "true" ] && SERVICES="$SERVICES frontend"
                    [ "$NEED_PYTHON" = "true" ] && SERVICES="$SERVICES python-tools"

                    echo "📦 重建服务: $SERVICES"

                    # 先清理所有容器（含依赖），再重建
                    docker-compose down --remove-orphans || true
                    # 移除不属于当前 compose 项目的残留容器
                    docker rm -f website-mysql website-backend website-frontend website-python-tools 2>/dev/null || true
                    docker-compose up -d --build $SERVICES
                '''
            }
        }

        // ========== Stage 4: 后端健康检查 ==========
        stage('后端健康检查') {
            when {
                expression { env.NEED_BACKEND == 'true' && env.SKIP_BUILD != 'true' }
            }
            steps {
                retry(5) {
                    sleep time: 8, unit: 'SECONDS'
                    sh '''
                        HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/plan/list 2>/dev/null)
                        if [ "$HTTP_CODE" != "200" ]; then
                            echo "❌ 后端未就绪 HTTP=$HTTP_CODE，重试中..."
                            exit 1
                        fi
                        echo "✅ 后端就绪 HTTP=$HTTP_CODE"
                    '''
                }
            }
        }

        // ========== Stage 5: 前端健康检查 ==========
        stage('前端健康检查') {
            when {
                expression { env.NEED_FRONTEND == 'true' && env.SKIP_BUILD != 'true' }
            }
            steps {
                retry(3) {
                    sleep time: 5, unit: 'SECONDS'
                    sh '''
                        HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:80 2>/dev/null)
                        if [ "$HTTP_CODE" != "200" ]; then
                            echo "❌ 前端未就绪 HTTP=$HTTP_CODE，重试中..."
                            exit 1
                        fi
                        echo "✅ 前端就绪 HTTP=$HTTP_CODE"
                    '''
                }
            }
        }
    }

    // ========== 全局 post ==========
    post {
        success {
            echo '🎉 部署成功！'
        }
        failure {
            echo '❌ 部署失败！请检查日志'
        }
        always {
            deleteDir()
        }
    }
}
