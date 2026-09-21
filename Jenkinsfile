pipeline {
    agent any

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'UAT', 'PRODUCTION'], description: 'Target environment')
        choice(name: 'ACTION', choices: ['DEPLOY', 'ROLLBACK'], description: 'Deployment action')
        string(name: 'VERSION', defaultValue: '5.0', description: 'Application version/image tag')
        choice(name: 'RUN_TESTS', choices: ['YES', 'NO'], description: 'Run automated tests')
        choice(name: 'PRODUCTION_CONFIRMATION', choices: ['NO', 'YES'], description: 'Required for production deployment')
    }

    environment {
        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'
    }

    stages {
        stage('Resolve Configuration') {
            steps {
                script {
                    def cfg = [
                        DEV: [
                            branch: 'develop', network: 'customer-dev-net',
                            app: 'customer-app-dev', db: 'customer-db-dev',
                            volume: 'customer-db-dev-data', port: '8081',
                            host: 'customer-db-dev', name: 'customer_dev', user: 'customer_dev'
                        ],
                        UAT: [
                            branch: 'release', network: 'customer-uat-net',
                            app: 'customer-app-uat', db: 'customer-db-uat',
                            volume: 'customer-db-uat-data', port: '8082',
                            host: 'customer-db-uat', name: 'customer_uat', user: 'customer_uat'
                        ],
                        PRODUCTION: [
                            branch: 'main', network: 'customer-prod-net',
                            app: 'customer-app-prod', db: 'customer-db-prod',
                            volume: 'customer-db-prod-data', port: '8083',
                            host: 'customer-db-prod', name: 'customer_prod', user: 'customer_prod'
                        ]
                    ][params.ENVIRONMENT]

                    if (!cfg) error('Invalid ENVIRONMENT')
                    if (params.ACTION == 'DEPLOY' && params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRMATION != 'YES') {
                        error('Production deployment requires PRODUCTION_CONFIRMATION=YES')
                    }
                    if (!(params.VERSION ==~ /^[0-9]+\\.[0-9]+(?:\\.[0-9]+)?$/)) {
                        error('VERSION must look like 5.0 or 5.1')
                    }

                    env.GIT_BRANCH = cfg.branch
                    env.NETWORK = cfg.network
                    env.APP_CONTAINER = cfg.app
                    env.DB_CONTAINER = cfg.db
                    env.DB_VOLUME = cfg.volume
                    env.HOST_PORT = cfg.port
                    env.DB_HOST = cfg.host
                    env.DB_NAME = cfg.name
                    env.DB_USER = cfg.user
                    env.IMAGE = "${IMAGE_REPOSITORY}:${params.VERSION}"

                    echo """============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================
Environment          : ${params.ENVIRONMENT}
Action               : ${params.ACTION}
Version              : ${params.VERSION}
Git Branch           : ${env.GIT_BRANCH}
Network              : ${env.NETWORK}
Application Container: ${env.APP_CONTAINER}
Database Container   : ${env.DB_CONTAINER}
Database Volume      : ${env.DB_VOLUME}
Database Host        : ${env.DB_HOST}
Database Name        : ${env.DB_NAME}
Host Port            : ${env.HOST_PORT}
Container Port       : ${env.CONTAINER_PORT}
Image                : ${env.IMAGE}
Run Tests            : ${params.RUN_TESTS}
============================================================"""
                }
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                // Replace both placeholders with your Jenkins/Git values.
                git branch: env.GIT_BRANCH,
                    credentialsId: 'git-credentials',
                    url: 'YOUR_GIT_URL'
            }
        }

        stage('Run Tests') {
            when { expression { params.RUN_TESTS == 'YES' } }
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r app/requirements.txt
                    pytest -q app/test_app.py
                '''
            }
        }

        stage('Build Image') {
            when { expression { params.ACTION == 'DEPLOY' } }
            steps {
                sh "docker build --build-arg VERSION=${params.VERSION} -t ${IMAGE} ."
            }
        }

        stage('Verify Image') {
            steps {
                sh "docker image inspect ${IMAGE}"
            }
        }

        stage('Prepare Network and Volume') {
            when { expression { params.ACTION == 'DEPLOY' } }
            steps {
                sh '''
                    docker network inspect "$NETWORK" >/dev/null 2>&1 || docker network create "$NETWORK"
                    docker volume inspect "$DB_VOLUME" >/dev/null 2>&1 || docker volume create "$DB_VOLUME"
                '''
            }
        }

        stage('Deploy Database') {
            when { expression { params.ACTION == 'DEPLOY' } }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "db-${params.ENVIRONMENT.toLowerCase()}",
                    usernameVariable: 'DB_USER_SECRET',
                    passwordVariable: 'DB_PASSWORD_SECRET'
                )]) {
                    sh '''
                        docker rm -f "$DB_CONTAINER" >/dev/null 2>&1 || true
                        docker run -d                           --name "$DB_CONTAINER"                           --network "$NETWORK"                           -e POSTGRES_DB="$DB_NAME"                           -e POSTGRES_USER="$DB_USER_SECRET"                           -e POSTGRES_PASSWORD="$DB_PASSWORD_SECRET"                           -v "$DB_VOLUME:/var/lib/postgresql/data"                           -v "$PWD/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro"                           postgres:16
                    '''
                }
            }
        }

        stage('Wait for Database') {
            when { expression { params.ACTION == 'DEPLOY' } }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "db-${params.ENVIRONMENT.toLowerCase()}",
                    usernameVariable: 'DB_USER_SECRET',
                    passwordVariable: 'DB_PASSWORD_SECRET'
                )]) {
                    sh '''
                        for i in $(seq 1 30); do
                          if docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER_SECRET" -d "$DB_NAME" >/dev/null 2>&1; then
                            echo "Database is ready"
                            exit 0
                          fi
                          sleep 2
                        done
                        docker logs "$DB_CONTAINER" || true
                        exit 1
                    '''
                }
            }
        }

        stage('Deploy Application') {
            when { expression { params.ACTION == 'DEPLOY' } }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "db-${params.ENVIRONMENT.toLowerCase()}",
                    usernameVariable: 'DB_USER_SECRET',
                    passwordVariable: 'DB_PASSWORD_SECRET'
                )]) {
                    sh '''
                        docker rm -f "$APP_CONTAINER" >/dev/null 2>&1 || true
                        docker run -d                           --name "$APP_CONTAINER"                           --network "$NETWORK"                           -p "$HOST_PORT:8080"                           -e ENVIRONMENT="$ENVIRONMENT"                           -e APP_VERSION="$VERSION"                           -e DB_HOST="$DB_HOST"                           -e DB_PORT=5432                           -e DB_NAME="$DB_NAME"                           -e DB_USER="$DB_USER_SECRET"                           -e DB_PASSWORD="$DB_PASSWORD_SECRET"                           "$IMAGE"
                    '''
                }
            }
        }

        stage('Validate Containers') {
            steps {
                sh '''
                    test "$(docker inspect -f '{{.State.Running}}' "$APP_CONTAINER")" = "true"
                    test "$(docker inspect -f '{{.State.Running}}' "$DB_CONTAINER")" = "true"
                    docker ps
                '''
            }
        }

        stage('Validate Network') {
            steps {
                sh '''
                    docker network inspect "$NETWORK" | tee network-inspect.json
                    grep -q "\"Name\": \"$APP_CONTAINER\"" network-inspect.json
                    grep -q "\"Name\": \"$DB_CONTAINER\"" network-inspect.json
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh 'curl --fail --silent --show-error "http://localhost:${HOST_PORT}/health"'
            }
        }

        stage('Application to Database Connectivity') {
            steps {
                sh '''
                    docker exec "$APP_CONTAINER" python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); socket.create_connection((h,p),5).close(); print('DATABASE CONNECTIVITY SUCCESS:',h,p)"
                '''
            }
        }

        stage('Environment Validation') {
            steps {
                sh '''
                    curl --fail --silent "http://localhost:${HOST_PORT}/environment" | tee environment.json
                    grep -q "$ENVIRONMENT" environment.json
                '''
            }
        }

        stage('Version Validation') {
            steps {
                sh '''
                    curl --fail --silent "http://localhost:${HOST_PORT}/version" | tee version.json
                    grep -q "$VERSION" version.json
                '''
            }
        }

        stage('Volume Inspection') {
            steps {
                sh 'docker volume inspect "$DB_VOLUME" | tee volume-inspect.json'
            }
        }
    }

    post {
        success { echo 'DEPLOYMENT VALIDATION SUCCESSFUL' }
        failure { echo 'DEPLOYMENT VALIDATION FAILED' }
    }
}
