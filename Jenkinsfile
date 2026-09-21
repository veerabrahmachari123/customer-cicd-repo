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
            description: 'Required YES for production deployment'
        )
    }

    environment {
        REPO_URL = 'https://github.com/veerabrahmachari123/customer-cicd-repo.git'

        APP_IMAGE = 'customer-app'

        DEV_APP = 'customer-app-dev'
        DEV_DB = 'customer-db-dev'
        DEV_NETWORK = 'customer-dev-net'
        DEV_PORT = '8081'
        DEV_VOLUME = 'customer-db-dev-data'

        UAT_APP = 'customer-app-uat'
        UAT_DB = 'customer-db-uat'
        UAT_NETWORK = 'customer-uat-net'
        UAT_PORT = '8082'
        UAT_VOLUME = 'customer-db-uat-data'

        PROD_APP = 'customer-app-prod'
        PROD_DB = 'customer-db-prod'
        PROD_NETWORK = 'customer-prod-net'
        PROD_PORT = '8083'
        PROD_VOLUME = 'customer-db-prod-data'

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
                        env.APP_CONTAINER = env.DEV_APP
                        env.DB_CONTAINER = env.DEV_DB
                        env.DOCKER_NETWORK = env.DEV_NETWORK
                        env.HOST_PORT = env.DEV_PORT
                        env.DB_VOLUME = env.DEV_VOLUME
                        env.ENV_FILE = 'config/dev.env.example'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        env.GIT_BRANCH = 'release'
                        env.APP_CONTAINER = env.UAT_APP
                        env.DB_CONTAINER = env.UAT_DB
                        env.DOCKER_NETWORK = env.UAT_NETWORK
                        env.HOST_PORT = env.UAT_PORT
                        env.DB_VOLUME = env.UAT_VOLUME
                        env.ENV_FILE = 'config/uat.env.example'
                    }
                    else {
                        env.GIT_BRANCH = 'main'
                        env.APP_CONTAINER = env.PROD_APP
                        env.DB_CONTAINER = env.PROD_DB
                        env.DOCKER_NETWORK = env.PROD_NETWORK
                        env.HOST_PORT = env.PROD_PORT
                        env.DB_VOLUME = env.PROD_VOLUME
                        env.ENV_FILE = 'config/prod.env.example'
                    }

                    echo "========================================"
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Action      : ${params.ACTION}"
                    echo "Version     : ${params.VERSION}"
                    echo "Git Branch  : ${env.GIT_BRANCH}"
                    echo "App         : ${env.APP_CONTAINER}"
                    echo "Database    : ${env.DB_CONTAINER}"
                    echo "Network     : ${env.DOCKER_NETWORK}"
                    echo "Port        : ${env.HOST_PORT}"
                    echo "Volume      : ${env.DB_VOLUME}"
                    echo "========================================"

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
                        echo ERROR: Docker is not available.
                        exit /b 1
                    )

                    docker info
                    if errorlevel 1 (
                        echo ERROR: Docker Desktop is not running.
                        exit /b 1
                    )
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                script {
                    echo "Checking out branch: ${env.GIT_BRANCH}"
                }

                bat '''
                    @echo off

                    if exist .git (
                        echo Git repository already exists.
                    ) else (
                        git clone "%REPO_URL%" .
                        if errorlevel 1 exit /b 1
                    )

                    git fetch --all --prune
                    if errorlevel 1 exit /b 1

                    git checkout "%GIT_BRANCH%"
                    if errorlevel 1 (
                        git checkout -B "%GIT_BRANCH%" "origin/%GIT_BRANCH%"
                        if errorlevel 1 exit /b 1
                    )

                    git reset --hard "origin/%GIT_BRANCH%"
                    if errorlevel 1 exit /b 1

                    echo.
                    echo Current commit:
                    git log -1 --oneline

                    echo.
                    echo Git status:
                    git status
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

                    python --version

                    if not exist app\\requirements.txt (
                        echo ERROR: requirements.txt not found.
                        exit /b 1
                    )

                    python -m pip install -r app\\requirements.txt
                    if errorlevel 1 exit /b 1

                    python -m pytest app\\test_app.py -v
                    if errorlevel 1 (
                        echo ERROR: Tests failed.
                        exit /b 1
                    )
                '''
            }
        }

        stage('Capture Previous Deployment') {
            steps {
                bat '''
                    @echo off

                    echo Checking previous application image...

                    docker inspect "%APP_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo No previous application container found.
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
                        echo Creating Docker network %DOCKER_NETWORK%...
                        docker network create "%DOCKER_NETWORK%"
                        if errorlevel 1 (
                            echo ERROR: Failed to create Docker network.
                            exit /b 1
                        )
                    ) else (
                        echo Docker network already exists.
                    )

                    echo.
                    echo Network details:
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
                        echo Creating Docker volume %DB_VOLUME%...
                        docker volume create "%DB_VOLUME%"
                        if errorlevel 1 (
                            echo ERROR: Failed to create Docker volume.
                            exit /b 1
                        )
                    ) else (
                        echo Docker volume already exists.
                    )

                    echo.
                    echo Volume details:
                    docker volume inspect "%DB_VOLUME%"
                '''
            }
        }

        stage('Build Application Image') {
            steps {
                bat '''
                    @echo off

                    echo Building image %APP_IMAGE%:%VERSION% ...

                    docker build --build-arg VERSION="%VERSION%" -t "%APP_IMAGE%:%VERSION%" .
                    if errorlevel 1 (
                        echo ERROR: Docker image build failed.
                        exit /b 1
                    )

                    echo.
                    echo Verifying image...

                    docker image inspect "%APP_IMAGE%:%VERSION%"
                    if errorlevel 1 (
                        echo ERROR: Docker image does not exist.
                        exit /b 1
                    )
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
                            echo ERROR: Database container creation failed.
                            exit /b 1
                        )
                    ) else (
                        echo Database container already exists.
                    )

                    echo.
                    echo Checking database network membership...

                    docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}" | findstr /I /X "%DB_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo Connecting database to network...
                        docker network connect "%DOCKER_NETWORK%" "%DB_CONTAINER%"
                        if errorlevel 1 (
                            echo ERROR: Failed to connect database to network.
                            exit /b 1
                        )
                    ) else (
                        echo Database is already connected to network.
                    )

                    echo.
                    echo Starting database...

                    docker start "%DB_CONTAINER%" >nul 2>&1

                    echo.
                    echo Waiting for MySQL...

                    set DB_READY=0

                    for /L %%i in (1,1,30) do (
                        docker exec "%DB_CONTAINER%" mysqladmin ping -h localhost -u root -p"%DB_ROOT_PASSWORD%" --silent >nul 2>&1

                        if not errorlevel 1 (
                            echo Database is READY.
                            set DB_READY=1
                            goto DBREADY
                        )

                        echo Waiting for database... attempt %%i of 30
                        timeout /t 2 /nobreak >nul
                    )

                    :DBREADY

                    if "%DB_READY%"=="0" (
                        echo ERROR: Database did not become ready.
                        docker logs "%DB_CONTAINER%"
                        exit /b 1
                    )

                    echo.
                    echo Database status:
                    docker ps --filter "name=%DB_CONTAINER%"
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                bat '''
                    @echo off

                    echo Removing old application container if present...

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
                        echo ERROR: Application container failed to start.
                        exit /b 1
                    )

                    echo.
                    echo Application container:
                    docker ps --filter "name=%APP_CONTAINER%"

                    echo.
                    echo Application logs:
                    docker logs "%APP_CONTAINER%"
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

                    echo App running: %APP_RUNNING%

                    if /I not "%APP_RUNNING%"=="true" (
                        echo ERROR: Application container is not running.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    docker inspect "%DB_CONTAINER%" --format="{{.State.Running}}" > db-running.txt
                    set /p DB_RUNNING=<db-running.txt

                    echo DB running: %DB_RUNNING%

                    if /I not "%DB_RUNNING%"=="true" (
                        echo ERROR: Database container is not running.
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

                    type network-containers.txt

                    findstr /I /X "%APP_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not connected to correct network.
                        exit /b 1
                    )

                    findstr /I /X "%DB_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not connected to correct network.
                        exit /b 1
                    )

                    echo.
                    echo Correct network verified.
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo HEALTH CHECK
                    echo ========================================

                    timeout /t 5 /nobreak >nul

                    curl.exe --fail --silent --show-error "http://localhost:%HOST_PORT%/health"

                    if errorlevel 1 (
                        echo ERROR: Health endpoint failed.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    echo.
                    echo Health endpoint succeeded.
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
                    echo Application can reach database using Docker DNS.
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo VALIDATING ENVIRONMENT
                    echo ========================================

                    echo Expected environment: %ENVIRONMENT%
                    echo Expected version: %VERSION%

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/environment"

                    if errorlevel 1 (
                        echo ERROR: Environment endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Version endpoint:

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/version"

                    if errorlevel 1 (
                        echo ERROR: Version endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Environment and version endpoints succeeded.
                '''
            }
        }

        stage('Validate Customer Search') {
            steps {
                bat '''
                    @echo off

                    echo ========================================
                    echo CUSTOMER SEARCH
                    echo ========================================

                    curl.exe --fail --silent "http://localhost:%HOST_PORT%/customers/search?name=John"

                    if errorlevel 1 (
                        echo ERROR: Customer search failed.
                        exit /b 1
                    )

                    echo.
                    echo Customer search succeeded.
                '''
            }
        }

        stage('Deployment Evidence') {
            steps {
                bat '''
                    @echo off

                    echo Creating deployment evidence...

                    (
                        echo Environment: %ENVIRONMENT%
                        echo Action: %ACTION%
                        echo Version: %VERSION%
                        echo Git Branch: %GIT_BRANCH%
                        echo Application Container: %APP_CONTAINER%
                        echo Database Container: %DB_CONTAINER%
                        echo Docker Network: %DOCKER_NETWORK%
                        echo Docker Volume: %DB_VOLUME%
                        echo Host Port: %HOST_PORT%
                        echo.
                        echo Docker Containers:
                        docker ps
                        echo.
                        echo Docker Network:
                        docker network inspect "%DOCKER_NETWORK%"
                        echo.
                        echo Docker Volume:
                        docker volume inspect "%DB_VOLUME%"
                        echo.
                        echo Docker Images:
                        docker images "%APP_IMAGE%"
                    ) > deployment-evidence.txt

                    type deployment-evidence.txt
                '''

                archiveArtifacts artifacts: 'deployment-evidence.txt,previous-image.txt,network-containers.txt,app-running.txt,db-running.txt',
                    allowEmptyArchive: true
            }
        }
    }

    post {

        success {
            echo "========================================"
            echo "DEPLOYMENT SUCCESSFUL"
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Version     : ${params.VERSION}"
            echo "Application : ${env.APP_CONTAINER}"
            echo "Database    : ${env.DB_CONTAINER}"
            echo "Network     : ${env.DOCKER_NETWORK}"
            echo "Port        : ${env.HOST_PORT}"
            echo "========================================"
        }

        failure {
            script {
                echo "========================================"
                echo "DEPLOYMENT FAILED"
                echo "========================================"

                bat '''
                    @echo off

                    echo Application logs:
                    docker logs "%APP_CONTAINER%" > failure-app-logs.txt 2>&1

                    echo Database logs:
                    docker logs "%DB_CONTAINER%" > failure-db-logs.txt 2>&1

                    echo Container status:
                    docker ps -a > failure-containers.txt 2>&1
                '''

                archiveArtifacts artifacts: 'failure-app-logs.txt,failure-db-logs.txt,failure-containers.txt',
                    allowEmptyArchive: true

                if (params.ENVIRONMENT == 'PRODUCTION' &&
                    params.ACTION == 'DEPLOY') {

                    echo "Production deployment failed."
                    echo "Attempting automatic rollback..."

                    bat '''
                        @echo off

                        if not exist previous-image.txt (
                            echo No previous image information available.
                            exit /b 1
                        )

                        set /p PREVIOUS_IMAGE=<previous-image.txt

                        echo Previous image: %PREVIOUS_IMAGE%

                        if "%PREVIOUS_IMAGE%"=="NONE" (
                            echo No previous production image available.
                            exit /b 1
                        )

                        echo Removing failed application...

                        docker rm -f "%APP_CONTAINER%" >nul 2>&1

                        echo Starting previous application image...

                        docker run -d ^
                            --name "%APP_CONTAINER%" ^
                            --network "%DOCKER_NETWORK%" ^
                            -p "%HOST_PORT%:8080" ^
                            -e APP_ENV="%ENVIRONMENT%" ^
                            -e DB_HOST="%DB_CONTAINER%" ^
                            -e DB_PORT="3306" ^
                            -e DB_NAME="%DB_NAME%" ^
                            -e DB_USER="%DB_USER%" ^
                            -e DB_PASSWORD="%DB_PASSWORD%" ^
                            "%PREVIOUS_IMAGE%"

                        if errorlevel 1 (
                            echo ERROR: Rollback container failed to start.
                            exit /b 1
                        )

                        timeout /t 5 /nobreak >nul

                        echo Checking rollback health...

                        curl.exe --fail --silent "http://localhost:%HOST_PORT%/health"

                        if errorlevel 1 (
                            echo ERROR: Rollback health check failed.
                            docker logs "%APP_CONTAINER%"
                            exit /b 1
                        )

                        echo ROLLBACK SUCCESSFUL.
                        echo Restored image: %PREVIOUS_IMAGE%
                    '''

                    echo "Production rollback completed."
                }
            }
        }

        always {
            echo "Pipeline completed."
        }
    }
}