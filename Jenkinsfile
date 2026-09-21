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
            description: 'Application version'
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

        APP_IMAGE = 'customer-app'
        DB_IMAGE = 'mysql:8.0'

        DB_NAME = 'customerdb'
        DB_USER = 'customeruser'
        DB_PASSWORD = 'customerpass'
        DB_ROOT_PASSWORD = 'rootpass'
    }

    stages {

        stage('Resolve Configuration') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'DEV') {
                        env.GIT_BRANCH = 'develop'
                        env.APP_CONTAINER = 'customer-app-dev'
                        env.DB_CONTAINER = 'customer-db-dev'
                        env.DOCKER_NETWORK = 'customer-dev-net'
                        env.DB_VOLUME = 'customer-db-dev-data'
                        env.HOST_PORT = '8081'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        env.GIT_BRANCH = 'release'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.DOCKER_NETWORK = 'customer-uat-net'
                        env.DB_VOLUME = 'customer-db-uat-data'
                        env.HOST_PORT = '8082'
                    }
                    else {
                        env.GIT_BRANCH = 'main'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.DOCKER_NETWORK = 'customer-prod-net'
                        env.DB_VOLUME = 'customer-db-prod-data'
                        env.HOST_PORT = '8083'
                    }

                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Action      : ${params.ACTION}"
                    echo "Version     : ${params.VERSION}"
                    echo "Git Branch  : ${env.GIT_BRANCH}"
                    echo "App         : ${env.APP_CONTAINER}"
                    echo "Database    : ${env.DB_CONTAINER}"
                    echo "Network     : ${env.DOCKER_NETWORK}"
                    echo "Volume      : ${env.DB_VOLUME}"
                    echo "Port        : ${env.HOST_PORT}"

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.ACTION == 'DEPLOY' &&
                        params.PRODUCTION_CONFIRMATION != 'YES') {
                        error('Production deployment requires PRODUCTION_CONFIRMATION = YES')
                    }
                }
            }
        }

        stage('Docker Check') {
            steps {
                bat '''
                    @echo off

                    docker version
                    if errorlevel 1 (
                        echo ERROR: Docker is unavailable.
                        exit /b 1
                    )

                    docker info
                    if errorlevel 1 (
                        echo ERROR: Docker Desktop is not running.
                        exit /b 1
                    )

                    echo Docker is ready.
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                bat '''
                    @echo off

                    echo Fetching repository...

                    git init

                    git remote remove origin >nul 2>&1
                    git remote add origin "%REPO_URL%"

                    git fetch origin --prune

                    if errorlevel 1 (
                        echo ERROR: Git fetch failed.
                        exit /b 1
                    )

                    echo Checking out %GIT_BRANCH%...

                    git checkout -B "%GIT_BRANCH%" "origin/%GIT_BRANCH%"

                    if errorlevel 1 (
                        echo ERROR: Checkout failed.
                        exit /b 1
                    )

                    git reset --hard "origin/%GIT_BRANCH%"

                    if errorlevel 1 (
                        echo ERROR: Git reset failed.
                        exit /b 1
                    )

                    echo.
                    echo Current commit:

                    git log -1 --oneline
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
                    @echo off

                    python -m pip install -r app\\requirements.txt

                    if errorlevel 1 (
                        echo ERROR: Dependency installation failed.
                        exit /b 1
                    )

                    python -m pytest app\\test_app.py -v

                    if errorlevel 1 (
                        echo ERROR: Tests failed.
                        exit /b 1
                    )

                    echo Tests passed.
                '''
            }
        }

        stage('Capture Previous Deployment') {
            steps {
                bat '''
                    @echo off

                    docker inspect "%APP_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo NONE > previous-image.txt
                    ) else (
                        docker inspect "%APP_CONTAINER%" --format="{{.Config.Image}}" > previous-image.txt
                    )

                    echo Previous image:
                    type previous-image.txt
                '''
            }
        }

        stage('Prepare Docker Network') {
            steps {
                bat '''
                    @echo off

                    docker network inspect "%DOCKER_NETWORK%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating network %DOCKER_NETWORK%...

                        docker network create "%DOCKER_NETWORK%"

                        if errorlevel 1 (
                            echo ERROR: Network creation failed.
                            exit /b 1
                        )
                    ) else (
                        echo Network already exists.
                    )

                    echo.
                    docker network inspect "%DOCKER_NETWORK%"
                '''
            }
        }

        stage('Prepare Docker Volume') {
            steps {
                bat '''
                    @echo off

                    docker volume inspect "%DB_VOLUME%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating volume %DB_VOLUME%...

                        docker volume create "%DB_VOLUME%"

                        if errorlevel 1 (
                            echo ERROR: Volume creation failed.
                            exit /b 1
                        )
                    ) else (
                        echo Volume already exists.
                    )

                    echo.
                    docker volume inspect "%DB_VOLUME%"
                '''
            }
        }

        stage('Build Application Image') {
            steps {
                bat '''
                    @echo off

                    echo Building %APP_IMAGE%:%VERSION%...

                    docker build --build-arg VERSION="%VERSION%" -t "%APP_IMAGE%:%VERSION%" .

                    if errorlevel 1 (
                        echo ERROR: Docker build failed.
                        exit /b 1
                    )

                    docker image inspect "%APP_IMAGE%:%VERSION%"

                    if errorlevel 1 (
                        echo ERROR: Image verification failed.
                        exit /b 1
                    )

                    echo Image created successfully.
                '''
            }
        }

        stage('Deploy Database') {
            steps {
                bat '''
                    @echo off

                    echo Checking database container...

                    docker inspect "%DB_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (

                        echo Creating database container...

                        docker run -d ^
                            --name "%DB_CONTAINER%" ^
                            --network "%DOCKER_NETWORK%" ^
                            --network-alias "%DB_CONTAINER%" ^
                            -v "%DB_VOLUME%:/var/lib/mysql" ^
                            -e MYSQL_DATABASE="%DB_NAME%" ^
                            -e MYSQL_USER="%DB_USER%" ^
                            -e MYSQL_PASSWORD="%DB_PASSWORD%" ^
                            -e MYSQL_ROOT_PASSWORD="%DB_ROOT_PASSWORD%" ^
                            "%DB_IMAGE%"

                        if errorlevel 1 (
                            echo ERROR: Database creation failed.
                            exit /b 1
                        )

                    ) else (

                        echo Database already exists.

                        docker start "%DB_CONTAINER%" >nul 2>&1
                    )

                    echo.
                    echo Checking network membership...

                    docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}" | findstr /I /X "%DB_CONTAINER%" >nul

                    if errorlevel 1 (

                        echo Connecting database to network...

                        docker network connect "%DOCKER_NETWORK%" "%DB_CONTAINER%"

                        if errorlevel 1 (
                            echo ERROR: Network connection failed.
                            exit /b 1
                        )

                    ) else (

                        echo Database already connected.
                    )

                    echo.
                    echo Waiting for MySQL...

                    set DB_READY=0

                    for /L %%i in (1,1,30) do (

                        docker exec "%DB_CONTAINER%" mysqladmin ping -h localhost -u root -p"%DB_ROOT_PASSWORD%" --silent >nul 2>&1

                        if not errorlevel 1 (
                            echo Database is ready.
                            set DB_READY=1
                            goto DB_READY
                        )

                        echo Waiting... %%i/30

                        timeout /t 2 /nobreak >nul
                    )

                    :DB_READY

                    if "%DB_READY%"=="0" (
                        echo ERROR: Database did not become ready.
                        docker logs "%DB_CONTAINER%"
                        exit /b 1
                    )
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                bat '''
                    @echo off

                    echo Removing old application container...

                    docker rm -f "%APP_CONTAINER%" >nul 2>&1

                    echo Starting application...

                    docker run -d ^
                        --name "%APP_CONTAINER%" ^
                        --network "%DOCKER_NETWORK%" ^
                        -p "%HOST_PORT%:8080" ^
                        -e APP_ENV="%ENVIRONMENT%" ^
                        -e APP_VERSION="%VERSION%" ^
                        -e DB_HOST="%DB_CONTAINER%" ^
                        -e DB_PORT="3306" ^
                        -e DB_NAME="%DB_NAME%" ^
                        -e DB_USER="%DB_USER%" ^
                        -e DB_PASSWORD="%DB_PASSWORD%" ^
                        "%APP_IMAGE%:%VERSION%"

                    if errorlevel 1 (
                        echo ERROR: Application failed to start.
                        exit /b 1
                    )

                    echo Application started.

                    docker ps --filter "name=%APP_CONTAINER%"
                '''
            }
        }

        stage('Validate Containers') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo VALIDATING CONTAINERS
                    echo ========================================

                    docker inspect "%APP_CONTAINER%" --format="{{.State.Running}}" > app-running.txt

                    set /p APP_RUNNING=<app-running.txt

                    echo Application running: %APP_RUNNING%

                    if /I not "%APP_RUNNING%"=="true" (
                        echo ERROR: Application is not running.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    docker inspect "%DB_CONTAINER%" --format="{{.State.Running}}" > db-running.txt

                    set /p DB_RUNNING=<db-running.txt

                    echo Database running: %DB_RUNNING%

                    if /I not "%DB_RUNNING%"=="true" (
                        echo ERROR: Database is not running.
                        docker logs "%DB_CONTAINER%"
                        exit /b 1
                    )

                    echo.
                    echo Both containers are running.
                '''
            }
        }

        stage('Validate Network') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo VALIDATING NETWORK
                    echo ========================================

                    docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}" > network-containers.txt

                    echo Connected containers:

                    type network-containers.txt

                    findstr /I /X "%APP_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not on correct network.
                        exit /b 1
                    )

                    findstr /I /X "%DB_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not on correct network.
                        exit /b 1
                    )

                    echo Network validation successful.
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    @echo off

                    echo Waiting for application...

                    timeout /t 5 /nobreak >nul

                    echo Checking health endpoint...

                    curl.exe --fail --silent --show-error "http://localhost:%HOST_PORT%/health"

                    if errorlevel 1 (
                        echo ERROR: Health check failed.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    echo.
                    echo Health check successful.
                '''
            }
        }

        stage('Validate App To DB Connectivity') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo APP TO DATABASE CONNECTIVITY
                    echo ========================================

                    docker exec "%APP_CONTAINER%" python -c "import socket; s=socket.create_connection(('%DB_CONTAINER%',3306),5); print('DATABASE CONNECTION SUCCESSFUL'); s.close()"

                    if errorlevel 1 (
                        echo ERROR: Application cannot reach database.
                        exit /b 1
                    )

                    echo.
                    echo Application successfully reached database.
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                bat '''
                    @echo off

                    echo Expected environment: %ENVIRONMENT%
                    echo Expected version: %VERSION%

                    echo.
                    echo Environment:

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/environment"

                    if errorlevel 1 (
                        echo ERROR: Environment endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Version:

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/version"

                    if errorlevel 1 (
                        echo ERROR: Version endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Environment validation successful.
                '''
            }
        }

        stage('Validate Customer Search') {
            steps {
                bat '''
                    @echo off

                    echo Testing customer search...

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/customers/search?name=John"

                    if errorlevel 1 (
                        echo ERROR: Customer search failed.
                        exit /b 1
                    )

                    echo.
                    echo Customer search successful.
                '''
            }
        }

        stage('Deployment Evidence') {
            steps {

                bat '''
                    @echo off

                    (
                        echo Environment: %ENVIRONMENT%
                        echo Action: %ACTION%
                        echo Version: %VERSION%
                        echo Git Branch: %GIT_BRANCH%
                        echo Application: %APP_CONTAINER%
                        echo Database: %DB_CONTAINER%
                        echo Network: %DOCKER_NETWORK%
                        echo Volume: %DB_VOLUME%
                        echo Host Port: %HOST_PORT%
                        echo.
                        echo Containers:
                        docker ps
                        echo.
                        echo Network:
                        docker network inspect "%DOCKER_NETWORK%"
                        echo.
                        echo Volume:
                        docker volume inspect "%DB_VOLUME%"
                        echo.
                        echo Images:
                        docker images "%APP_IMAGE%"
                    ) > deployment-evidence.txt

                    type deployment-evidence.txt
                '''

                archiveArtifacts(
                    artifacts: 'deployment-evidence.txt,previous-image.txt,network-containers.txt,app-running.txt,db-running.txt',
                    allowEmptyArchive: true
                )
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'DEPLOYMENT SUCCESSFUL'
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Version     : ${params.VERSION}"
            echo "Application : ${env.APP_CONTAINER}"
            echo "Database    : ${env.DB_CONTAINER}"
            echo "Network     : ${env.DOCKER_NETWORK}"
            echo "Port        : ${env.HOST_PORT}"
            echo '========================================'
        }

        failure {
            script {

                echo 'Deployment failed.'

                bat '''
                    @echo off

                    docker logs "%APP_CONTAINER%" > failure-app-logs.txt 2>&1

                    docker logs "%DB_CONTAINER%" > failure-db-logs.txt 2>&1

                    docker ps -a > failure-containers.txt 2>&1
                '''

                archiveArtifacts(
                    artifacts: 'failure-app-logs.txt,failure-db-logs.txt,failure-containers.txt',
                    allowEmptyArchive: true
                )
            }
        }

        always {
            echo 'Pipeline completed.'
        }
    }
}