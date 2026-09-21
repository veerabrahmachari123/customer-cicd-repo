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
            description: 'Application version, for example 5.0 or 5.1'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Required for PRODUCTION'
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

                    } else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.DEPLOY_GIT_BRANCH = 'main'
                        env.DEPLOY_NETWORK = 'customer-prod-net'
                        env.DEPLOY_APP_CONTAINER = 'customer-app-prod'
                        env.DEPLOY_DB_CONTAINER = 'customer-db-prod'
                        env.DEPLOY_DB_VOLUME = 'customer-db-prod-data'
                        env.DEPLOY_DB_HOST = 'customer-db-prod'
                        env.DEPLOY_DB_NAME = 'customer_prod'
                        env.DEPLOY_DB_USER = 'customer_prod'
                        env.DEPLOY_HOST_PORT = '8083'

                    } else {
                        error("Invalid environment: ${params.ENVIRONMENT}")
                    }

                    env.DEPLOY_VERSION = params.VERSION.trim()
                    env.DEPLOY_IMAGE = "${env.IMAGE_REPOSITORY}:${env.DEPLOY_VERSION}"

                    echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================
Environment           : ${params.ENVIRONMENT}
Action                : ${params.ACTION}
Version               : ${env.DEPLOY_VERSION}
Git Branch            : ${env.DEPLOY_GIT_BRANCH}
Network               : ${env.DEPLOY_NETWORK}
Application Container : ${env.DEPLOY_APP_CONTAINER}
Database Container    : ${env.DEPLOY_DB_CONTAINER}
Database Volume       : ${env.DEPLOY_DB_VOLUME}
Database Host         : ${env.DEPLOY_DB_HOST}
Database Name         : ${env.DEPLOY_DB_NAME}
Database User         : ${env.DEPLOY_DB_USER}
Host Port             : ${env.DEPLOY_HOST_PORT}
Container Port        : ${env.CONTAINER_PORT}
Docker Image          : ${env.DEPLOY_IMAGE}
Run Tests             : ${params.RUN_TESTS}
============================================================
"""
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {

                    def version = params.VERSION.trim()

                    if (!version) {
                        error('VERSION cannot be empty.')
                    }

                    if (!(version ==~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/)) {
                        error(
                            "Invalid VERSION '${version}'. " +
                            "Use values such as 5.0 or 5.1."
                        )
                    }

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRMATION != 'YES') {

                        error(
                            'PRODUCTION requires PRODUCTION_CONFIRMATION=YES.'
                        )
                    }

                    echo "Environment validated: ${params.ENVIRONMENT}"
                    echo "Action validated: ${params.ACTION}"
                    echo "Version validated: ${version}"
                    echo "Git branch validated: ${env.DEPLOY_GIT_BRANCH}"
                }
            }
        }

        stage('Check Docker') {
            steps {
                bat '''
                    @echo off
                    docker version

                    if errorlevel 1 (
                        echo Docker is not available.
                        exit /b 1
                    )

                    echo Docker is available.
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                script {

                    echo "Checking out branch: ${env.DEPLOY_GIT_BRANCH}"

                    checkout([
                        $class: 'GitSCM',
                        branches: [
                            [name: "*/${env.DEPLOY_GIT_BRANCH}"]
                        ],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        userRemoteConfigs: [
                            [url: env.REPO_URL]
                        ]
                    ])

                    bat '''
                        @echo off

                        echo ===== CURRENT BRANCH =====
                        git branch --show-current

                        echo.
                        echo ===== LAST COMMIT =====
                        git log -1 --oneline

                        echo.
                        echo ===== STATUS =====
                        git status --short --branch
                    '''
                }
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
                    @echo off

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

        stage('Capture Previous Deployment') {
            steps {
                script {

                    env.PREVIOUS_IMAGE = ''
                    env.PREVIOUS_VERSION = ''
                    env.DEPLOY_STARTED = 'false'

                    int result = bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker inspect ${env.DEPLOY_APP_CONTAINER} --format="{{.Config.Image}}" > previous-image.txt
                        """
                    )

                    if (result == 0) {

                        env.PREVIOUS_IMAGE =
                            readFile('previous-image.txt').trim()

                        if (env.PREVIOUS_IMAGE) {

                            int colon =
                                env.PREVIOUS_IMAGE.lastIndexOf(':')

                            if (colon >= 0) {
                                env.PREVIOUS_VERSION =
                                    env.PREVIOUS_IMAGE.substring(colon + 1)
                            }

                            echo """
Previous Image   : ${env.PREVIOUS_IMAGE}
Previous Version : ${env.PREVIOUS_VERSION}
"""
                        }

                    } else {

                        echo 'No previous application container found.'
                    }
                }
            }
        }

        stage('Prepare Docker Network') {
            steps {
                script {

                    int result = bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker network inspect ${env.DEPLOY_NETWORK} >nul 2>&1
                        """
                    )

                    if (result != 0) {

                        echo "Creating network ${env.DEPLOY_NETWORK}"

                        bat """
                            @echo off
                            docker network create ${env.DEPLOY_NETWORK}

                            if errorlevel 1 (
                                echo Failed to create Docker network.
                                exit /b 1
                            )
                        """

                    } else {

                        echo "Network already exists: ${env.DEPLOY_NETWORK}"
                    }
                }
            }
        }

        stage('Prepare Database Volume') {
            steps {
                script {

                    int result = bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker volume inspect ${env.DEPLOY_DB_VOLUME} >nul 2>&1
                        """
                    )

                    if (result != 0) {

                        echo "Creating volume ${env.DEPLOY_DB_VOLUME}"

                        bat """
                            @echo off
                            docker volume create ${env.DEPLOY_DB_VOLUME}

                            if errorlevel 1 (
                                echo Failed to create database volume.
                                exit /b 1
                            )
                        """

                    } else {

                        echo "Volume already exists: ${env.DEPLOY_DB_VOLUME}"
                    }
                }
            }
        }

        stage('Prepare Target Image') {
            steps {
                script {

                    if (params.ACTION == 'DEPLOY') {

                        echo "Building ${env.DEPLOY_IMAGE}"

                        bat """
                            @echo off

                            docker build ^
                              --build-arg VERSION=${env.DEPLOY_VERSION} ^
                              -t ${env.DEPLOY_IMAGE} .

                            if errorlevel 1 (
                                echo Docker build FAILED.
                                exit /b 1
                            )
                        """

                    } else {

                        echo "Rollback requested."
                        echo "Checking ${env.DEPLOY_IMAGE}"

                        int result = bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker image inspect ${env.DEPLOY_IMAGE} >nul 2>&1
                            """
                        )

                        if (result != 0) {

                            error(
                                "Rollback image ${env.DEPLOY_IMAGE} does not exist."
                            )
                        }

                        echo "Rollback image found."
                    }
                }
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat """
                    @echo off

                    docker image inspect ${env.DEPLOY_IMAGE}

                    if errorlevel 1 (
                        echo Image verification FAILED.
                        exit /b 1
                    )

                    echo.
                    echo Docker image verified successfully:
                    echo ${env.DEPLOY_IMAGE}

                    echo.
                    echo ===== DOCKER IMAGES =====
                    docker images ${env.IMAGE_REPOSITORY}
                """
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

                    int exists = bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker inspect ${env.DEPLOY_DB_CONTAINER} >nul 2>&1
                        """
                    )

                    if (exists != 0) {

                        echo "Creating database container..."

                        withCredentials([
                            usernamePassword(
                                credentialsId: credentialId,
                                usernameVariable: 'DB_USER_SECRET',
                                passwordVariable: 'DB_PASSWORD_SECRET'
                            )
                        ]) {

                            bat """
                                @echo off

                                docker run -d ^
                                  --name ${env.DEPLOY_DB_CONTAINER} ^
                                  --network ${env.DEPLOY_NETWORK} ^
                                  --restart unless-stopped ^
                                  -e POSTGRES_DB=${env.DEPLOY_DB_NAME} ^
                                  -e POSTGRES_USER=%DB_USER_SECRET% ^
                                  -e POSTGRES_PASSWORD=%DB_PASSWORD_SECRET% ^
                                  -v ${env.DEPLOY_DB_VOLUME}:/var/lib/postgresql/data ^
                                  -v "%CD%\\\\db\\\\init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                                  postgres:16

                                if errorlevel 1 (
                                    echo Database deployment FAILED.
                                    exit /b 1
                                )
                            """
                        }

                    } else {

                        echo "Database container already exists."

                        int running = bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker inspect ${env.DEPLOY_DB_CONTAINER} --format="{{.State.Running}}" | findstr /I "true" >nul
                            """
                        )

                        if (running != 0) {

                            bat """
                                @echo off
                                docker start ${env.DEPLOY_DB_CONTAINER}

                                if errorlevel 1 exit /b 1
                            """
                        }

                        echo "Ensuring database is connected to expected network."

                        bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker network connect ${env.DEPLOY_NETWORK} ${env.DEPLOY_DB_CONTAINER}
                            """
                        )
                    }

                    echo "Database ready: ${env.DEPLOY_DB_CONTAINER}"
                }
            }
        }

        stage('Wait For Database') {
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

                    int ready = 1

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        for (int attempt = 1; attempt <= 30; attempt++) {

                            ready = bat(
                                returnStatus: true,
                                script: """
                                    @echo off

                                    docker exec ${env.DEPLOY_DB_CONTAINER} ^
                                      pg_isready ^
                                      -U %DB_USER_SECRET% ^
                                      -d ${env.DEPLOY_DB_NAME}
                                """
                            )

                            if (ready == 0) {

                                echo 'Database is READY.'
                                break
                            }

                            echo "Database not ready. Attempt ${attempt}/30"
                            sleep time: 2, unit: 'SECONDS'
                        }
                    }

                    if (ready != 0) {

                        error(
                            "Database ${env.DEPLOY_DB_CONTAINER} did not become ready."
                        )
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

                    env.DEPLOY_STARTED = 'true'

                    echo "Deploying application..."

                    bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker rm -f ${env.DEPLOY_APP_CONTAINER} >nul 2>&1
                        """
                    )

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat """
                            @echo off

                            docker run -d ^
                              --name ${env.DEPLOY_APP_CONTAINER} ^
                              --network ${env.DEPLOY_NETWORK} ^
                              --restart unless-stopped ^
                              -p ${env.DEPLOY_HOST_PORT}:${env.CONTAINER_PORT} ^
                              -e ENVIRONMENT=${params.ENVIRONMENT} ^
                              -e APP_VERSION=${env.DEPLOY_VERSION} ^
                              -e DB_HOST=${env.DEPLOY_DB_HOST} ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=${env.DEPLOY_DB_NAME} ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              ${env.DEPLOY_IMAGE}

                            if errorlevel 1 (
                                echo Application deployment FAILED.
                                exit /b 1
                            )
                        """
                    }

                    echo "Application started: ${env.DEPLOY_APP_CONTAINER}"
                }
            }
        }

        stage('Validate Containers') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$app=(docker inspect -f '{{.State.Running}}' '${env.DEPLOY_APP_CONTAINER}'); ^
                     \$db=(docker inspect -f '{{.State.Running}}' '${env.DEPLOY_DB_CONTAINER}'); ^
                     if(\$app -ne 'true'){Write-Error 'Application container is not running';exit 1}; ^
                     if(\$db -ne 'true'){Write-Error 'Database container is not running';exit 1}; ^
                     Write-Host 'Application: RUNNING'; ^
                     Write-Host 'Database: RUNNING'"

                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===== RUNNING CONTAINERS =====
                    docker ps
                """
            }
        }

        stage('Validate Network') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$n=(docker network inspect '${env.DEPLOY_NETWORK}' | ConvertFrom-Json)[0]; ^
                     \$names=@(\$n.Containers.PSObject.Properties | ForEach-Object { \$_.Value.Name }); ^
                     if(\$names -notcontains '${env.DEPLOY_APP_CONTAINER}'){Write-Error 'Application is not on expected network';exit 1}; ^
                     if(\$names -notcontains '${env.DEPLOY_DB_CONTAINER}'){Write-Error 'Database is not on expected network';exit 1}; ^
                     Write-Host 'Network validation successful'; ^
                     Write-Host 'Network: ${env.DEPLOY_NETWORK}'; ^
                     \$names"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Health Check') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:${env.DEPLOY_HOST_PORT}/health' -TimeoutSec 15; ^
                     if(\$r.StatusCode -ne 200){Write-Error 'Health check failed';exit 1}; ^
                     Write-Host 'HTTP Status:' \$r.StatusCode; ^
                     Write-Host 'Response:' \$r.Content"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Application To Database Connectivity') {
            steps {
                bat """
                    @echo off

                    docker exec ${env.DEPLOY_APP_CONTAINER} python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); s.close(); print('DATABASE CONNECTIVITY SUCCESS:',h,p)"

                    if errorlevel 1 (
                        echo Application to database connectivity FAILED.
                        exit /b 1
                    )
                """
            }
        }

        stage('Environment Validation') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.DEPLOY_HOST_PORT}/environment' -TimeoutSec 15; ^
                     Write-Host 'Expected:' '${params.ENVIRONMENT}'; ^
                     Write-Host 'Actual  :' \$r.environment; ^
                     if(\$r.environment -ne '${params.ENVIRONMENT}'){Write-Error 'Environment mismatch';exit 1}"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Version Validation') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.DEPLOY_HOST_PORT}/version' -TimeoutSec 15; ^
                     Write-Host 'Expected:' '${env.DEPLOY_VERSION}'; ^
                     Write-Host 'Actual  :' \$r.version; ^
                     if([string]\$r.version -ne '${env.DEPLOY_VERSION}'){Write-Error 'Version mismatch';exit 1}"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Volume Inspection') {
            steps {
                bat """
                    @echo off

                    echo ===== DATABASE VOLUME =====
                    docker volume inspect ${env.DEPLOY_DB_VOLUME}

                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===== PORT MAPPING =====
                    docker port ${env.DEPLOY_APP_CONTAINER}

                    echo.
                    echo Expected:
                    echo Host Port      : ${env.DEPLOY_HOST_PORT}
                    echo Container Port : ${env.CONTAINER_PORT}
                """
            }
        }

        stage('Deployment Successful') {
            steps {
                echo """
============================================================
DEPLOYMENT SUCCESSFUL
============================================================
Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${env.DEPLOY_VERSION}
Branch      : ${env.DEPLOY_GIT_BRANCH}
Application : ${env.DEPLOY_APP_CONTAINER}
Database    : ${env.DEPLOY_DB_CONTAINER}
Network     : ${env.DEPLOY_NETWORK}
Volume      : ${env.DEPLOY_DB_VOLUME}
Host Port   : ${env.DEPLOY_HOST_PORT}
Image       : ${env.DEPLOY_IMAGE}
============================================================
FINAL RESULT = SUCCESS
============================================================
"""
            }
        }
    }

    post {

        always {
            script {

                echo 'Collecting deployment evidence...'

                bat(
                    returnStatus: true,
                    script: """
                        @echo off

                        docker ps -a > evidence-docker-ps.txt

                        docker network inspect ${env.DEPLOY_NETWORK} > evidence-network.txt

                        docker volume inspect ${env.DEPLOY_DB_VOLUME} > evidence-volume.txt

                        docker images ${env.IMAGE_REPOSITORY} > evidence-docker-images.txt

                        docker port ${env.DEPLOY_APP_CONTAINER} > evidence-port.txt
                    """
                )

                archiveArtifacts(
                    artifacts: 'evidence-*.txt,previous-image.txt',
                    allowEmptyArchive: true,
                    fingerprint: true
                )
            }
        }

        success {
            echo 'Jenkins pipeline completed successfully.'
        }

        failure {
            script {

                echo """
============================================================
PIPELINE FAILED
============================================================
Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${params.VERSION}
============================================================
"""

                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY' &&
                    env.DEPLOY_STARTED == 'true' &&
                    env.PREVIOUS_IMAGE?.trim()
                ) {

                    echo """
============================================================
STARTING AUTOMATIC PRODUCTION ROLLBACK
============================================================
Previous Image   : ${env.PREVIOUS_IMAGE}
Previous Version : ${env.PREVIOUS_VERSION}
============================================================
"""

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'db-production',
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker rm -f ${env.DEPLOY_APP_CONTAINER} >nul 2>&1
                            """
                        )

                        bat """
                            @echo off

                            docker run -d ^
                              --name ${env.DEPLOY_APP_CONTAINER} ^
                              --network ${env.DEPLOY_NETWORK} ^
                              --restart unless-stopped ^
                              -p ${env.DEPLOY_HOST_PORT}:${env.CONTAINER_PORT} ^
                              -e ENVIRONMENT=PRODUCTION ^
                              -e APP_VERSION=${env.PREVIOUS_VERSION} ^
                              -e DB_HOST=${env.DEPLOY_DB_HOST} ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=${env.DEPLOY_DB_NAME} ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              ${env.PREVIOUS_IMAGE}

                            if errorlevel 1 (
                                echo ROLLBACK FAILED.
                                exit /b 1
                            )
                        """
                    }

                    sleep time: 5, unit: 'SECONDS'

                    int health = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                            "\$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:${env.DEPLOY_HOST_PORT}/health' -TimeoutSec 15; ^
                             if(\$r.StatusCode -ne 200){exit 1}; ^
                             Write-Host \$r.Content"
                        """
                    )

                    int version = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                            "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.DEPLOY_HOST_PORT}/version' -TimeoutSec 15; ^
                             Write-Host 'Rollback version:' \$r.version; ^
                             if([string]\$r.version -ne '${env.PREVIOUS_VERSION}'){exit 1}"
                        """
                    )

                    int database = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            docker exec ${env.DEPLOY_APP_CONTAINER} python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); s.close(); print('ROLLBACK DATABASE CONNECTIVITY SUCCESS:',h,p)"
                        """
                    )

                    if (
                        health == 0 &&
                        version == 0 &&
                        database == 0
                    ) {

                        echo """
============================================================
ROLLBACK SUCCESSFUL
============================================================
Restored Image   : ${env.PREVIOUS_IMAGE}
Restored Version : ${env.PREVIOUS_VERSION}
Environment      : PRODUCTION
============================================================
FINAL RESULT = ROLLBACK
============================================================
"""

                    } else {

                        echo """
============================================================
ROLLBACK VALIDATION FAILED
============================================================
Health Result   : ${health}
Version Result  : ${version}
Database Result : ${database}
============================================================
"""
                    }

                } else {

                    echo 'Automatic rollback was not required.'
                }
            }
        }
    }
}