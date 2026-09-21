pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    parameters {

        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'UAT', 'PRODUCTION'],
            description: 'Deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Docker image version'
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
        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'
        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'
    }

    stages {

        stage('Resolve Configuration') {
            steps {
                script {

                    echo '============================================================'
                    echo 'RESOLVED DEPLOYMENT CONFIGURATION'
                    echo '============================================================'

                    if (params.ENVIRONMENT == 'DEV') {

                        env.DEPLOY_GIT_BRANCH = 'develop'
                        env.DEPLOY_NETWORK = 'customer-dev-net'
                        env.DEPLOY_APP_CONTAINER = 'customer-app-dev'
                        env.DEPLOY_DB_CONTAINER = 'customer-db-dev'
                        env.DEPLOY_DB_VOLUME = 'customer-db-dev-data'
                        env.DEPLOY_DB_HOST = 'customer-db-dev'
                        env.DEPLOY_DB_NAME = 'customer_dev'
                        env.DEPLOY_DB_USER = 'customer_dev'
                        env.DEPLOY_HOST_PORT = '8081'

                    } else if (params.ENVIRONMENT == 'UAT') {

                        env.DEPLOY_GIT_BRANCH = 'release'
                        env.DEPLOY_NETWORK = 'customer-uat-net'
                        env.DEPLOY_APP_CONTAINER = 'customer-app-uat'
                        env.DEPLOY_DB_CONTAINER = 'customer-db-uat'
                        env.DEPLOY_DB_VOLUME = 'customer-db-uat-data'
                        env.DEPLOY_DB_HOST = 'customer-db-uat'
                        env.DEPLOY_DB_NAME = 'customer_uat'
                        env.DEPLOY_DB_USER = 'customer_uat'
                        env.DEPLOY_HOST_PORT = '8082'

                    } else {

                        env.DEPLOY_GIT_BRANCH = 'main'
                        env.DEPLOY_NETWORK = 'customer-prod-net'
                        env.DEPLOY_APP_CONTAINER = 'customer-app-prod'
                        env.DEPLOY_DB_CONTAINER = 'customer-db-prod'
                        env.DEPLOY_DB_VOLUME = 'customer-db-prod-data'
                        env.DEPLOY_DB_HOST = 'customer-db-prod'
                        env.DEPLOY_DB_NAME = 'customer_prod'
                        env.DEPLOY_DB_USER = 'customer_prod'
                        env.DEPLOY_HOST_PORT = '8083'
                    }

                    env.DEPLOY_VERSION = params.VERSION.trim()
                    env.DEPLOY_IMAGE = "${env.IMAGE_REPOSITORY}:${env.DEPLOY_VERSION}"

                    echo "Environment           : ${params.ENVIRONMENT}"
                    echo "Action                : ${params.ACTION}"
                    echo "Version               : ${env.DEPLOY_VERSION}"
                    echo "Git Branch            : ${env.DEPLOY_GIT_BRANCH}"
                    echo "Network               : ${env.DEPLOY_NETWORK}"
                    echo "Application Container : ${env.DEPLOY_APP_CONTAINER}"
                    echo "Database Container    : ${env.DEPLOY_DB_CONTAINER}"
                    echo "Database Volume       : ${env.DEPLOY_DB_VOLUME}"
                    echo "Database Host         : ${env.DEPLOY_DB_HOST}"
                    echo "Database Name         : ${env.DEPLOY_DB_NAME}"
                    echo "Database User         : ${env.DEPLOY_DB_USER}"
                    echo "Host Port             : ${env.DEPLOY_HOST_PORT}"
                    echo "Container Port        : ${env.CONTAINER_PORT}"
                    echo "Docker Image          : ${env.DEPLOY_IMAGE}"
                    echo "Run Tests             : ${params.RUN_TESTS}"

                    echo '============================================================'
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {

                    if (!(params.VERSION ==~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/)) {
                        error("Invalid VERSION: ${params.VERSION}")
                    }

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRMATION != 'YES'
                    ) {
                        error('Production deployment requires PRODUCTION_CONFIRMATION = YES')
                    }

                    echo "Environment validated: ${params.ENVIRONMENT}"
                    echo "Action validated: ${params.ACTION}"
                    echo "Version validated: ${params.VERSION}"
                    echo "Git branch validated: ${env.DEPLOY_GIT_BRANCH}"
                }
            }
        }

        stage('Check Docker') {
            steps {
                bat '''
                    echo ==========================================
                    echo DOCKER CHECK
                    echo ==========================================

                    docker version

                    if errorlevel 1 (
                        echo ERROR: Docker is not available.
                        exit /b 1
                    )

                    echo Docker is available.
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {

                checkout([
                    $class: 'GitSCM',
                    branches: [
                        [
                            name: "*/${env.DEPLOY_GIT_BRANCH}"
                        ]
                    ],
                    userRemoteConfigs: [
                        [
                            url: "${env.REPO_URL}"
                        ]
                    ],
                    extensions: [
                        [
                            $class: 'CloneOption',
                            shallow: false,
                            noTags: false
                        ]
                    ]
                ])

                bat '''
                    echo ==========================================
                    echo CURRENT BRANCH / COMMIT
                    echo ==========================================

                    echo ===== LAST COMMIT =====
                    git log -1 --oneline

                    echo.
                    echo ===== STATUS =====
                    git status --short
                '''
            }
        }

        stage('Run Tests') {
            when {
                expression {
                    params.RUN_TESTS == 'YES'
                }
            }

            steps {
                bat '''
                    echo ==========================================
                    echo RUNNING TESTS
                    echo ==========================================

                    docker run --rm ^
                        -v "%CD%:/workspace" ^
                        -w /workspace ^
                        python:3.12-slim ^
                        sh -c "pip install --no-cache-dir -q -r app/requirements.txt && pytest -q app/test_app.py"

                    if errorlevel 1 (
                        echo ERROR: Tests failed.
                        exit /b 1
                    )

                    echo Tests PASSED.
                '''
            }
        }

        stage('Capture Previous Deployment') {
            steps {
                bat '''
                    echo ==========================================
                    echo CAPTURING PREVIOUS DEPLOYMENT
                    echo ==========================================

                    if exist previous-image.txt del /q previous-image.txt
                    if exist previous-version.txt del /q previous-version.txt

                    docker inspect "%DEPLOY_APP_CONTAINER%" ^
                        --format="{{.Config.Image}}" ^
                        > previous-image.txt 2>nul

                    if not exist previous-image.txt (
                        echo NONE>previous-image.txt
                        echo NONE>previous-version.txt
                    )

                    if exist previous-image.txt (
                        for /f "usebackq delims=" %%A in ("previous-image.txt") do (
                            if not "%%A"=="NONE" (
                                echo %%A>previous-image.txt
                            )
                        )
                    )
                '''

                script {
                    def previousImage = 'NONE'
                    def previousVersion = 'NONE'

                    if (fileExists('previous-image.txt')) {
                        previousImage = readFile('previous-image.txt').trim()
                    }

                    if (
                        previousImage &&
                        previousImage != 'NONE' &&
                        previousImage.contains(':')
                    ) {
                        previousVersion = previousImage.substring(
                            previousImage.lastIndexOf(':') + 1
                        )
                    }

                    writeFile(
                        file: 'previous-version.txt',
                        text: previousVersion
                    )

                    env.PREVIOUS_IMAGE = previousImage
                    env.PREVIOUS_VERSION = previousVersion

                    echo ''
                    echo "Previous Image   : ${previousImage}"
                    echo "Previous Version : ${previousVersion}"
                    echo ''
                }
            }
        }

        stage('Prepare Docker Network') {
            steps {
                bat '''
                    echo ==========================================
                    echo PREPARING DOCKER NETWORK
                    echo ==========================================

                    docker network inspect "%DEPLOY_NETWORK%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating network: %DEPLOY_NETWORK%

                        docker network create "%DEPLOY_NETWORK%"

                        if errorlevel 1 (
                            echo ERROR: Could not create network.
                            exit /b 1
                        )
                    ) else (
                        echo Network already exists: %DEPLOY_NETWORK%
                    )

                    docker network inspect "%DEPLOY_NETWORK%" > network-inspect-before.json
                '''
            }
        }

        stage('Prepare Database Volume') {
            steps {
                bat '''
                    echo ==========================================
                    echo PREPARING DATABASE VOLUME
                    echo ==========================================

                    docker volume inspect "%DEPLOY_DB_VOLUME%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating volume: %DEPLOY_DB_VOLUME%

                        docker volume create "%DEPLOY_DB_VOLUME%"

                        if errorlevel 1 (
                            echo ERROR: Could not create volume.
                            exit /b 1
                        )
                    ) else (
                        echo Volume already exists: %DEPLOY_DB_VOLUME%
                    )

                    docker volume inspect "%DEPLOY_DB_VOLUME%" > volume-inspect.json
                '''
            }
        }

        stage('Prepare Target Image') {
            steps {
                script {

                    if (params.ACTION == 'DEPLOY') {

                        echo "Building ${env.DEPLOY_IMAGE}"

                        bat """
                            echo ==========================================
                            echo BUILDING DOCKER IMAGE
                            echo ==========================================

                            docker build ^
                                --build-arg VERSION=${env.DEPLOY_VERSION} ^
                                -t ${env.DEPLOY_IMAGE} .

                            if errorlevel 1 (
                                echo ERROR: Docker build failed.
                                exit /b 1
                            )
                        """

                    } else {

                        echo "Checking rollback image ${env.DEPLOY_IMAGE}"

                        bat """
                            docker image inspect ${env.DEPLOY_IMAGE} >nul 2>&1

                            if errorlevel 1 (
                                echo ERROR: Rollback image ${env.DEPLOY_IMAGE} does not exist.
                                exit /b 1
                            )

                            echo Rollback image exists.
                        """
                    }
                }
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat '''
                    echo ==========================================
                    echo VERIFYING DOCKER IMAGE
                    echo ==========================================

                    docker image inspect "%DEPLOY_IMAGE%" > image-inspect.json

                    if errorlevel 1 (
                        echo ERROR: Docker image does not exist.
                        exit /b 1
                    )

                    echo.
                    echo Docker image verified successfully:
                    echo %DEPLOY_IMAGE%

                    echo.
                    echo ===== DOCKER IMAGES =====

                    docker images customer-app
                '''
            }
        }

        stage('Deploy Database') {
            steps {
                script {

                    def credentialId

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    } else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    } else {
                        credentialId = 'db-production'
                    }

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USERNAME_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            echo ==========================================
                            echo DEPLOYING DATABASE
                            echo ==========================================

                            docker container inspect "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                            if errorlevel 1 (

                                echo Database container does not exist.
                                echo Creating database container...

                                docker run -d ^
                                    --name "%DEPLOY_DB_CONTAINER%" ^
                                    --network "%DEPLOY_NETWORK%" ^
                                    --restart unless-stopped ^
                                    -e POSTGRES_DB="%DEPLOY_DB_NAME%" ^
                                    -e POSTGRES_USER="%DB_USERNAME_SECRET%" ^
                                    -e POSTGRES_PASSWORD="%DB_PASSWORD_SECRET%" ^
                                    -v "%DEPLOY_DB_VOLUME%:/var/lib/postgresql/data" ^
                                    -v "%CD%/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                                    postgres:16

                                if errorlevel 1 (
                                    echo ERROR: Database container creation failed.
                                    exit /b 1
                                )

                            ) else (

                                echo Database container already exists.

                                docker start "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                                echo Ensuring database is connected to expected network.

                                docker network connect "%DEPLOY_NETWORK%" "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                                if errorlevel 1 (
                                    echo Database is already connected to the network.
                                )
                            )

                            echo.
                            echo Database ready: %DEPLOY_DB_CONTAINER%
                        """
                    }
                }
            }
        }

        stage('Wait For Database') {
            steps {
                script {

                    timeout(time: 120, unit: 'SECONDS') {

                        waitUntil {

                            def result = bat(
                                script: '''
                                    docker exec "%DEPLOY_DB_CONTAINER%" ^
                                        pg_isready ^
                                        -U "%DEPLOY_DB_USER%" ^
                                        -d "%DEPLOY_DB_NAME%"
                                ''',
                                returnStatus: true
                            )

                            if (result == 0) {
                                echo 'Database is READY.'
                                return true
                            }

                            echo 'Waiting for database...'

                            sleep(
                                time: 5,
                                unit: 'SECONDS'
                            )

                            return false
                        }
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {

                    def credentialId

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    } else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    } else {
                        credentialId = 'db-production'
                    }

                    echo 'Deploying application...'

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USERNAME_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            echo ==========================================
                            echo DEPLOYING APPLICATION
                            echo ==========================================

                            docker rm -f "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                            docker run -d ^
                                --name "%DEPLOY_APP_CONTAINER%" ^
                                --network "%DEPLOY_NETWORK%" ^
                                --restart unless-stopped ^
                                -p "%DEPLOY_HOST_PORT%:%CONTAINER_PORT%" ^
                                -e APP_ENV="%ENVIRONMENT%" ^
                                -e APP_VERSION="%DEPLOY_VERSION%" ^
                                -e DB_HOST="%DEPLOY_DB_HOST%" ^
                                -e DB_PORT="5432" ^
                                -e DB_NAME="%DEPLOY_DB_NAME%" ^
                                -e DB_USER="%DB_USERNAME_SECRET%" ^
                                -e DB_PASSWORD="%DB_PASSWORD_SECRET%" ^
                                "%DEPLOY_IMAGE%"

                            if errorlevel 1 (
                                echo ERROR: Application failed to start.
                                exit /b 1
                            )

                            echo.
                            echo Application started: %DEPLOY_APP_CONTAINER%
                        """
                    }
                }
            }
        }

        stage('Validate Containers') {
            steps {
                bat '''
                    echo ==========================================
                    echo VALIDATING CONTAINERS
                    echo ==========================================

                    echo.
                    echo ===== APPLICATION CONTAINER =====

                    docker ps --filter "name=%DEPLOY_APP_CONTAINER%" ^
                        --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" > app-running.txt

                    if errorlevel 1 (
                        echo ERROR: Cannot inspect application container.
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    findstr /i "^true$" app-running.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application container is NOT running.
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Application container is RUNNING.

                    echo.
                    echo ===== DATABASE CONTAINER =====

                    docker ps --filter "name=%DEPLOY_DB_CONTAINER%" ^
                        --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_DB_CONTAINER%" > db-running.txt

                    if errorlevel 1 (
                        echo ERROR: Cannot inspect database container.
                        docker logs "%DEPLOY_DB_CONTAINER%"
                        exit /b 1
                    )

                    findstr /i "^true$" db-running.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database container is NOT running.
                        docker logs "%DEPLOY_DB_CONTAINER%"
                        exit /b 1
                    )

                    echo Database container is RUNNING.

                    echo.
                    echo ==========================================
                    echo CONTAINER VALIDATION SUCCESSFUL
                    echo ==========================================
                '''
            }
        }

        stage('Validate Network') {
            steps {
                bat '''
                    echo ==========================================
                    echo VALIDATING DOCKER NETWORK
                    echo ==========================================

                    docker network inspect "%DEPLOY_NETWORK%" > network-inspect-final.json

                    if errorlevel 1 (
                        echo ERROR: Network inspection failed.
                        exit /b 1
                    )

                    echo.
                    echo Network:
                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{.Name}}"

                    echo.
                    echo Connected containers:
                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}} {{end}}"

                    echo.

                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}} {{end}}" ^
                        | findstr /i "%DEPLOY_APP_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not connected to expected network.
                        exit /b 1
                    )

                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}} {{end}}" ^
                        | findstr /i "%DEPLOY_DB_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not connected to expected network.
                        exit /b 1
                    )

                    echo Network validation successful.
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    echo ==========================================
                    echo HEALTH CHECK
                    echo ==========================================

                    timeout /t 5 /nobreak >nul

                    curl.exe -fsS ^
                        "http://localhost:%DEPLOY_HOST_PORT%/health" ^
                        -o health-response.json

                    if errorlevel 1 (
                        echo ERROR: Health endpoint failed.
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Health response:
                    type health-response.json

                    echo.
                    echo Health check PASSED.
                '''
            }
        }

        stage('Application To Database Connectivity') {
            steps {
                bat '''
                    echo ==========================================
                    echo APPLICATION TO DATABASE CONNECTIVITY
                    echo ==========================================

                    docker exec "%DEPLOY_APP_CONTAINER%" ^
                        python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); print('Database reachable from application:',h,p); s.close()"

                    if errorlevel 1 (
                        echo ERROR: Application cannot reach database.
                        echo.
                        echo Application logs:
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        echo.
                        echo Network:
                        docker network inspect "%DEPLOY_NETWORK%"
                        exit /b 1
                    )

                    echo.
                    echo Application successfully reaches database.
                '''
            }
        }

        stage('Environment Validation') {
            steps {
                bat '''
                    echo ==========================================
                    echo ENVIRONMENT VALIDATION
                    echo ==========================================

                    curl.exe -fsS ^
                        "http://localhost:%DEPLOY_HOST_PORT%/environment" ^
                        -o environment-response.json

                    if errorlevel 1 (
                        echo ERROR: Environment endpoint failed.
                        exit /b 1
                    )

                    echo Environment response:
                    type environment-response.json

                    echo.
                    echo Expected environment:
                    echo %ENVIRONMENT%

                    findstr /i "%ENVIRONMENT%" environment-response.json >nul

                    if errorlevel 1 (
                        echo ERROR: Environment does not match.
                        exit /b 1
                    )

                    echo Environment validation PASSED.
                '''
            }
        }

        stage('Version Validation') {
            steps {
                bat '''
                    echo ==========================================
                    echo VERSION VALIDATION
                    echo ==========================================

                    curl.exe -fsS ^
                        "http://localhost:%DEPLOY_HOST_PORT%/version" ^
                        -o version-response.json

                    if errorlevel 1 (
                        echo ERROR: Version endpoint failed.
                        exit /b 1
                    )

                    echo Version response:
                    type version-response.json

                    echo.
                    echo Expected version:
                    echo %DEPLOY_VERSION%

                    findstr /i "%DEPLOY_VERSION%" version-response.json >nul

                    if errorlevel 1 (
                        echo ERROR: Version does not match.
                        exit /b 1
                    )

                    echo Version validation PASSED.
                '''
            }
        }

        stage('Volume Inspection') {
            steps {
                bat '''
                    echo ==========================================
                    echo VOLUME INSPECTION
                    echo ==========================================

                    docker volume inspect "%DEPLOY_DB_VOLUME%" > volume-inspect-final.json

                    if errorlevel 1 (
                        echo ERROR: Volume inspection failed.
                        exit /b 1
                    )

                    echo.
                    echo Database volume:
                    docker volume inspect "%DEPLOY_DB_VOLUME%"

                    echo.
                    echo Application port:
                    docker port "%DEPLOY_APP_CONTAINER%"

                    echo.
                    echo Persistent storage validation PASSED.
                '''
            }
        }

        stage('Deployment Successful') {
            steps {
                bat '''
                    echo.
                    echo ============================================================
                    echo                 DEPLOYMENT SUCCESSFUL
                    echo ============================================================
                    echo.
                    echo Environment           : %ENVIRONMENT%
                    echo Action                : %ACTION%
                    echo Version               : %DEPLOY_VERSION%
                    echo Docker Image          : %DEPLOY_IMAGE%
                    echo Git Branch            : %DEPLOY_GIT_BRANCH%
                    echo Application Container : %DEPLOY_APP_CONTAINER%
                    echo Database Container    : %DEPLOY_DB_CONTAINER%
                    echo Network               : %DEPLOY_NETWORK%
                    echo Database Volume       : %DEPLOY_DB_VOLUME%
                    echo Host Port             : %DEPLOY_HOST_PORT%
                    echo Container Port        : %CONTAINER_PORT%
                    echo Application URL       : http://localhost:%DEPLOY_HOST_PORT%
                    echo.
                    echo ============================================================
                '''
            }
        }
    }

    post {

        always {

            echo 'Collecting deployment evidence...'

            bat '''
                echo ==========================================
                echo FINAL DOCKER STATUS
                echo ==========================================

                docker ps -a > evidence-docker-ps.txt

                type evidence-docker-ps.txt

                echo.
                echo ==========================================
                echo DOCKER IMAGES
                echo ==========================================

                docker images customer-app > evidence-docker-images.txt

                type evidence-docker-images.txt

                echo.
                echo ==========================================
                echo NETWORK
                echo ==========================================

                docker network inspect "%DEPLOY_NETWORK%" > evidence-network.txt 2>nul

                echo.
                echo ==========================================
                echo VOLUME
                echo ==========================================

                docker volume inspect "%DEPLOY_DB_VOLUME%" > evidence-volume.txt 2>nul

                echo.
                echo ==========================================
                echo PORT
                echo ==========================================

                docker port "%DEPLOY_APP_CONTAINER%" > evidence-port.txt 2>nul
            '''

            archiveArtifacts(
                artifacts: '''
                    previous-image.txt,
                    previous-version.txt,
                    image-inspect.json,
                    health-response.json,
                    environment-response.json,
                    version-response.json,
                    network-inspect-before.json,
                    network-inspect-final.json,
                    volume-inspect.json,
                    volume-inspect-final.json,
                    evidence-docker-ps.txt,
                    evidence-docker-images.txt,
                    evidence-network.txt,
                    evidence-volume.txt,
                    evidence-port.txt
                ''',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }

        success {
            echo '============================================================'
            echo 'PIPELINE COMPLETED SUCCESSFULLY'
            echo '============================================================'
        }

        failure {

            script {

                echo '============================================================'
                echo 'PIPELINE FAILED'
                echo '============================================================'

                echo "Environment : ${params.ENVIRONMENT}"
                echo "Action      : ${params.ACTION}"
                echo "Version     : ${params.VERSION}"

                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY' &&
                    env.PREVIOUS_IMAGE &&
                    env.PREVIOUS_IMAGE != 'NONE'
                ) {

                    echo 'Production deployment failed.'
                    echo 'Attempting automatic rollback.'

                    def rollbackImage = env.PREVIOUS_IMAGE
                    def rollbackVersion = env.PREVIOUS_VERSION

                    echo "Rollback Image   : ${rollbackImage}"
                    echo "Rollback Version : ${rollbackVersion}"

                    def credentialId = 'db-production'

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USERNAME_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            echo ==========================================
                            echo AUTOMATIC PRODUCTION ROLLBACK
                            echo ==========================================

                            docker image inspect "${rollbackImage}" >nul 2>&1

                            if errorlevel 1 (
                                echo ERROR: Previous image does not exist.
                                exit /b 1
                            )

                            docker rm -f "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                            docker run -d ^
                                --name "%DEPLOY_APP_CONTAINER%" ^
                                --network "%DEPLOY_NETWORK%" ^
                                --restart unless-stopped ^
                                -p "%DEPLOY_HOST_PORT%:%CONTAINER_PORT%" ^
                                -e APP_ENV="PRODUCTION" ^
                                -e APP_VERSION="${rollbackVersion}" ^
                                -e DB_HOST="%DEPLOY_DB_HOST%" ^
                                -e DB_PORT="5432" ^
                                -e DB_NAME="%DEPLOY_DB_NAME%" ^
                                -e DB_USER="%DB_USERNAME_SECRET%" ^
                                -e DB_PASSWORD="%DB_PASSWORD_SECRET%" ^
                                "${rollbackImage}"

                            if errorlevel 1 (
                                echo ERROR: Rollback container failed to start.
                                exit /b 1
                            )

                            timeout /t 5 /nobreak >nul

                            docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" > rollback-running.txt

                            findstr /i "^true$" rollback-running.txt >nul

                            if errorlevel 1 (
                                echo ERROR: Rolled back application is not running.
                                docker logs "%DEPLOY_APP_CONTAINER%"
                                exit /b 1
                            )

                            echo Rollback container is RUNNING.

                            curl.exe -fsS ^
                                "http://localhost:%DEPLOY_HOST_PORT%/health" ^
                                -o rollback-health.json

                            if errorlevel 1 (
                                echo ERROR: Rollback health check failed.
                                docker logs "%DEPLOY_APP_CONTAINER%"
                                exit /b 1
                            )

                            echo.
                            echo ============================================================
                            echo              PRODUCTION ROLLBACK SUCCESSFUL
                            echo ============================================================
                            echo Restored Image   : ${rollbackImage}
                            echo Restored Version : ${rollbackVersion}
                            echo ============================================================
                        """
                    }

                } else {

                    echo 'Automatic rollback was not required.'
                }
            }
        }
    }
}