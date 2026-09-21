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
            description: 'Deploy a new version or rollback to an existing image'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Application version/image tag, for example 5.0 or 5.1'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run automated application tests'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Must be YES for any PRODUCTION deployment'
        )
    }

    environment {
        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'
        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'
    }

    stages {

        /*
         * ============================================================
         * RESOLVE CONFIGURATION
         * ============================================================
         */
        stage('Resolve Configuration') {
            steps {
                script {
                    env.DEPLOY_VERSION = params.VERSION.trim()
                    env.DEPLOY_IMAGE = "${env.IMAGE_REPOSITORY}:${env.DEPLOY_VERSION}"

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
                        env.DEPLOY_DB_CREDENTIAL_ID = 'db-dev'

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
                        env.DEPLOY_DB_CREDENTIAL_ID = 'db-uat'

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
                        env.DEPLOY_DB_CREDENTIAL_ID = 'db-production'
                    }

                    echo ''
                    echo '============================================================'
                    echo 'RESOLVED DEPLOYMENT CONFIGURATION'
                    echo '============================================================'
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
                    echo ''
                }
            }
        }

        /*
         * ============================================================
         * VALIDATE PARAMETERS
         * ============================================================
         */
        stage('Validate Parameters') {
            steps {
                script {

                    if (!(params.ENVIRONMENT in ['DEV', 'UAT', 'PRODUCTION'])) {
                        error("Invalid ENVIRONMENT: ${params.ENVIRONMENT}")
                    }

                    if (!(params.ACTION in ['DEPLOY', 'ROLLBACK'])) {
                        error("Invalid ACTION: ${params.ACTION}")
                    }

                    if (!(params.RUN_TESTS in ['YES', 'NO'])) {
                        error("Invalid RUN_TESTS value")
                    }

                    if (!(params.VERSION ==~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/)) {
                        error(
                            "Invalid VERSION '${params.VERSION}'. " +
                            "Use values such as 5.0, 5.1 or 5.0.1"
                        )
                    }

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.ACTION == 'DEPLOY' &&
                        params.PRODUCTION_CONFIRMATION != 'YES'
                    ) {
                        error(
                            'PRODUCTION deployment requires ' +
                            'PRODUCTION_CONFIRMATION=YES'
                        )
                    }

                    echo "Environment validated: ${params.ENVIRONMENT}"
                    echo "Action validated: ${params.ACTION}"
                    echo "Version validated: ${env.DEPLOY_VERSION}"
                    echo "Git branch validated: ${env.DEPLOY_GIT_BRANCH}"
                }
            }
        }

        /*
         * ============================================================
         * CHECK DOCKER
         * ============================================================
         */
        stage('Check Docker') {
            steps {
                bat '''
                    docker version
                    echo Docker is available.
                '''
            }
        }

        /*
         * ============================================================
         * CHECKOUT CORRECT BRANCH
         * ============================================================
         */
        stage('Checkout Correct Branch') {
            steps {
                script {
                    echo "Checking out branch: ${env.DEPLOY_GIT_BRANCH}"

                    checkout([
                        $class: 'GitSCM',
                        branches: [[
                            name: "*/${env.DEPLOY_GIT_BRANCH}"
                        ]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [
                            [$class: 'CleanBeforeCheckout']
                        ],
                        userRemoteConfigs: [[
                            url: env.REPO_URL
                        ]]
                    ])

                    bat '''
                        echo ===== CURRENT COMMIT =====
                        git rev-parse --short HEAD

                        echo.
                        echo ===== LAST COMMIT =====
                        git log -1 --oneline

                        echo.
                        echo ===== STATUS =====
                        git status --short
                    '''
                }
            }
        }

        /*
         * ============================================================
         * RUN TESTS
         * ============================================================
         */
        stage('Run Tests') {
            when {
                expression {
                    params.RUN_TESTS == 'YES'
                }
            }

            steps {
                bat '''
                    echo Running tests...

                    docker run --rm ^
                      -v "%CD%:/workspace" ^
                      -w /workspace ^
                      python:3.12-slim ^
                      sh -c "pip install --no-cache-dir -q -r app/requirements.txt && pytest -q app/test_app.py"

                    if errorlevel 1 (
                        echo Tests FAILED.
                        exit /b 1
                    )

                    echo Tests PASSED.
                '''
            }
        }

        /*
         * ============================================================
         * CAPTURE PREVIOUS DEPLOYMENT
         * ============================================================
         */
        stage('Capture Previous Deployment') {
            steps {
                script {

                    bat '''
                        if exist previous-image.txt del /f /q previous-image.txt
                        docker inspect %DEPLOY_APP_CONTAINER% --format="{{.Config.Image}}" > previous-image.txt 2>nul

                        if errorlevel 1 (
                            echo No previous application container found.
                        ) else (
                            echo Previous application image:
                            type previous-image.txt
                        )
                    '''

                    if (fileExists('previous-image.txt')) {
                        def previous = readFile('previous-image.txt').trim()

                        if (previous) {
                            env.PREVIOUS_IMAGE = previous

                            echo "Previous image detected: ${env.PREVIOUS_IMAGE}"

                            if (env.PREVIOUS_IMAGE.contains(':')) {
                                env.PREVIOUS_VERSION =
                                    env.PREVIOUS_IMAGE.substring(
                                        env.PREVIOUS_IMAGE.lastIndexOf(':') + 1
                                    )
                            }

                            echo "Previous version: ${env.PREVIOUS_VERSION ?: 'unknown'}"
                        }
                    }

                    if (!env.PREVIOUS_IMAGE) {
                        echo 'No previous deployment exists.'
                    }
                }
            }
        }

        /*
         * ============================================================
         * PREPARE DOCKER NETWORK
         * ============================================================
         */
        stage('Prepare Docker Network') {
            steps {
                script {

                    bat '''
                        docker network inspect %DEPLOY_NETWORK% >nul 2>&1

                        if errorlevel 1 (
                            echo Creating network %DEPLOY_NETWORK%
                            docker network create %DEPLOY_NETWORK%
                        ) else (
                            echo Network already exists: %DEPLOY_NETWORK%
                        )
                    '''
                }
            }
        }

        /*
         * ============================================================
         * PREPARE DATABASE VOLUME
         * ============================================================
         */
        stage('Prepare Database Volume') {
            steps {
                script {

                    bat '''
                        docker volume inspect %DEPLOY_DB_VOLUME% >nul 2>&1

                        if errorlevel 1 (
                            echo Creating volume %DEPLOY_DB_VOLUME%
                            docker volume create %DEPLOY_DB_VOLUME%
                        ) else (
                            echo Volume already exists: %DEPLOY_DB_VOLUME%
                        )
                    '''
                }
            }
        }

        /*
         * ============================================================
         * PREPARE TARGET IMAGE
         * ============================================================
         */
        stage('Prepare Target Image') {
            steps {
                script {

                    if (params.ACTION == 'DEPLOY') {

                        echo "Building ${env.DEPLOY_IMAGE}"

                        bat '''
                            docker build ^
                              --build-arg VERSION=%DEPLOY_VERSION% ^
                              -t %DEPLOY_IMAGE% ^
                              .
                        '''

                    } else {

                        echo "Rollback requested."
                        echo "Rollback image: ${env.DEPLOY_IMAGE}"

                        bat '''
                            docker image inspect %DEPLOY_IMAGE% >nul 2>&1

                            if errorlevel 1 (
                                echo Rollback image does not exist: %DEPLOY_IMAGE%
                                exit /b 1
                            )

                            echo Rollback image exists: %DEPLOY_IMAGE%
                        '''
                    }
                }
            }
        }

        /*
         * ============================================================
         * VERIFY DOCKER IMAGE
         * ============================================================
         */
        stage('Verify Docker Image') {
            steps {
                bat '''
                    docker image inspect %DEPLOY_IMAGE%

                    echo.
                    echo ===== DOCKER IMAGES =====

                    docker images %IMAGE_REPOSITORY%
                '''
            }
        }

        /*
         * ============================================================
         * DEPLOY DATABASE
         * ============================================================
         */
        stage('Deploy Database') {
            steps {
                script {

                    echo 'Creating database container...'

                    withCredentials([
                        usernamePassword(
                            credentialsId: env.DEPLOY_DB_CREDENTIAL_ID,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat '''
                            docker inspect %DEPLOY_DB_CONTAINER% >nul 2>&1

                            if errorlevel 1 (

                                docker run -d ^
                                  --name %DEPLOY_DB_CONTAINER% ^
                                  --network %DEPLOY_NETWORK% ^
                                  -e POSTGRES_DB=%DEPLOY_DB_NAME% ^
                                  -e POSTGRES_USER=%DB_USER_SECRET% ^
                                  -e POSTGRES_PASSWORD=%DB_PASSWORD_SECRET% ^
                                  -v %DEPLOY_DB_VOLUME%:/var/lib/postgresql/data ^
                                  -v "%CD%\\db\\init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                                  postgres:16

                            ) else (

                                echo Database container already exists.

                                docker start %DEPLOY_DB_CONTAINER% >nul 2>&1

                                docker network inspect %DEPLOY_NETWORK% ^
                                  --format="{{range .Containers}}{{.Name}}{{end}}" ^
                                  | findstr /i "%DEPLOY_DB_CONTAINER%" >nul

                                if errorlevel 1 (
                                    docker network connect %DEPLOY_NETWORK% %DEPLOY_DB_CONTAINER%
                                )
                            )
                        '''
                    }

                    echo "Database ready: ${env.DEPLOY_DB_CONTAINER}"
                }
            }
        }

        /*
         * ============================================================
         * WAIT FOR DATABASE
         * ============================================================
         */
        stage('Wait For Database') {
            steps {
                script {

                    withCredentials([
                        usernamePassword(
                            credentialsId: env.DEPLOY_DB_CREDENTIAL_ID,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat '''
                            set DB_READY=0

                            for /L %%i in (1,1,30) do (

                                docker exec %DEPLOY_DB_CONTAINER% ^
                                  pg_isready ^
                                  -U %DB_USER_SECRET% ^
                                  -d %DEPLOY_DB_NAME%

                                if not errorlevel 1 (
                                    echo Database is READY.
                                    set DB_READY=1
                                    goto :database_ready
                                )

                                echo Database not ready. Attempt %%i/30
                                timeout /t 2 /nobreak >nul
                            )

                            :database_ready

                            if "%DB_READY%"=="0" (
                                echo Database failed to become ready.
                                docker logs %DEPLOY_DB_CONTAINER%
                                exit /b 1
                            )
                        '''
                    }
                }
            }
        }

        /*
         * ============================================================
         * DEPLOY APPLICATION
         * ============================================================
         */
        stage('Deploy Application') {
            steps {
                script {

                    echo 'Deploying application...'

                    bat '''
                        docker rm -f %DEPLOY_APP_CONTAINER% >nul 2>&1
                    '''

                    withCredentials([
                        usernamePassword(
                            credentialsId: env.DEPLOY_DB_CREDENTIAL_ID,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat '''
                            docker run -d ^
                              --name %DEPLOY_APP_CONTAINER% ^
                              --network %DEPLOY_NETWORK% ^
                              -p %DEPLOY_HOST_PORT%:%CONTAINER_PORT% ^
                              -e APP_ENVIRONMENT=%ENVIRONMENT% ^
                              -e APP_VERSION=%DEPLOY_VERSION% ^
                              -e DB_HOST=%DEPLOY_DB_HOST% ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=%DEPLOY_DB_NAME% ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              %DEPLOY_IMAGE%
                        '''
                    }

                    env.DEPLOY_STARTED = 'true'

                    echo "Application started: ${env.DEPLOY_APP_CONTAINER}"
                }
            }
        }

        /*
         * ============================================================
         * VALIDATE CONTAINERS
         * ============================================================
         */
        stage('Validate Containers') {
            steps {
                bat '''
                    echo ===== APPLICATION CONTAINER =====

                    docker ps ^
                      --filter "name=%DEPLOY_APP_CONTAINER%" ^
                      --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    echo.
                    echo ===== DATABASE CONTAINER =====

                    docker ps ^
                      --filter "name=%DEPLOY_DB_CONTAINER%" ^
                      --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

                    echo.
                    echo ===== CONTAINER STATUS VALIDATION =====

                    powershell -NoProfile -Command "$appRunning = docker inspect -f '{{.State.Running}}' $env:DEPLOY_APP_CONTAINER; if ($appRunning -ne 'true') { Write-Error 'Application container is not running'; exit 1 }; $dbRunning = docker inspect -f '{{.State.Running}}' $env:DEPLOY_DB_CONTAINER; if ($dbRunning -ne 'true') { Write-Error 'Database container is not running'; exit 1 }; Write-Host 'Application and database containers are RUNNING.'"
                '''
            }
        }

        /*
         * ============================================================
         * VALIDATE NETWORK
         * ============================================================
         */
        stage('Validate Network') {
            steps {
                bat '''
                    echo ===== NETWORK INSPECTION =====

                    docker network inspect %DEPLOY_NETWORK%

                    echo.
                    echo ===== NETWORK MEMBERS =====

                    powershell -NoProfile -Command "$containers = docker network inspect $env:DEPLOY_NETWORK | ConvertFrom-Json; $containers[0].Containers.PSObject.Properties | ForEach-Object { $_.Value.Name }"

                    echo.
                    echo ===== NETWORK VALIDATION =====

                    powershell -NoProfile -Command "$containers = docker network inspect $env:DEPLOY_NETWORK | ConvertFrom-Json; $names = @($containers[0].Containers.PSObject.Properties | ForEach-Object { $_.Value.Name }); if ($names -notcontains $env:DEPLOY_APP_CONTAINER) { Write-Error 'Application is not connected to expected network'; exit 1 }; if ($names -notcontains $env:DEPLOY_DB_CONTAINER) { Write-Error 'Database is not connected to expected network'; exit 1 }; Write-Host 'Application and database are on the correct Docker network.'"
                '''
            }
        }

        /*
         * ============================================================
         * HEALTH CHECK
         * ============================================================
         */
        stage('Health Check') {
            steps {
                script {

                    bat '''
                        powershell -NoProfile -Command "$url = 'http://localhost:%DEPLOY_HOST_PORT%/health'; Write-Host ('Checking ' + $url); try { $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10; Write-Host ('HTTP Status: ' + $response.StatusCode); Write-Host $response.Content; if ($response.StatusCode -ne 200) { exit 1 } } catch { Write-Error ('Health check failed: ' + $_.Exception.Message); docker logs %DEPLOY_APP_CONTAINER%; exit 1 }"
                    '''
                }
            }
        }

        /*
         * ============================================================
         * APPLICATION TO DATABASE CONNECTIVITY
         * ============================================================
         */
        stage('Application To Database Connectivity') {
            steps {
                bat '''
                    echo Testing database connectivity from inside application container...

                    docker exec %DEPLOY_APP_CONTAINER% python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); print('DB_HOST='+h); print('DB_PORT='+str(p)); s=socket.create_connection((h,p),5); print('APPLICATION_TO_DATABASE_CONNECTIVITY=SUCCESS'); s.close()"

                    if errorlevel 1 (
                        echo Application cannot reach database.
                        docker logs %DEPLOY_APP_CONTAINER%
                        exit /b 1
                    )
                '''
            }
        }

        /*
         * ============================================================
         * ENVIRONMENT VALIDATION
         * ============================================================
         */
        stage('Environment Validation') {
            steps {
                bat '''
                    echo ===== ENVIRONMENT ENDPOINT =====

                    powershell -NoProfile -Command "$expected = '%ENVIRONMENT%'; $response = Invoke-RestMethod -Uri 'http://localhost:%DEPLOY_HOST_PORT%/environment' -TimeoutSec 10; $json = $response | ConvertTo-Json -Compress; Write-Host $json; $actual = $response.environment; if ($actual -ne $expected) { Write-Error ('Expected environment ' + $expected + ' but received ' + $actual); exit 1 }; Write-Host ('ENVIRONMENT VALIDATION=SUCCESS: ' + $actual)"
                '''
            }
        }

        /*
         * ============================================================
         * VERSION VALIDATION
         * ============================================================
         */
        stage('Version Validation') {
            steps {
                bat '''
                    echo ===== VERSION ENDPOINT =====

                    powershell -NoProfile -Command "$expected = '%DEPLOY_VERSION%'; $response = Invoke-RestMethod -Uri 'http://localhost:%DEPLOY_HOST_PORT%/version' -TimeoutSec 10; $json = $response | ConvertTo-Json -Compress; Write-Host $json; $actual = [string]$response.version; if ($actual -ne $expected) { Write-Error ('Expected version ' + $expected + ' but received ' + $actual); exit 1 }; Write-Host ('VERSION VALIDATION=SUCCESS: ' + $actual)"
                '''
            }
        }

        /*
         * ============================================================
         * VOLUME INSPECTION
         * ============================================================
         */
        stage('Volume Inspection') {
            steps {
                bat '''
                    echo ===== DATABASE VOLUME =====

                    docker volume inspect %DEPLOY_DB_VOLUME%

                    echo.
                    echo ===== APPLICATION PORT MAPPING =====

                    docker port %DEPLOY_APP_CONTAINER%

                    echo.
                    echo ===== DATABASE VOLUME VALIDATION =====

                    docker inspect %DEPLOY_DB_CONTAINER% --format="{{range .Mounts}}{{.Name}} -> {{.Destination}}{{println}}{{end}}"
                '''
            }
        }

        /*
         * ============================================================
         * DEPLOYMENT SUCCESSFUL
         * ============================================================
         */
        stage('Deployment Successful') {
            steps {
                script {

                    echo ''
                    echo '============================================================'
                    echo 'DEPLOYMENT SUCCESSFUL'
                    echo '============================================================'
                    echo "Environment           : ${params.ENVIRONMENT}"
                    echo "Action                : ${params.ACTION}"
                    echo "Version               : ${env.DEPLOY_VERSION}"
                    echo "Git Branch            : ${env.DEPLOY_GIT_BRANCH}"
                    echo "Application Container : ${env.DEPLOY_APP_CONTAINER}"
                    echo "Database Container    : ${env.DEPLOY_DB_CONTAINER}"
                    echo "Network               : ${env.DEPLOY_NETWORK}"
                    echo "Database Volume       : ${env.DEPLOY_DB_VOLUME}"
                    echo "Application URL       : http://localhost:${env.DEPLOY_HOST_PORT}"
                    echo 'Health URL            : /health'
                    echo 'Environment URL       : /environment'
                    echo 'Version URL           : /version'
                    echo '============================================================'
                    echo ''
                }
            }
        }
    }

    /*
     * ================================================================
     * POST ACTIONS
     * ================================================================
     */
    post {

        always {
            script {

                echo 'Collecting deployment evidence...'

                bat '''
                    docker images %IMAGE_REPOSITORY% > evidence-docker-images.txt 2>&1
                    docker ps -a > evidence-docker-ps.txt 2>&1
                    docker network inspect %DEPLOY_NETWORK% > evidence-network.txt 2>&1
                    docker volume inspect %DEPLOY_DB_VOLUME% > evidence-volume.txt 2>&1
                    docker port %DEPLOY_APP_CONTAINER% > evidence-port.txt 2>&1
                '''

                archiveArtifacts(
                    artifacts:
                        'evidence-*.txt,previous-image.txt',
                    allowEmptyArchive: true,
                    fingerprint: true
                )
            }
        }

        success {
            script {

                echo ''
                echo '============================================================'
                echo 'FINAL RESULT = SUCCESS'
                echo '============================================================'
                echo "Environment : ${params.ENVIRONMENT}"
                echo "Action      : ${params.ACTION}"
                echo "Version     : ${env.DEPLOY_VERSION}"
                echo '============================================================'
                echo ''
            }
        }

        failure {
            script {

                echo ''
                echo '============================================================'
                echo 'PIPELINE FAILED'
                echo '============================================================'
                echo "Environment : ${params.ENVIRONMENT}"
                echo "Action      : ${params.ACTION}"
                echo "Version     : ${env.DEPLOY_VERSION}"
                echo '============================================================'

                /*
                 * Automatic production rollback.
                 *
                 * Only attempted when:
                 * - environment is PRODUCTION
                 * - action is DEPLOY
                 * - application deployment actually started
                 * - a previous application image exists
                 */
                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY' &&
                    env.DEPLOY_STARTED == 'true' &&
                    env.PREVIOUS_IMAGE
                ) {

                    echo 'Production deployment failed.'
                    echo "Previous production image: ${env.PREVIOUS_IMAGE}"
                    echo 'Starting automatic rollback...'

                    try {

                        bat '''
                            echo Removing failed production application...
                            docker rm -f %DEPLOY_APP_CONTAINER% >nul 2>&1
                        '''

                        withCredentials([
                            usernamePassword(
                                credentialsId: env.DEPLOY_DB_CREDENTIAL_ID,
                                usernameVariable: 'DB_USER_SECRET',
                                passwordVariable: 'DB_PASSWORD_SECRET'
                            )
                        ]) {

                            bat '''
                                echo Restoring previous production image...

                                docker run -d ^
                                  --name %DEPLOY_APP_CONTAINER% ^
                                  --network %DEPLOY_NETWORK% ^
                                  -p %DEPLOY_HOST_PORT%:%CONTAINER_PORT% ^
                                  -e APP_ENVIRONMENT=%ENVIRONMENT% ^
                                  -e APP_VERSION=%PREVIOUS_VERSION% ^
                                  -e DB_HOST=%DEPLOY_DB_HOST% ^
                                  -e DB_PORT=5432 ^
                                  -e DB_NAME=%DEPLOY_DB_NAME% ^
                                  -e DB_USER=%DB_USER_SECRET% ^
                                  -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                                  %PREVIOUS_IMAGE%
                            '''
                        }

                        timeout /t 5 /nobreak >nul

                        bat '''
                            echo Validating rolled-back application...

                            powershell -NoProfile -Command "$url = 'http://localhost:%DEPLOY_HOST_PORT%/health'; try { $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10; Write-Host ('Rollback health HTTP status: ' + $r.StatusCode); if ($r.StatusCode -ne 200) { exit 1 } } catch { Write-Error ('Rollback health check failed: ' + $_.Exception.Message); exit 1 }"

                            powershell -NoProfile -Command "$expected = '%PREVIOUS_VERSION%'; $r = Invoke-RestMethod -Uri 'http://localhost:%DEPLOY_HOST_PORT%/version' -TimeoutSec 10; Write-Host ('Rollback version: ' + $r.version); if ([string]$r.version -ne $expected) { Write-Error ('Rollback version mismatch. Expected ' + $expected + ' but got ' + $r.version); exit 1 }"

                            docker exec %DEPLOY_APP_CONTAINER% python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); print('ROLLBACK_DATABASE_CONNECTIVITY=SUCCESS'); s.close()"
                        '''

                        echo ''
                        echo '============================================================'
                        echo 'FINAL RESULT = ROLLBACK'
                        echo '============================================================'
                        echo "Failed version   : ${env.DEPLOY_VERSION}"
                        echo "Restored version : ${env.PREVIOUS_VERSION}"
                        echo "Restored image   : ${env.PREVIOUS_IMAGE}"
                        echo 'Rollback health  : PASSED'
                        echo 'Rollback version : PASSED'
                        echo 'Database access  : PASSED'
                        echo '============================================================'
                        echo ''

                    } catch (rollbackError) {

                        echo ''
                        echo '============================================================'
                        echo 'ROLLBACK FAILED'
                        echo '============================================================'
                        echo "Rollback error: ${rollbackError}"
                        echo '============================================================'
                        echo ''

                    }

                } else {

                    echo 'Automatic rollback was not required.'
                }
            }
        }
    }
}