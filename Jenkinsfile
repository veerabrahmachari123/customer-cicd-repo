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
            description: 'Select deployment environment'
        )

        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'DEPLOY a new version or ROLLBACK to an existing image version'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Docker image version, for example 5.0 or 5.1'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests before deployment'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Must be YES for any PRODUCTION deployment or rollback'
        )
    }

    environment {
        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'
        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'

        GIT_BRANCH = ''
        NETWORK = ''
        APP_CONTAINER = ''
        DB_CONTAINER = ''
        DB_VOLUME = ''
        DB_HOST = ''
        DB_NAME = ''
        DB_USER = ''
        HOST_PORT = ''
        IMAGE = ''

        PREVIOUS_IMAGE = ''
        PREVIOUS_VERSION = ''
        DEPLOY_STARTED = 'false'
    }

    stages {

        stage('Resolve Configuration') {
            steps {
                script {

                    if (params.ENVIRONMENT == 'DEV') {

                        env.GIT_BRANCH = 'develop'
                        env.NETWORK = 'customer-dev-net'
                        env.APP_CONTAINER = 'customer-app-dev'
                        env.DB_CONTAINER = 'customer-db-dev'
                        env.DB_VOLUME = 'customer-db-dev-data'
                        env.DB_HOST = 'customer-db-dev'
                        env.DB_NAME = 'customer_dev'
                        env.DB_USER = 'customer_dev'
                        env.HOST_PORT = '8081'

                    } else if (params.ENVIRONMENT == 'UAT') {

                        env.GIT_BRANCH = 'release'
                        env.NETWORK = 'customer-uat-net'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.DB_VOLUME = 'customer-db-uat-data'
                        env.DB_HOST = 'customer-db-uat'
                        env.DB_NAME = 'customer_uat'
                        env.DB_USER = 'customer_uat'
                        env.HOST_PORT = '8082'

                    } else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.GIT_BRANCH = 'main'
                        env.NETWORK = 'customer-prod-net'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.DB_VOLUME = 'customer-db-prod-data'
                        env.DB_HOST = 'customer-db-prod'
                        env.DB_NAME = 'customer_prod'
                        env.DB_USER = 'customer_prod'
                        env.HOST_PORT = '8083'

                    } else {
                        error("Invalid environment: ${params.ENVIRONMENT}")
                    }

                    env.IMAGE = "${env.IMAGE_REPOSITORY}:${params.VERSION.trim()}"

                    echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================
Environment           : ${params.ENVIRONMENT}
Action                : ${params.ACTION}
Version               : ${params.VERSION.trim()}
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

        stage('Validate Parameters') {
            steps {
                script {

                    String version = params.VERSION.trim()

                    if (!version) {
                        error('VERSION cannot be empty.')
                    }

                    if (!(version ==~ /^[A-Za-z0-9][A-Za-z0-9_.-]*$/)) {
                        error("Invalid VERSION '${version}'. Use values such as 5.0 or 5.1.")
                    }

                    if (!(params.ENVIRONMENT in ['DEV', 'UAT', 'PRODUCTION'])) {
                        error("Invalid ENVIRONMENT: ${params.ENVIRONMENT}")
                    }

                    if (!(params.ACTION in ['DEPLOY', 'ROLLBACK'])) {
                        error("Invalid ACTION: ${params.ACTION}")
                    }

                    if (!(params.RUN_TESTS in ['YES', 'NO'])) {
                        error("Invalid RUN_TESTS value: ${params.RUN_TESTS}")
                    }

                    if (!(params.PRODUCTION_CONFIRMATION in ['YES', 'NO'])) {
                        error("Invalid PRODUCTION_CONFIRMATION value.")
                    }

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.PRODUCTION_CONFIRMATION != 'YES') {

                        error(
                            'PRODUCTION deployment/rollback requires ' +
                            'PRODUCTION_CONFIRMATION=YES.'
                        )
                    }

                    echo "Environment validated: ${params.ENVIRONMENT}"
                    echo "Action validated: ${params.ACTION}"
                    echo "Version validated: ${version}"
                    echo "Git branch validated: ${env.GIT_BRANCH}"
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
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                script {

                    echo "Checking out branch: ${env.GIT_BRANCH}"

                    checkout([
                        $class: 'GitSCM',
                        branches: [
                            [name: "*/${env.GIT_BRANCH}"]
                        ],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        userRemoteConfigs: [
                            [url: env.REPO_URL]
                        ]
                    ])

                    bat '''
                        @echo off
                        git status --short --branch
                        git branch --show-current
                        git log -1 --oneline
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

                    echo Running application tests inside Python Docker container...

                    docker run --rm ^
                      -v "%CD%:/workspace" ^
                      -w /workspace ^
                      python:3.12-slim ^
                      sh -c "pip install --no-cache-dir -q -r app/requirements.txt && pytest -q app/test_app.py"

                    if errorlevel 1 (
                        echo Application tests failed.
                        exit /b 1
                    )

                    echo Application tests passed successfully.
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
                            docker inspect ${env.APP_CONTAINER} --format="{{.Config.Image}}" > previous-image.txt
                        """
                    )

                    if (result == 0) {

                        env.PREVIOUS_IMAGE = readFile(
                            'previous-image.txt'
                        ).trim()

                        if (env.PREVIOUS_IMAGE) {

                            int lastColon =
                                env.PREVIOUS_IMAGE.lastIndexOf(':')

                            if (lastColon >= 0) {
                                env.PREVIOUS_VERSION =
                                    env.PREVIOUS_IMAGE.substring(lastColon + 1)
                            }

                            echo """
Previous application image : ${env.PREVIOUS_IMAGE}
Previous application version: ${env.PREVIOUS_VERSION}
"""
                        }

                    } else {

                        echo 'No existing application container found.'
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
                            docker network inspect ${env.NETWORK} >nul 2>&1
                        """
                    )

                    if (result != 0) {

                        echo "Creating Docker network: ${env.NETWORK}"

                        bat """
                            @echo off
                            docker network create ${env.NETWORK}
                            if errorlevel 1 exit /b 1
                        """

                    } else {

                        echo "Docker network already exists: ${env.NETWORK}"
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
                            docker volume inspect ${env.DB_VOLUME} >nul 2>&1
                        """
                    )

                    if (result != 0) {

                        echo "Creating database volume: ${env.DB_VOLUME}"

                        bat """
                            @echo off
                            docker volume create ${env.DB_VOLUME}
                            if errorlevel 1 exit /b 1
                        """

                    } else {

                        echo "Database volume already exists: ${env.DB_VOLUME}"
                    }
                }
            }
        }

        stage('Prepare Target Image') {
            steps {
                script {

                    if (params.ACTION == 'DEPLOY') {

                        echo "Building Docker image: ${env.IMAGE}"

                        bat """
                            @echo off

                            docker build ^
                              --build-arg VERSION=${params.VERSION.trim()} ^
                              -t ${env.IMAGE} .

                            if errorlevel 1 (
                                echo Docker image build failed.
                                exit /b 1
                            )
                        """

                    } else {

                        echo "Rollback requested."
                        echo "Checking for existing image: ${env.IMAGE}"

                        int result = bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker image inspect ${env.IMAGE} >nul 2>&1
                            """
                        )

                        if (result != 0) {
                            error(
                                "Rollback image ${env.IMAGE} does not exist locally."
                            )
                        }

                        echo "Rollback image exists: ${env.IMAGE}"
                    }
                }
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat """
                    @echo off

                    docker image inspect ${env.IMAGE}

                    if errorlevel 1 (
                        echo Docker image verification failed.
                        exit /b 1
                    )

                    echo Docker image verified:
                    echo ${env.IMAGE}

                    docker images ${env.IMAGE_REPOSITORY}
                """
            }
        }

        stage('Deploy Database') {
            steps {
                script {

                    String credentialId

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    } else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    } else {
                        credentialId = 'db-production'
                    }

                    int containerExists = bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker inspect ${env.DB_CONTAINER} >nul 2>&1
                        """
                    )

                    if (containerExists != 0) {

                        echo "Creating database container: ${env.DB_CONTAINER}"

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
                                  --name ${env.DB_CONTAINER} ^
                                  --network ${env.NETWORK} ^
                                  --restart unless-stopped ^
                                  -e POSTGRES_DB=${env.DB_NAME} ^
                                  -e POSTGRES_USER=%DB_USER_SECRET% ^
                                  -e POSTGRES_PASSWORD=%DB_PASSWORD_SECRET% ^
                                  -v ${env.DB_VOLUME}:/var/lib/postgresql/data ^
                                  -v "%CD%\\\\db\\\\init.sql:/docker-entrypoint-initdb.d/init.sql:ro" ^
                                  postgres:16

                                if errorlevel 1 (
                                    echo Database container creation failed.
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
                                docker inspect ${env.DB_CONTAINER} --format="{{.State.Running}}" | findstr /I "true" >nul
                            """
                        )

                        if (running != 0) {

                            echo "Starting existing database container..."

                            bat """
                                @echo off
                                docker start ${env.DB_CONTAINER}
                                if errorlevel 1 exit /b 1
                            """
                        }

                        echo "Ensuring database is connected to ${env.NETWORK}..."

                        bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker network connect ${env.NETWORK} ${env.DB_CONTAINER}
                            """
                        )
                    }

                    echo "Database container ready: ${env.DB_CONTAINER}"
                }
            }
        }

        stage('Wait For Database') {
            steps {
                script {

                    String credentialId

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    } else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    } else {
                        credentialId = 'db-production'
                    }

                    int databaseReady = 1

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        for (int attempt = 1; attempt <= 30; attempt++) {

                            databaseReady = bat(
                                returnStatus: true,
                                script: """
                                    @echo off
                                    docker exec ${env.DB_CONTAINER} pg_isready -U %DB_USER_SECRET% -d ${env.DB_NAME}
                                """
                            )

                            if (databaseReady == 0) {
                                echo "Database is ready."
                                break
                            }

                            echo "Database not ready yet. Attempt ${attempt}/30"
                            sleep time: 2, unit: 'SECONDS'
                        }
                    }

                    if (databaseReady != 0) {
                        error(
                            "Database ${env.DB_CONTAINER} did not become ready."
                        )
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {

                    String credentialId

                    if (params.ENVIRONMENT == 'DEV') {
                        credentialId = 'db-dev'
                    } else if (params.ENVIRONMENT == 'UAT') {
                        credentialId = 'db-uat'
                    } else {
                        credentialId = 'db-production'
                    }

                    env.DEPLOY_STARTED = 'true'

                    echo "Deploying application image: ${env.IMAGE}"

                    bat(
                        returnStatus: true,
                        script: """
                            @echo off
                            docker rm -f ${env.APP_CONTAINER} >nul 2>&1
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
                              --name ${env.APP_CONTAINER} ^
                              --network ${env.NETWORK} ^
                              --restart unless-stopped ^
                              -p ${env.HOST_PORT}:${env.CONTAINER_PORT} ^
                              -e ENVIRONMENT=${params.ENVIRONMENT} ^
                              -e APP_VERSION=${params.VERSION.trim()} ^
                              -e DB_HOST=${env.DB_HOST} ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=${env.DB_NAME} ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              ${env.IMAGE}

                            if errorlevel 1 (
                                echo Application container failed to start.
                                exit /b 1
                            )
                        """
                    }

                    echo "Application container started: ${env.APP_CONTAINER}"
                }
            }
        }

        stage('Validate Containers') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$app=(docker inspect -f '{{.State.Running}}' '${env.APP_CONTAINER}'); ^
                     \$db=(docker inspect -f '{{.State.Running}}' '${env.DB_CONTAINER}'); ^
                     if(\$app -ne 'true'){Write-Error 'Application container is not running';exit 1}; ^
                     if(\$db -ne 'true'){Write-Error 'Database container is not running';exit 1}; ^
                     Write-Host 'Application container is RUNNING'; ^
                     Write-Host 'Database container is RUNNING'"

                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===== DOCKER PS =====
                    docker ps --filter "name=${env.APP_CONTAINER}" --filter "name=${env.DB_CONTAINER}"
                """
            }
        }

        stage('Validate Network') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$n=(docker network inspect '${env.NETWORK}' | ConvertFrom-Json)[0]; ^
                     \$names=@(\$n.Containers.PSObject.Properties | ForEach-Object { \$_.Value.Name }); ^
                     if(\$names -notcontains '${env.APP_CONTAINER}'){Write-Error 'Application is not connected to expected network';exit 1}; ^
                     if(\$names -notcontains '${env.DB_CONTAINER}'){Write-Error 'Database is not connected to expected network';exit 1}; ^
                     Write-Host 'Expected network: ${env.NETWORK}'; ^
                     Write-Host 'Connected containers:'; ^
                     \$names"

                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===== NETWORK INSPECT =====
                    docker network inspect ${env.NETWORK}
                """
            }
        }

        stage('Health Check') {
            steps {
                bat """
                    @echo off

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "\$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:${env.HOST_PORT}/health' -TimeoutSec 15; ^
                     if(\$r.StatusCode -ne 200){Write-Error 'Health check failed';exit 1}; ^
                     Write-Host 'Health check HTTP status:' \$r.StatusCode; ^
                     Write-Host 'Health response:' \$r.Content"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Application To Database Connectivity') {
            steps {
                bat """
                    @echo off

                    docker exec ${env.APP_CONTAINER} python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); s.close(); print('DATABASE CONNECTIVITY SUCCESS:',h,p)"

                    if errorlevel 1 (
                        echo Application cannot connect to database.
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
                    "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.HOST_PORT}/environment' -TimeoutSec 15; ^
                     Write-Host 'Expected environment: ${params.ENVIRONMENT}'; ^
                     Write-Host 'Actual environment  :' \$r.environment; ^
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
                    "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.HOST_PORT}/version' -TimeoutSec 15; ^
                     Write-Host 'Expected version: ${params.VERSION.trim()}'; ^
                     Write-Host 'Actual version  :' \$r.version; ^
                     if([string]\$r.version -ne '${params.VERSION.trim()}'){Write-Error 'Version mismatch';exit 1}"

                    if errorlevel 1 exit /b 1
                """
            }
        }

        stage('Volume Inspection') {
            steps {
                bat """
                    @echo off

                    echo ===== DATABASE VOLUME =====
                    docker volume inspect ${env.DB_VOLUME}

                    if errorlevel 1 exit /b 1

                    echo.
                    echo ===== APPLICATION PORT MAPPING =====
                    docker port ${env.APP_CONTAINER}

                    echo.
                    echo Expected host port: ${env.HOST_PORT}
                    echo Expected container port: ${env.CONTAINER_PORT}
                """
            }
        }

        stage('Deployment Successful') {
            steps {
                script {

                    echo """
============================================================
DEPLOYMENT SUCCESSFUL
============================================================
Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${params.VERSION.trim()}
Branch      : ${env.GIT_BRANCH}
Application : ${env.APP_CONTAINER}
Database    : ${env.DB_CONTAINER}
Network     : ${env.NETWORK}
Host Port   : ${env.HOST_PORT}
Image       : ${env.IMAGE}
============================================================
FINAL RESULT = SUCCESS
============================================================
"""
                }
            }
        }
    }

    post {

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
Requested   : ${params.VERSION.trim()}
============================================================
"""

                /*
                 * Automatic production rollback.
                 *
                 * If a production DEPLOY fails after replacing the
                 * application container, restore the previous image.
                 */

                if (
                    params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY' &&
                    env.DEPLOY_STARTED == 'true' &&
                    env.PREVIOUS_IMAGE?.trim()
                ) {

                    echo """
============================================================
AUTOMATIC PRODUCTION ROLLBACK
============================================================
Previous Image   : ${env.PREVIOUS_IMAGE}
Previous Version : ${env.PREVIOUS_VERSION}
============================================================
"""

                    String credentialId = 'db-production'

                    withCredentials([
                        usernamePassword(
                            credentialsId: credentialId,
                            usernameVariable: 'DB_USER_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat(
                            returnStatus: true,
                            script: """
                                @echo off
                                docker rm -f ${env.APP_CONTAINER} >nul 2>&1
                            """
                        )

                        bat """
                            @echo off

                            docker run -d ^
                              --name ${env.APP_CONTAINER} ^
                              --network ${env.NETWORK} ^
                              --restart unless-stopped ^
                              -p ${env.HOST_PORT}:${env.CONTAINER_PORT} ^
                              -e ENVIRONMENT=PRODUCTION ^
                              -e APP_VERSION=${env.PREVIOUS_VERSION} ^
                              -e DB_HOST=${env.DB_HOST} ^
                              -e DB_PORT=5432 ^
                              -e DB_NAME=${env.DB_NAME} ^
                              -e DB_USER=%DB_USER_SECRET% ^
                              -e DB_PASSWORD=%DB_PASSWORD_SECRET% ^
                              ${env.PREVIOUS_IMAGE}

                            if errorlevel 1 (
                                echo ROLLBACK APPLICATION FAILED.
                                exit /b 1
                            )
                        """
                    }

                    echo "Waiting for rolled-back application..."

                    sleep time: 5, unit: 'SECONDS'

                    int rollbackHealth = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                            "\$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:${env.HOST_PORT}/health' -TimeoutSec 15; ^
                             if(\$r.StatusCode -ne 200){exit 1}; ^
                             Write-Host \$r.Content"
                        """
                    )

                    int rollbackVersion = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                            "\$r=Invoke-RestMethod -Uri 'http://localhost:${env.HOST_PORT}/version' -TimeoutSec 15; ^
                             Write-Host 'Rollback version:' \$r.version; ^
                             if([string]\$r.version -ne '${env.PREVIOUS_VERSION}'){exit 1}"
                        """
                    )

                    int rollbackDb = bat(
                        returnStatus: true,
                        script: """
                            @echo off

                            docker exec ${env.APP_CONTAINER} python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); s.close(); print('ROLLBACK DATABASE CONNECTIVITY SUCCESS:',h,p)"
                        """
                    )

                    if (
                        rollbackHealth == 0 &&
                        rollbackVersion == 0 &&
                        rollbackDb == 0
                    ) {

                        echo """
============================================================
ROLLBACK SUCCESSFUL
============================================================
Restored Image   : ${env.PREVIOUS_IMAGE}
Restored Version : ${env.PREVIOUS_VERSION}
Environment      : PRODUCTION
Application      : ${env.APP_CONTAINER}
Database         : ${env.DB_CONTAINER}
Network          : ${env.NETWORK}
============================================================
FINAL RESULT = ROLLBACK
============================================================
"""

                    } else {

                        echo """
============================================================
ROLLBACK FAILED
============================================================
Health Check Result       : ${rollbackHealth}
Version Validation Result : ${rollbackVersion}
Database Connectivity     : ${rollbackDb}
============================================================
"""
                    }

                } else {

                    echo 'Automatic rollback was not applicable.'
                }
            }
        }

        always {
            script {

                echo 'Collecting deployment evidence...'

                bat(
                    returnStatus: true,
                    script: """
                        @echo off

                        docker ps -a > evidence-docker-ps.txt

                        docker network inspect ${env.NETWORK} > evidence-network.txt

                        docker volume inspect ${env.DB_VOLUME} > evidence-volume.txt

                        docker images ${env.IMAGE_REPOSITORY} > evidence-docker-images.txt

                        docker port ${env.APP_CONTAINER} > evidence-port.txt
                    """
                )

                archiveArtifacts(
                    artifacts: 'evidence-*.txt,previous-image.txt',
                    allowEmptyArchive: true,
                    fingerprint: true
                )
            }

            echo "Build completed with status: ${currentBuild.currentResult}"
        }
    }
}