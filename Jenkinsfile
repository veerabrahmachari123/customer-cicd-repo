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
            description: 'Target deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Docker image version/tag'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests before deployment'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Required YES for production deployment'
        )
    }

    environment {

        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'

        IMAGE_REPOSITORY = 'customer-app'

        CONTAINER_PORT = '8080'
    }

    stages {

        // ============================================================
        // 1. RESOLVE ENVIRONMENT CONFIGURATION
        // ============================================================

        stage('Resolve Configuration') {

            steps {

                script {

                    echo "=========================================="
                    echo "RESOLVING DEPLOYMENT CONFIGURATION"
                    echo "=========================================="

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

                    }
                    else if (params.ENVIRONMENT == 'UAT') {

                        env.DEPLOY_GIT_BRANCH = 'release'
                        env.DEPLOY_NETWORK = 'customer-uat-net'
                        env.DEPLOY_APP_CONTAINER = 'customer-app-uat'
                        env.DEPLOY_DB_CONTAINER = 'customer-db-uat'
                        env.DEPLOY_DB_VOLUME = 'customer-db-uat-data'
                        env.DEPLOY_DB_HOST = 'customer-db-uat'
                        env.DEPLOY_DB_NAME = 'customer_uat'
                        env.DEPLOY_DB_USER = 'customer_uat'
                        env.DEPLOY_HOST_PORT = '8082'

                    }
                    else {

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

                    echo "Environment       : ${params.ENVIRONMENT}"
                    echo "Action             : ${params.ACTION}"
                    echo "Version            : ${env.DEPLOY_VERSION}"
                    echo "Git Branch         : ${env.DEPLOY_GIT_BRANCH}"
                    echo "Network            : ${env.DEPLOY_NETWORK}"
                    echo "Application        : ${env.DEPLOY_APP_CONTAINER}"
                    echo "Database           : ${env.DEPLOY_DB_CONTAINER}"
                    echo "Database Volume    : ${env.DEPLOY_DB_VOLUME}"
                    echo "Database Host      : ${env.DEPLOY_DB_HOST}"
                    echo "Database Name      : ${env.DEPLOY_DB_NAME}"
                    echo "Database User      : ${env.DEPLOY_DB_USER}"
                    echo "Host Port          : ${env.DEPLOY_HOST_PORT}"
                    echo "Docker Image       : ${env.DEPLOY_IMAGE}"
                    echo "=========================================="
                }
            }
        }

        // ============================================================
        // 2. VALIDATE PARAMETERS
        // ============================================================

        stage('Validate Parameters') {

            steps {

                script {

                    if (!(params.VERSION ==~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/)) {

                        error(
                            "Invalid VERSION '${params.VERSION}'. " +
                            "Use only letters, numbers, dots, underscores and hyphens."
                        )
                    }

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRMATION != 'YES'
                    ) {

                        error(
                            "Production deployment requires " +
                            "PRODUCTION_CONFIRMATION = YES."
                        )
                    }

                    echo "Parameters validated successfully."
                }
            }
        }

        // ============================================================
        // 3. CHECK DOCKER
        // ============================================================

        stage('Check Docker') {

            steps {

                bat '''
                    echo ==========================================
                    echo DOCKER VERSION
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

        // ============================================================
        // 4. CHECKOUT CORRECT BRANCH
        // ============================================================

        stage('Checkout Source') {

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
                    echo CHECKED OUT SOURCE
                    echo ==========================================

                    git branch -a

                    git rev-parse HEAD

                    git log -1 --oneline

                    git status
                '''
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
                    echo ==========================================
                    echo RUNNING APPLICATION TESTS
                    echo ==========================================

                    docker run --rm ^
                        -v "%CD%:/workspace" ^
                        -w /workspace ^
                        python:3.12-slim ^
                        sh -c "pip install --no-cache-dir -q -r app/requirements.txt && pytest -q app/test_app.py"

                    if errorlevel 1 (
                        echo ERROR: Application tests failed.
                        exit /b 1
                    )

                    echo All application tests passed.
                '''
            }
        }

        // ============================================================
        // 6. CAPTURE PREVIOUS IMAGE
        // ============================================================

        stage('Capture Previous Image') {

            steps {

                bat '''
                    echo ==========================================
                    echo CAPTURING PREVIOUS APPLICATION IMAGE
                    echo ==========================================

                    if exist previous-image.txt del /q previous-image.txt
                    if exist previous-version.txt del /q previous-version.txt

                    docker inspect "%DEPLOY_APP_CONTAINER%" ^
                        --format="{{.Config.Image}}" ^
                        > previous-image.txt 2>nul

                    if exist previous-image.txt (

                        set /p PREVIOUS_IMAGE=<previous-image.txt

                        echo Previous Image: %PREVIOUS_IMAGE%

                        for /f "tokens=2 delims=:" %%A in ("%PREVIOUS_IMAGE%") do (
                            echo %%A>previous-version.txt
                        )

                    ) else (

                        echo No existing application container found.
                        echo NONE>previous-image.txt
                        echo NONE>previous-version.txt
                    )

                    echo.
                    echo Previous deployment information saved.
                '''
            }
        }

        // ============================================================
        // 7. CREATE NETWORK
        // ============================================================

        stage('Prepare Docker Network') {

            steps {

                bat '''
                    echo ==========================================
                    echo PREPARING DOCKER NETWORK
                    echo ==========================================

                    docker network inspect "%DEPLOY_NETWORK%" >nul 2>&1

                    if errorlevel 1 (

                        echo Creating network %DEPLOY_NETWORK%...

                        docker network create "%DEPLOY_NETWORK%"

                        if errorlevel 1 (
                            echo ERROR: Failed to create Docker network.
                            exit /b 1
                        )

                    ) else (

                        echo Network %DEPLOY_NETWORK% already exists.
                    )

                    docker network inspect "%DEPLOY_NETWORK%" > network-inspect-before.json

                    echo Network ready.
                '''
            }
        }

        // ============================================================
        // 8. CREATE DATABASE VOLUME
        // ============================================================

        stage('Prepare Database Volume') {

            steps {

                bat '''
                    echo ==========================================
                    echo PREPARING DATABASE VOLUME
                    echo ==========================================

                    docker volume inspect "%DEPLOY_DB_VOLUME%" >nul 2>&1

                    if errorlevel 1 (

                        echo Creating volume %DEPLOY_DB_VOLUME%...

                        docker volume create "%DEPLOY_DB_VOLUME%"

                        if errorlevel 1 (
                            echo ERROR: Failed to create database volume.
                            exit /b 1
                        )

                    ) else (

                        echo Volume %DEPLOY_DB_VOLUME% already exists.
                    )

                    docker volume inspect "%DEPLOY_DB_VOLUME%" > volume-inspect.json

                    echo Database volume ready.
                '''
            }
        }

        // ============================================================
        // 9. BUILD OR VERIFY IMAGE
        // ============================================================

        stage('Prepare Docker Image') {

            steps {

                script {

                    if (params.ACTION == 'DEPLOY') {

                        bat """
                            echo ==========================================
                            echo BUILDING APPLICATION IMAGE
                            echo ==========================================

                            docker build ^
                                --build-arg VERSION=${env.DEPLOY_VERSION} ^
                                -t ${env.DEPLOY_IMAGE} .

                            if errorlevel 1 (
                                echo ERROR: Docker image build failed.
                                exit /b 1
                            )

                            echo Image built successfully.
                        """
                    }
                    else {

                        bat """
                            echo ==========================================
                            echo CHECKING ROLLBACK IMAGE
                            echo ==========================================

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

        // ============================================================
        // 10. VERIFY IMAGE
        // ============================================================

        stage('Verify Docker Image') {

            steps {

                bat '''
                    echo ==========================================
                    echo VERIFYING DOCKER IMAGE
                    echo ==========================================

                    docker image inspect "%DEPLOY_IMAGE%"

                    if errorlevel 1 (
                        echo ERROR: Image verification failed.
                        exit /b 1
                    )

                    echo.
                    echo IMAGE TAG:
                    docker image inspect "%DEPLOY_IMAGE%" ^
                        --format="{{index .RepoTags 0}}"

                    echo.
                    echo APP VERSION:
                    docker image inspect "%DEPLOY_IMAGE%" ^
                        --format="{{.Config.Env}}" | findstr /i "APP_VERSION"

                    echo.
                    echo Docker image verified successfully.
                '''
            }
        }

        // ============================================================
        // 11. DEPLOY DATABASE
        // ============================================================

        stage('Deploy Database') {

            steps {

                script {

                    def credentialId = ''

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    }
                    else {
                        credentialId = 'db-production'
                    }

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USERNAME',
                            passwordVariable: 'DB_PASSWORD'
                        )
                    ]) {

                        bat """
                            echo ==========================================
                            echo DEPLOYING DATABASE
                            echo ==========================================

                            docker container inspect "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                            if errorlevel 1 (

                                echo Database container does not exist.
                                echo Creating PostgreSQL database...

                                docker run -d ^
                                    --name "%DEPLOY_DB_CONTAINER%" ^
                                    --network "%DEPLOY_NETWORK%" ^
                                    --restart unless-stopped ^
                                    -e POSTGRES_DB="%DEPLOY_DB_NAME%" ^
                                    -e POSTGRES_USER="%DB_USERNAME%" ^
                                    -e POSTGRES_PASSWORD="%DB_PASSWORD%" ^
                                    -v "%DEPLOY_DB_VOLUME%:/var/lib/postgresql/data" ^
                                    -v "%CD%/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                                    postgres:16

                                if errorlevel 1 (
                                    echo ERROR: Failed to create database container.
                                    exit /b 1
                                )

                            ) else (

                                echo Database container already exists.

                                docker start "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                                echo Ensuring database is connected to network...

                                docker network connect "%DEPLOY_NETWORK%" "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                                if errorlevel 1 (
                                    echo Database was already connected to the network.
                                )
                            )

                            echo.
                            echo Database container:
                            docker ps --filter "name=%DEPLOY_DB_CONTAINER%"

                            echo.
                            echo Database deployment complete.
                        """
                    }
                }
            }
        }

        // ============================================================
        // 12. WAIT FOR DATABASE
        // ============================================================

        stage('Wait For Database') {

            steps {

                script {

                    timeout(time: 120, unit: 'SECONDS') {

                        waitUntil {

                            def status = bat(
                                script: '''
                                    docker exec "%DEPLOY_DB_CONTAINER%" pg_isready -U "%DEPLOY_DB_USER%" -d "%DEPLOY_DB_NAME%"
                                ''',
                                returnStatus: true
                            )

                            if (status == 0) {

                                echo "PostgreSQL is accepting connections."

                                return true
                            }

                            echo "Waiting for PostgreSQL..."

                            sleep(time: 5, unit: 'SECONDS')

                            return false
                        }
                    }
                }
            }
        }

        // ============================================================
        // 13. DEPLOY APPLICATION
        // ============================================================

        stage('Deploy Application') {

            steps {

                script {

                    def credentialId = ''

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    }
                    else {
                        credentialId = 'db-production'
                    }

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USERNAME',
                            passwordVariable: 'DB_PASSWORD'
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
                                -e DB_USER="%DB_USERNAME%" ^
                                -e DB_PASSWORD="%DB_PASSWORD%" ^
                                "%DEPLOY_IMAGE%"

                            if errorlevel 1 (
                                echo ERROR: Application container failed to start.
                                exit /b 1
                            )

                            echo.
                            echo Application container started.

                            docker ps --filter "name=%DEPLOY_APP_CONTAINER%"
                        """
                    }
                }
            }
        }

        // ============================================================
        // 14. VALIDATE CONTAINERS
        // ============================================================

        stage('Validate Containers') {

            steps {

                bat '''
                    echo ==========================================
                    echo VALIDATING APPLICATION CONTAINER
                    echo ==========================================

                    docker ps --filter "name=%DEPLOY_APP_CONTAINER%" ^
                        --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    echo.
                    echo Checking application container...

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" ^
                        | findstr /i "^true$" >nul

                    if errorlevel 1 (

                        echo ERROR: Application container is not running.

                        docker logs "%DEPLOY_APP_CONTAINER%"

                        exit /b 1
                    )

                    echo Application container is RUNNING.

                    echo.
                    echo ==========================================
                    echo VALIDATING DATABASE CONTAINER
                    echo ==========================================

                    docker ps --filter "name=%DEPLOY_DB_CONTAINER%" ^
                        --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    echo.
                    echo Checking database container...

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_DB_CONTAINER%" ^
                        | findstr /i "^true$" >nul

                    if errorlevel 1 (

                        echo ERROR: Database container is not running.

                        docker logs "%DEPLOY_DB_CONTAINER%"

                        exit /b 1
                    )

                    echo Database container is RUNNING.

                    echo.
                    echo Both containers are RUNNING.
                '''
            }
        }

        // ============================================================
        // 15. VALIDATE NETWORK
        // ============================================================

        stage('Validate Network') {

            steps {

                bat '''
                    echo ==========================================
                    echo VALIDATING DOCKER NETWORK
                    echo ==========================================

                    docker network inspect "%DEPLOY_NETWORK%" > network-inspect.json

                    if errorlevel 1 (
                        echo ERROR: Docker network inspection failed.
                        exit /b 1
                    )

                    echo.
                    echo Network:
                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{.Name}}"

                    echo.
                    echo Connected containers:

                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}}{{" "}}{{end}}"

                    echo.

                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}}{{" "}}{{end}}" ^
                        | findstr /i "%DEPLOY_APP_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not connected to expected network.
                        exit /b 1
                    )

                    docker network inspect "%DEPLOY_NETWORK%" ^
                        --format="{{range .Containers}}{{.Name}}{{" "}}{{end}}" ^
                        | findstr /i "%DEPLOY_DB_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not connected to expected network.
                        exit /b 1
                    )

                    echo.
                    echo Application and database are connected to:
                    echo %DEPLOY_NETWORK%
                '''
            }
        }

        // ============================================================
        // 16. HEALTH CHECK
        // ============================================================

        stage('Health Check') {

            steps {

                bat '''
                    echo ==========================================
                    echo APPLICATION HEALTH CHECK
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
                    echo Health endpoint succeeded.
                '''
            }
        }

        // ============================================================
        // 17. APP TO DATABASE CONNECTIVITY
        // ============================================================

        stage('Validate App Database Connectivity') {

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

        // ============================================================
        // 18. ENVIRONMENT VALIDATION
        // ============================================================

        stage('Validate Environment') {

            steps {

                bat '''
                    echo ==========================================
                    echo VALIDATING APPLICATION ENVIRONMENT
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
                '''
            }
        }

        // ============================================================
        // 19. VERSION VALIDATION
        // ============================================================

        stage('Validate Version') {

            steps {

                bat '''
                    echo ==========================================
                    echo VALIDATING DEPLOYED VERSION
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
                    echo Requested version:
                    echo %DEPLOY_VERSION%

                    findstr /i "%DEPLOY_VERSION%" version-response.json >nul

                    if errorlevel 1 (

                        echo ERROR: Deployed version does not match requested version.

                        exit /b 1
                    )

                    echo.
                    echo Version validation successful.
                '''
            }
        }

        // ============================================================
        // 20. VOLUME INSPECTION
        // ============================================================

        stage('Validate Persistent Storage') {

            steps {

                bat '''
                    echo ==========================================
                    echo VALIDATING PERSISTENT DATABASE STORAGE
                    echo ==========================================

                    docker volume inspect "%DEPLOY_DB_VOLUME%" ^
                        > volume-inspect-final.json

                    if errorlevel 1 (
                        echo ERROR: Volume inspection failed.
                        exit /b 1
                    )

                    echo Database volume:
                    docker volume inspect "%DEPLOY_DB_VOLUME%"

                    echo.
                    echo Application port mapping:
                    docker port "%DEPLOY_APP_CONTAINER%"

                    echo.
                    echo Persistent storage validation complete.
                '''
            }
        }

        // ============================================================
        // 21. FINAL DEPLOYMENT INFORMATION
        // ============================================================

        stage('Deployment Successful') {

            steps {

                bat '''
                    echo.
                    echo ==================================================
                    echo              DEPLOYMENT SUCCESSFUL
                    echo ==================================================
                    echo.
                    echo Environment       : %ENVIRONMENT%
                    echo Action             : %ACTION%
                    echo Version            : %DEPLOY_VERSION%
                    echo Image              : %DEPLOY_IMAGE%
                    echo Git Branch         : %DEPLOY_GIT_BRANCH%
                    echo Application        : %DEPLOY_APP_CONTAINER%
                    echo Database           : %DEPLOY_DB_CONTAINER%
                    echo Network            : %DEPLOY_NETWORK%
                    echo Database Volume    : %DEPLOY_DB_VOLUME%
                    echo Host Port          : %DEPLOY_HOST_PORT%
                    echo Application URL     : http://localhost:%DEPLOY_HOST_PORT%
                    echo.
                    echo ==================================================
                '''
            }
        }
    }

    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        always {

            echo "Collecting deployment evidence..."

            bat '''
                echo ==========================================
                echo FINAL DOCKER STATUS
                echo ==========================================

                docker ps -a

                echo.
                echo ==========================================
                echo FINAL DOCKER IMAGES
                echo ==========================================

                docker images customer-app

                echo.
                echo ==========================================
                echo NETWORK
                echo ==========================================

                docker network inspect "%DEPLOY_NETWORK%" > network-inspect-final.json 2>nul

                echo.
                echo ==========================================
                echo DATABASE VOLUME
                echo ==========================================

                docker volume inspect "%DEPLOY_DB_VOLUME%" > volume-inspect-final.json 2>nul
            '''

            archiveArtifacts(
                artifacts: '''
                    previous-image.txt,
                    previous-version.txt,
                    health-response.json,
                    environment-response.json,
                    version-response.json,
                    network-inspect-before.json,
                    network-inspect-final.json,
                    volume-inspect.json,
                    volume-inspect-final.json
                ''',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }

        success {

            echo "=================================================="
            echo "JENKINS DEPLOYMENT COMPLETED SUCCESSFULLY"
            echo "=================================================="
        }

        failure {

            script {

                echo "=================================================="
                echo "JENKINS DEPLOYMENT FAILED"
                echo "=================================================="

                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY'
                ) {

                    echo "Production deployment failed."

                    bat '''
                        echo Checking previous production image...

                        if not exist previous-image.txt (
                            echo No previous image information available.
                            exit /b 0
                        )

                        set /p PREVIOUS_IMAGE=<previous-image.txt

                        if "%PREVIOUS_IMAGE%"=="NONE" (
                            echo No previous production image available.
                            exit /b 0
                        )

                        echo Previous production image:
                        echo %PREVIOUS_IMAGE%

                        docker image inspect "%PREVIOUS_IMAGE%" >nul 2>&1

                        if errorlevel 1 (
                            echo Previous production image does not exist locally.
                            exit /b 0
                        )

                        echo.
                        echo ==========================================
                        echo AUTOMATIC PRODUCTION ROLLBACK
                        echo ==========================================

                        docker rm -f "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                        docker run -d ^
                            --name "%DEPLOY_APP_CONTAINER%" ^
                            --network "%DEPLOY_NETWORK%" ^
                            --restart unless-stopped ^
                            -p "%DEPLOY_HOST_PORT%:%CONTAINER_PORT%" ^
                            -e APP_ENV="%ENVIRONMENT%" ^
                            -e APP_VERSION="%PREVIOUS_IMAGE%" ^
                            -e DB_HOST="%DEPLOY_DB_HOST%" ^
                            -e DB_PORT="5432" ^
                            -e DB_NAME="%DEPLOY_DB_NAME%" ^
                            -e DB_USER="%DEPLOY_DB_USER%" ^
                            "%PREVIOUS_IMAGE%"

                        if errorlevel 1 (
                            echo ERROR: Automatic rollback container failed to start.
                            exit /b 1
                        )

                        timeout /t 5 /nobreak >nul

                        docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" ^
                            | findstr /i "^true$" >nul

                        if errorlevel 1 (
                            echo ERROR: Rolled back application is not running.
                            docker logs "%DEPLOY_APP_CONTAINER%"
                            exit /b 1
                        )

                        echo.
                        echo Production rollback container is RUNNING.

                        curl.exe -fsS ^
                            "http://localhost:%DEPLOY_HOST_PORT%/health" ^
                            -o rollback-health.json

                        if errorlevel 1 (
                            echo ERROR: Rollback health check failed.
                            docker logs "%DEPLOY_APP_CONTAINER%"
                            exit /b 1
                        )

                        echo.
                        echo ==========================================
                        echo PRODUCTION ROLLBACK SUCCESSFUL
                        echo ==========================================

                        echo Previous image restored:
                        echo %PREVIOUS_IMAGE%
                    '''
                }
                else {

                    echo "Automatic rollback is not required for this environment."
                }
            }
        }
    }
}