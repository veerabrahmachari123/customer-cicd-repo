```groovy
pipeline {

    agent any

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
            description: 'Application version/image tag'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Must be YES for PRODUCTION deployment'
        )
    }

    environment {

        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'

        IMAGE_REPOSITORY = 'customer-app'
        CONTAINER_PORT = '8080'

        DEPLOY_GIT_BRANCH = ''
        DEPLOY_NETWORK = ''
        DEPLOY_APP_CONTAINER = ''
        DEPLOY_DB_CONTAINER = ''
        DEPLOY_DB_VOLUME = ''
        DEPLOY_DB_HOST = ''
        DEPLOY_DB_NAME = ''
        DEPLOY_DB_USER = ''
        DEPLOY_HOST_PORT = ''
        DEPLOY_IMAGE = ''

        PREVIOUS_IMAGE = 'NONE'
        PREVIOUS_VERSION = 'NONE'
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
                    }

                    env.DEPLOY_IMAGE =
                        "${env.IMAGE_REPOSITORY}:${params.VERSION}"

                    echo """
============================================================
RESOLVED DEPLOYMENT CONFIGURATION
============================================================
Environment           : ${params.ENVIRONMENT}
Action                : ${params.ACTION}
Version               : ${params.VERSION}
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

                    if (!(params.ENVIRONMENT in ['DEV', 'UAT', 'PRODUCTION'])) {
                        error('Invalid environment selected.')
                    }

                    if (!(params.ACTION in ['DEPLOY', 'ROLLBACK'])) {
                        error('Invalid action selected.')
                    }

                    if (!(params.VERSION ==~ /^[0-9]+(\.[0-9]+)*$/)) {
                        error(
                            "Invalid VERSION '${params.VERSION}'. " +
                            "Use values such as 5.0, 5.1 or 6.0."
                        )
                    }

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.ACTION == 'DEPLOY' &&
                        params.PRODUCTION_CONFIRMATION != 'YES'
                    ) {
                        error(
                            'Production deployment requires ' +
                            'PRODUCTION_CONFIRMATION=YES.'
                        )
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
                script {

                    echo "Checking out branch: ${env.DEPLOY_GIT_BRANCH}"

                    checkout([
                        $class: 'GitSCM',

                        branches: [[
                            name: "*/${env.DEPLOY_GIT_BRANCH}"
                        ]],

                        doGenerateSubmoduleConfigurations: false,

                        extensions: [[
                            $class: 'CleanBeforeCheckout'
                        ]],

                        userRemoteConfigs: [[
                            url: env.REPO_URL
                        ]]
                    ])

                    bat '''
                        echo ===== CURRENT BRANCH =====
                        git branch --show-current

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
                        sh -c "pip install -q -r app/requirements.txt && python -m pytest app/test_app.py -v"

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

                    bat '''
                        if exist previous-image.txt del /q previous-image.txt
                    '''

                    def containerExists = bat(
                        script: """
                            @echo off

                            docker inspect "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                            if errorlevel 1 exit /b 1

                            exit /b 0
                        """,
                        returnStatus: true
                    )

                    if (containerExists == 0) {

                        bat '''
                            docker inspect -f "{{.Config.Image}}" "%DEPLOY_APP_CONTAINER%" > previous-image.txt
                        '''

                        def previousImageFile =
                            readFile('previous-image.txt').trim()

                        if (
                            previousImageFile &&
                            previousImageFile != 'NONE'
                        ) {

                            env.PREVIOUS_IMAGE = previousImageFile

                            def versionMatcher =
                                previousImageFile =~ /:(.+)$/

                            if (versionMatcher.find()) {
                                env.PREVIOUS_VERSION =
                                    versionMatcher.group(1)
                            }
                        }

                    } else {

                        env.PREVIOUS_IMAGE = 'NONE'
                        env.PREVIOUS_VERSION = 'NONE'

                        writeFile(
                            file: 'previous-image.txt',
                            text: 'NONE'
                        )
                    }

                    echo """
Previous Image   : ${env.PREVIOUS_IMAGE}
Previous Version : ${env.PREVIOUS_VERSION}
"""
                }
            }
        }

        stage('Prepare Docker Network') {
            steps {
                script {

                    def networkExists = bat(
                        script: """
                            @echo off

                            docker network inspect "%DEPLOY_NETWORK%" >nul 2>&1

                            if errorlevel 1 exit /b 1

                            exit /b 0
                        """,
                        returnStatus: true
                    )

                    if (networkExists != 0) {

                        bat '''
                            echo Creating Docker network...

                            docker network create "%DEPLOY_NETWORK%"

                            if errorlevel 1 (
                                echo ERROR: Could not create Docker network.
                                exit /b 1
                            )

                            echo Docker network created.
                        '''

                    } else {

                        echo "Network already exists: ${env.DEPLOY_NETWORK}"
                    }
                }
            }
        }

        stage('Prepare Database Volume') {
            steps {
                script {

                    def volumeExists = bat(
                        script: """
                            @echo off

                            docker volume inspect "%DEPLOY_DB_VOLUME%" >nul 2>&1

                            if errorlevel 1 exit /b 1

                            exit /b 0
                        """,
                        returnStatus: true
                    )

                    if (volumeExists != 0) {

                        bat '''
                            echo Creating database volume...

                            docker volume create "%DEPLOY_DB_VOLUME%"

                            if errorlevel 1 (
                                echo ERROR: Could not create database volume.
                                exit /b 1
                            )

                            echo Database volume created.
                        '''

                    } else {

                        echo "Volume already exists: ${env.DEPLOY_DB_VOLUME}"
                    }
                }
            }
        }

        stage('Prepare Target Image') {
            steps {
                script {

                    echo "Building ${env.DEPLOY_IMAGE}"

                    bat """
                        docker build ^
                            --build-arg VERSION=${params.VERSION} ^
                            -t "${env.DEPLOY_IMAGE}" .

                        if errorlevel 1 (
                            echo ERROR: Docker image build failed.
                            exit /b 1
                        )
                    """
                }
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat '''
                    docker image inspect "%DEPLOY_IMAGE%"

                    if errorlevel 1 (
                        echo ERROR: Docker image does not exist.
                        exit /b 1
                    )

                    echo.
                    echo ===== DOCKER IMAGES =====

                    docker images "%IMAGE_REPOSITORY%"

                    echo.
                    echo Docker image verified successfully:
                    echo %DEPLOY_IMAGE%
                '''
            }
        }

        stage('Deploy Database') {
            steps {
                script {

                    def dbExists = bat(
                        script: """
                            @echo off

                            docker inspect "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                            if errorlevel 1 exit /b 1

                            exit /b 0
                        """,
                        returnStatus: true
                    )

                    if (dbExists != 0) {

                        withCredentials([
                            usernamePassword(
                                credentialsId:
                                    params.ENVIRONMENT == 'DEV'
                                        ? 'db-dev'
                                        : params.ENVIRONMENT == 'UAT'
                                            ? 'db-uat'
                                            : 'db-production',

                                usernameVariable:
                                    'DB_USERNAME_SECRET',

                                passwordVariable:
                                    'DB_PASSWORD_SECRET'
                            )
                        ]) {

                            bat '''
                                echo Creating database container...

                                docker run -d ^
                                    --name "%DEPLOY_DB_CONTAINER%" ^
                                    --network "%DEPLOY_NETWORK%" ^
                                    --network-alias "%DEPLOY_DB_HOST%" ^
                                    -e "POSTGRES_DB=%DEPLOY_DB_NAME%" ^
                                    -e "POSTGRES_USER=%DB_USERNAME_SECRET%" ^
                                    -e "POSTGRES_PASSWORD=%DB_PASSWORD_SECRET%" ^
                                    -v "%DEPLOY_DB_VOLUME%:/var/lib/postgresql/data" ^
                                    postgres:16

                                if errorlevel 1 (
                                    echo ERROR: Database container creation failed.
                                    exit /b 1
                                )

                                echo Database container created.
                            '''
                        }

                    } else {

                        echo "Database container already exists."

                        bat '''
                            docker start "%DEPLOY_DB_CONTAINER%" >nul 2>&1
                        '''
                    }

                    /*
                     * IMPORTANT:
                     * Check Docker network membership before attempting
                     * docker network connect.
                     */

                    def dbOnNetwork = bat(
                        script: """
                            @echo off

                            docker network inspect "%DEPLOY_NETWORK%" --format="{{range .Containers}}{{.Name}} {{end}}" > db-network-members.txt 2>nul

                            findstr /i "%DEPLOY_DB_CONTAINER%" db-network-members.txt >nul

                            if errorlevel 1 exit /b 1

                            exit /b 0
                        """,
                        returnStatus: true
                    )

                    if (dbOnNetwork != 0) {

                        bat '''
                            echo Connecting database to expected network...

                            docker network connect "%DEPLOY_NETWORK%" "%DEPLOY_DB_CONTAINER%"

                            if errorlevel 1 (
                                echo ERROR: Could not connect database to network.
                                exit /b 1
                            )

                            echo Database connected to expected network.
                        '''

                    } else {

                        echo "Database already connected to expected network."
                    }

                    echo "Database ready: ${env.DEPLOY_DB_CONTAINER}"
                }
            }
        }

        stage('Wait For Database') {
            steps {
                script {

                    withCredentials([
                        usernamePassword(
                            credentialsId:
                                params.ENVIRONMENT == 'DEV'
                                    ? 'db-dev'
                                    : params.ENVIRONMENT == 'UAT'
                                        ? 'db-uat'
                                        : 'db-production',

                            usernameVariable:
                                'DB_USERNAME_SECRET',

                            passwordVariable:
                                'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat '''
                            echo Waiting for database...

                            set DB_READY=NO

                            for /L %%i in (1,1,30) do (

                                docker exec "%DEPLOY_DB_CONTAINER%" ^
                                    pg_isready ^
                                    -U "%DB_USERNAME_SECRET%" ^
                                    -d "%DEPLOY_DB_NAME%" >nul 2>&1

                                if not errorlevel 1 (
                                    set DB_READY=YES
                                    goto :DBREADY
                                )

                                timeout /t 2 /nobreak >nul
                            )

                            :DBREADY

                            if "%DB_READY%"=="NO" (
                                echo ERROR: Database did not become ready.
                                docker logs "%DEPLOY_DB_CONTAINER%"
                                exit /b 1
                            )

                            echo Database is READY.
                        '''
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {

                    echo "Deploying application..."

                    bat '''
                        docker rm -f "%DEPLOY_APP_CONTAINER%" >nul 2>&1
                    '''

                    withCredentials([
                        usernamePassword(
                            credentialsId:
                                params.ENVIRONMENT == 'DEV'
                                    ? 'db-dev'
                                    : params.ENVIRONMENT == 'UAT'
                                        ? 'db-uat'
                                        : 'db-production',

                            usernameVariable:
                                'DB_USERNAME_SECRET',

                            passwordVariable:
                                'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        bat '''
                            docker run -d ^
                                --name "%DEPLOY_APP_CONTAINER%" ^
                                --network "%DEPLOY_NETWORK%" ^
                                -p "%DEPLOY_HOST_PORT%:%CONTAINER_PORT%" ^
                                -e "APP_ENV=%ENVIRONMENT%" ^
                                -e "APP_VERSION=%VERSION%" ^
                                -e "DB_HOST=%DEPLOY_DB_HOST%" ^
                                -e "DB_PORT=5432" ^
                                -e "DB_NAME=%DEPLOY_DB_NAME%" ^
                                -e "DB_USER=%DB_USERNAME_SECRET%" ^
                                -e "DB_PASSWORD=%DB_PASSWORD_SECRET%" ^
                                "%DEPLOY_IMAGE%"

                            if errorlevel 1 (
                                echo ERROR: Application container failed to start.
                                exit /b 1
                            )
                        '''
                    }

                    echo "Application started: ${env.DEPLOY_APP_CONTAINER}"
                }
            }
        }

        stage('Validate Containers') {
            steps {
                bat '''
                    echo ============================================
                    echo VALIDATING APPLICATION CONTAINER
                    echo ============================================

                    docker inspect "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo ERROR: Application container does not exist.
                        docker ps -a
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" > app-running.txt

                    findstr /i "true" app-running.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application container is not running.
                        type app-running.txt
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Application container is RUNNING.

                    echo ============================================
                    echo VALIDATING DATABASE CONTAINER
                    echo ============================================

                    docker inspect "%DEPLOY_DB_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo ERROR: Database container does not exist.
                        docker ps -a
                        docker logs "%DEPLOY_DB_CONTAINER%"
                        exit /b 1
                    )

                    docker inspect -f "{{.State.Running}}" "%DEPLOY_DB_CONTAINER%" > db-running.txt

                    findstr /i "true" db-running.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database container is not running.
                        type db-running.txt
                        docker logs "%DEPLOY_DB_CONTAINER%"
                        exit /b 1
                    )

                    echo Database container is RUNNING.

                    echo ============================================
                    echo CONTAINER VALIDATION PASSED
                    echo ============================================
                '''
            }
        }

        stage('Validate Network') {
            steps {
                bat '''
                    echo ============================================
                    echo VALIDATING DOCKER NETWORK
                    echo ============================================

                    docker network inspect "%DEPLOY_NETWORK%"

                    if errorlevel 1 (
                        echo ERROR: Network does not exist.
                        exit /b 1
                    )

                    docker network inspect "%DEPLOY_NETWORK%" --format="{{range .Containers}}{{.Name}} {{end}}" > network-containers.txt

                    echo.
                    echo Connected containers:
                    type network-containers.txt

                    findstr /i "%DEPLOY_APP_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not connected to expected network.
                        exit /b 1
                    )

                    findstr /i "%DEPLOY_DB_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not connected to expected network.
                        exit /b 1
                    )

                    echo.
                    echo Application and database are on:
                    echo %DEPLOY_NETWORK%

                    echo.
                    echo Network validation PASSED.
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    echo ============================================
                    echo APPLICATION HEALTH CHECK
                    echo ============================================

                    echo Waiting for application...
                    timeout /t 3 /nobreak >nul

                    echo Checking health endpoint...

                    curl.exe -fsS "http://localhost:%DEPLOY_HOST_PORT%/health" -o health-response.json

                    if errorlevel 1 (
                        echo ERROR: Health endpoint failed.
                        type health-response.json 2>nul
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    echo.
                    echo Health response:
                    type health-response.json

                    echo.
                    echo HEALTH CHECK PASSED.
                '''
            }
        }

        stage('Application To Database Connectivity') {
            steps {
                bat '''
                    echo ============================================
                    echo APPLICATION TO DATABASE CONNECTIVITY
                    echo ============================================

                    docker exec "%DEPLOY_APP_CONTAINER%" python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); print('Database reachable from application:',h,p); s.close()"

                    if errorlevel 1 (
                        echo ERROR: Application cannot reach database.
                        docker logs "%DEPLOY_APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Application can reach database successfully.
                '''
            }
        }

        stage('Environment Validation') {
            steps {
                bat '''
                    echo ============================================
                    echo ENVIRONMENT VALIDATION
                    echo ============================================

                    curl.exe -fsS "http://localhost:%DEPLOY_HOST_PORT%/environment" -o environment-response.json

                    if errorlevel 1 (
                        echo ERROR: Environment endpoint failed.
                        type environment-response.json 2>nul
                        exit /b 1
                    )

                    echo.
                    echo Environment response:
                    type environment-response.json

                    findstr /i "%ENVIRONMENT%" environment-response.json >nul

                    if errorlevel 1 (
                        echo ERROR: Expected environment was not found.
                        echo Expected: %ENVIRONMENT%
                        exit /b 1
                    )

                    echo.
                    echo Environment validation PASSED.
                '''
            }
        }

        stage('Version Validation') {
            steps {
                bat '''
                    echo ============================================
                    echo VERSION VALIDATION
                    echo ============================================

                    curl.exe -fsS "http://localhost:%DEPLOY_HOST_PORT%/version" -o version-response.json

                    if errorlevel 1 (
                        echo ERROR: Version endpoint failed.
                        type version-response.json 2>nul
                        exit /b 1
                    )

                    echo.
                    echo Version response:
                    type version-response.json

                    findstr /i "%VERSION%" version-response.json >nul

                    if errorlevel 1 (
                        echo ERROR: Requested version was not found.
                        echo Expected version: %VERSION%
                        exit /b 1
                    )

                    echo.
                    echo Version validation PASSED.
                '''
            }
        }

        stage('Volume Inspection') {
            steps {
                bat '''
                    echo ============================================
                    echo DATABASE VOLUME INSPECTION
                    echo ============================================

                    docker volume inspect "%DEPLOY_DB_VOLUME%"

                    if errorlevel 1 (
                        echo ERROR: Database volume inspection failed.
                        exit /b 1
                    )

                    echo.
                    echo Volume inspection PASSED.
                '''
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
Version     : ${params.VERSION}
Image       : ${env.DEPLOY_IMAGE}
Network     : ${env.DEPLOY_NETWORK}
Application : ${env.DEPLOY_APP_CONTAINER}
Database    : ${env.DEPLOY_DB_CONTAINER}
============================================================
"""
            }
        }
    }

    post {

        always {
            script {

                echo "Collecting deployment evidence..."

                bat '''
                    docker ps -a > evidence-docker-ps.txt 2>&1
                    docker images > evidence-docker-images.txt 2>&1
                    docker network inspect "%DEPLOY_NETWORK%" > evidence-network.txt 2>&1
                    docker volume inspect "%DEPLOY_DB_VOLUME%" > evidence-volume.txt 2>&1
                    docker port "%DEPLOY_APP_CONTAINER%" > evidence-port.txt 2>&1
                '''

                archiveArtifacts(
                    artifacts:
                        'evidence-*.txt,' +
                        'health-response.json,' +
                        'environment-response.json,' +
                        'version-response.json,' +
                        'previous-image.txt,' +
                        'app-running.txt,' +
                        'db-running.txt,' +
                        'network-containers.txt,' +
                        'db-network-members.txt',

                    allowEmptyArchive: true,
                    fingerprint: true
                )
            }
        }

        success {
            echo """
============================================================
PIPELINE SUCCESSFUL
============================================================
Environment : ${params.ENVIRONMENT}
Action      : ${params.ACTION}
Version     : ${params.VERSION}
============================================================
"""
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
                    env.PREVIOUS_IMAGE != 'NONE' &&
                    env.PREVIOUS_IMAGE?.trim()
                ) {

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'db-production',
                            usernameVariable: 'DB_USERNAME_SECRET',
                            passwordVariable: 'DB_PASSWORD_SECRET'
                        )
                    ]) {

                        echo "Automatic production rollback starting..."
                        echo "Rollback image: ${env.PREVIOUS_IMAGE}"

                        bat '''
                            echo ============================================
                            echo PRODUCTION ROLLBACK
                            echo ============================================

                            echo Removing failed production application...

                            docker rm -f "%DEPLOY_APP_CONTAINER%" >nul 2>&1

                            echo Starting rollback application...

                            docker run -d ^
                                --name "%DEPLOY_APP_CONTAINER%" ^
                                --network "%DEPLOY_NETWORK%" ^
                                -p "%DEPLOY_HOST_PORT%:%CONTAINER_PORT%" ^
                                -e "APP_ENV=%ENVIRONMENT%" ^
                                -e "APP_VERSION=%PREVIOUS_VERSION%" ^
                                -e "DB_HOST=%DEPLOY_DB_HOST%" ^
                                -e "DB_PORT=5432" ^
                                -e "DB_NAME=%DEPLOY_DB_NAME%" ^
                                -e "DB_USER=%DB_USERNAME_SECRET%" ^
                                -e "DB_PASSWORD=%DB_PASSWORD_SECRET%" ^
                                "%PREVIOUS_IMAGE%"

                            if errorlevel 1 (
                                echo ERROR: Rollback container could not start.
                                exit /b 1
                            )

                            timeout /t 5 /nobreak >nul

                            echo Validating rollback container...

                            docker inspect -f "{{.State.Running}}" "%DEPLOY_APP_CONTAINER%" > rollback-running.txt

                            findstr /i "true" rollback-running.txt >nul

                            if errorlevel 1 (
                                echo ERROR: Rollback application is not running.
                                docker logs "%DEPLOY_APP_CONTAINER%"
                                exit /b 1
                            )

                            echo Rollback application is RUNNING.

                            echo Checking rollback health...

                            curl.exe -fsS "http://localhost:%DEPLOY_HOST_PORT%/health" -o rollback-health.json

                            if errorlevel 1 (
                                echo ERROR: Rollback health check failed.
                                docker logs "%DEPLOY_APP_CONTAINER%"
                                exit /b 1
                            )

                            echo Rollback health check PASSED.

                            echo Checking rollback version...

                            curl.exe -fsS "http://localhost:%DEPLOY_HOST_PORT%/version" -o rollback-version.json

                            if errorlevel 1 (
                                echo ERROR: Rollback version endpoint failed.
                                exit /b 1
                            )

                            findstr /i "%PREVIOUS_VERSION%" rollback-version.json >nul

                            if errorlevel 1 (
                                echo ERROR: Rollback version does not match previous version.
                                exit /b 1
                            )

                            echo Rollback version validation PASSED.

                            echo Testing rollback database connectivity...

                            docker exec "%DEPLOY_APP_CONTAINER%" python -c "import os,socket; h=os.environ['DB_HOST']; p=int(os.environ.get('DB_PORT','5432')); s=socket.create_connection((h,p),5); print('Rollback application can reach database:',h,p); s.close()"

                            if errorlevel 1 (
                                echo ERROR: Rollback application cannot reach database.
                                docker logs "%DEPLOY_APP_CONTAINER%"
                                exit /b 1
                            )

                            echo Rollback database connectivity PASSED.

                            echo ROLLBACK VALIDATION PASSED.
                        '''

                        archiveArtifacts(
                            artifacts:
                                'rollback-running.txt,' +
                                'rollback-health.json,' +
                                'rollback-version.json',

                            allowEmptyArchive: true,
                            fingerprint: true
                        )

                        echo """
============================================================
ROLLBACK SUCCESSFUL
============================================================
Restored Image   : ${env.PREVIOUS_IMAGE}
Restored Version : ${env.PREVIOUS_VERSION}
Environment      : PRODUCTION
============================================================
"""
                    }

                } else {

                    echo "Automatic rollback was not required."
                }
            }
        }
    }
}
```
