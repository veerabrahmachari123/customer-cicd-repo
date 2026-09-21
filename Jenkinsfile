pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'UAT', 'PRODUCTION'],
            description: 'Select deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            trim: true,
            description: 'Docker image version, for example 5.0 or 5.1'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Must be YES for production deployment'
        )
    }

    environment {
        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'
    }

    stages {

        // ============================================================
        // 1. RESOLVE ENVIRONMENT
        // ============================================================

        stage('Resolve Configuration') {
            steps {
                script {

                    def version = params.VERSION?.trim()

                    if (!version) {
                        error('VERSION cannot be empty. Example: 5.0')
                    }

                    env.VERSION = version

                    if (params.ENVIRONMENT == 'DEV') {

                        env.GIT_BRANCH = 'develop'
                        env.NETWORK = 'customer-dev-net'
                        env.APP_CONTAINER = 'customer-app-dev'
                        env.DB_CONTAINER = 'customer-db-dev'
                        env.DB_VOLUME = 'customer-db-dev-data'
                        env.HOST_PORT = '8081'
                        env.DB_HOST = 'customer-db-dev'
                        env.DB_NAME = 'customer_dev'
                        env.DB_USER = 'customer_dev'

                    }
                    else if (params.ENVIRONMENT == 'UAT') {

                        env.GIT_BRANCH = 'release'
                        env.NETWORK = 'customer-uat-net'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.DB_VOLUME = 'customer-db-uat-data'
                        env.HOST_PORT = '8082'
                        env.DB_HOST = 'customer-db-uat'
                        env.DB_NAME = 'customer_uat'
                        env.DB_USER = 'customer_uat'

                    }
                    else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.GIT_BRANCH = 'main'
                        env.NETWORK = 'customer-prod-net'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.DB_VOLUME = 'customer-db-prod-data'
                        env.HOST_PORT = '8083'
                        env.DB_HOST = 'customer-db-prod'
                        env.DB_NAME = 'customer_prod'
                        env.DB_USER = 'customer_prod'

                        if (
                            params.ACTION == 'DEPLOY' &&
                            params.PRODUCTION_CONFIRMATION != 'YES'
                        ) {
                            error(
                                'Production deployment requires PRODUCTION_CONFIRMATION=YES'
                            )
                        }

                    }
                    else {
                        error('Invalid ENVIRONMENT selected')
                    }

                    env.IMAGE = "${env.IMAGE_REPOSITORY}:${env.VERSION}"

                    echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================
Environment           : ${params.ENVIRONMENT}
Action                : ${params.ACTION}
Version               : ${env.VERSION}
Git Branch            : ${env.GIT_BRANCH}
Network               : ${env.NETWORK}
Application Container : ${env.APP_CONTAINER}
Database Container    : ${env.DB_CONTAINER}
Database Volume       : ${env.DB_VOLUME}
Database Host         : ${env.DB_HOST}
Database Name         : ${env.DB_NAME}
Database User         : ${env.DB_USER}
Host Port             : ${env.HOST_PORT}
Container Port        : ${env.CONTAINER_PORT}
Docker Image          : ${env.IMAGE}
Run Tests             : ${params.RUN_TESTS}
============================================================
"""
                }
            }
        }


        // ============================================================
        // 2. VALIDATE PARAMETERS
        // ============================================================

        stage('Validate Parameters') {
            steps {
                script {

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.ACTION == 'DEPLOY' &&
                        params.PRODUCTION_CONFIRMATION != 'YES'
                    ) {
                        error(
                            'Production deployment blocked. Set PRODUCTION_CONFIRMATION=YES.'
                        )
                    }

                    if (!env.VERSION?.trim()) {
                        error('VERSION cannot be empty')
                    }

                    echo "Environment validated: ${params.ENVIRONMENT}"
                    echo "Action validated: ${params.ACTION}"
                    echo "Version validated: ${env.VERSION}"
                }
            }
        }


        // ============================================================
        // 3. CHECK DOCKER
        // ============================================================

        stage('Check Docker') {
            steps {
                bat '''
                    docker version
                '''
            }
        }


        // ============================================================
        // 4. CHECKOUT CORRECT BRANCH
        // ============================================================

        stage('Checkout Correct Branch') {
            steps {

                // Change YOUR_GIT_URL to your repository URL.
                // Example:
                // https://github.com/veerabrahmachari123/customer-cicd-repo.git

                bat """
                    git fetch --all
                    git checkout ${env.GIT_BRANCH}
                    git pull origin ${env.GIT_BRANCH}
                """

                echo "Correct branch selected: ${env.GIT_BRANCH}"
            }
        }


        // ============================================================
        // 5. RUN TESTS
        // ============================================================

        stage('Run Tests') {
            when {
                expression {
                    params.RUN_TESTS == 'YES'
                }
            }

            steps {
                bat '''
                    python --version
                    python -m pip install -r app\\requirements.txt
                    python -m pytest -q app\\test_app.py
                '''
            }
        }


        // ============================================================
        // 6. BUILD DOCKER IMAGE
        // ============================================================

        stage('Build Docker Image') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker build ^
                      --build-arg VERSION=${env.VERSION} ^
                      -t ${env.IMAGE} .
                """

            }
        }


        // ============================================================
        // 7. VERIFY IMAGE
        // ============================================================

        stage('Verify Docker Image') {
            steps {

                bat """
                    docker image inspect ${env.IMAGE}
                """

                echo "Docker image verified: ${env.IMAGE}"
            }
        }


        // ============================================================
        // 8. CREATE NETWORK
        // ============================================================

        stage('Prepare Docker Network') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker network inspect ${env.NETWORK} >nul 2>&1

                    IF ERRORLEVEL 1 (
                        docker network create ${env.NETWORK}
                    )
                """

                echo "Docker network ready: ${env.NETWORK}"
            }
        }


        // ============================================================
        // 9. CREATE DATABASE VOLUME
        // ============================================================

        stage('Prepare Database Volume') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker volume inspect ${env.DB_VOLUME} >nul 2>&1

                    IF ERRORLEVEL 1 (
                        docker volume create ${env.DB_VOLUME}
                    )
                """

                echo "Database volume ready: ${env.DB_VOLUME}"
            }
        }


        // ============================================================
        // 10. DEPLOY DATABASE
        // ============================================================

        stage('Deploy Database') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    withCredentials([
                        usernamePassword(
                            credentialsId: "db-${params.ENVIRONMENT.toLowerCase()}",
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            docker rm -f ${env.DB_CONTAINER} >nul 2>&1

                            docker run -d ^
                              --name ${env.DB_CONTAINER} ^
                              --network ${env.NETWORK} ^
                              -e POSTGRES_DB=${env.DB_NAME} ^
                              -e POSTGRES_USER=%DB_USER_SECRET% ^
                              -e POSTGRES_PASSWORD=%DB_PASSWORD_SECRET% ^
                              -v ${env.DB_VOLUME}:/var/lib/postgresql/data ^
                              -v "%CD%\\db\\init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                              postgres:16
                        """
                    }
                }
            }
        }


        // ============================================================
        // 11. WAIT FOR DATABASE
        // ============================================================

        stage('Wait For Database') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def databaseReady = false

                    for (int i = 1; i <= 30; i++) {

                        bat """
                            docker exec ${env.DB_CONTAINER} ^
                            pg_isready ^
                            -U ${env.DB_USER} ^
                            -d ${env.DB_NAME}
                        """

                        if (currentBuild.currentResult != 'FAILURE') {
                            databaseReady = true
                            break
                        }

                        sleep(time: 2, unit: 'SECONDS')
                    }

                    if (!databaseReady) {
                        error('Database did not become ready')
                    }
                }
            }
        }


        // ============================================================
        // 12. DEPLOY APPLICATION
        // ============================================================

        stage('Deploy Application') {
            when {
                expression {
                    params.ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    withCredentials([
                        usernamePassword(
                            credentialsId: "db-${params.ENVIRONMENT.toLowerCase()}",
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            docker rm -f ${env.APP_CONTAINER} >nul 2>&1

                            docker run -d ^
                              --name ${env.APP_CONTAINER} ^
                              --network ${env.NETWORK} ^
                              -p ${env.HOST_PORT}:8080 ^
                              -e ENVIRONMENT=${params.ENVIRONMENT} ^
                              -e APP_VERSION=${env.VERSION} ^
                              -e DB_HOST=${env.DB_HOST} ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=${env.DB_NAME} ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              ${env.IMAGE}
                        """
                    }
                }
            }
        }


        // ============================================================
        // 13. VALIDATE CONTAINERS
        // ============================================================

        stage('Validate Containers') {
            steps {

                bat """
                    docker inspect ${env.APP_CONTAINER} ^
                      --format="{{.State.Running}}"

                    docker inspect ${env.DB_CONTAINER} ^
                      --format="{{.State.Running}}"

                    docker ps
                """
            }
        }


        // ============================================================
        // 14. NETWORK VALIDATION
        // ============================================================

        stage('Validate Network') {
            steps {

                bat """
                    docker network inspect ${env.NETWORK}
                """
            }
        }


        // ============================================================
        // 15. HEALTH CHECK
        // ============================================================

        stage('Health Check') {
            steps {

                bat """
                    curl.exe --fail ^
                      --silent ^
                      --show-error ^
                      http://localhost:${env.HOST_PORT}/health
                """
            }
        }


        // ============================================================
        // 16. DATABASE CONNECTIVITY
        // ============================================================

        stage('Application To Database Connectivity') {
            steps {

                bat """
                    docker exec ${env.APP_CONTAINER} ^
                    python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); socket.create_connection((h,p),5).close(); print('DATABASE CONNECTIVITY SUCCESS:',h,p)"
                """
            }
        }


        // ============================================================
        // 17. ENVIRONMENT VALIDATION
        // ============================================================

        stage('Environment Validation') {
            steps {

                bat """
                    curl.exe --fail ^
                      --silent ^
                      http://localhost:${env.HOST_PORT}/environment
                """
            }
        }


        // ============================================================
        // 18. VERSION VALIDATION
        // ============================================================

        stage('Version Validation') {
            steps {

                bat """
                    curl.exe --fail ^
                      --silent ^
                      http://localhost:${env.HOST_PORT}/version
                """
            }
        }


        // ============================================================
        // 19. VOLUME INSPECTION
        // ============================================================

        stage('Volume Inspection') {
            steps {

                bat """
                    docker volume inspect ${env.DB_VOLUME}
                """
            }
        }


        // ============================================================
        // 20. FINAL STATUS
        // ============================================================

        stage('Deployment Successful') {
            steps {

                echo """
============================================================
DEPLOYMENT SUCCESSFUL
============================================================
Environment : ${params.ENVIRONMENT}
Version     : ${env.VERSION}
Application : ${env.APP_CONTAINER}
Database    : ${env.DB_CONTAINER}
Network     : ${env.NETWORK}
Port        : ${env.HOST_PORT}
============================================================
"""
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {
            echo '=========================================='
            echo 'DEPLOYMENT VALIDATION SUCCESSFUL'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo 'DEPLOYMENT FAILED'
            echo 'Check the failed stage above.'
            echo '=========================================='
        }

        always {
            echo "Build completed with status: ${currentBuild.currentResult}"
        }
    }
}