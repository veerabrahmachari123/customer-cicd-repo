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
            description: 'Application version/tag'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests before deployment'
        )

        choice(
            name: 'PRODUCTION_CONFIRMATION',
            choices: ['NO', 'YES'],
            description: 'Required confirmation for production deployment'
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
                        env.DOCKER_VOLUME = 'customer-db-dev-data'
                        env.APP_PORT = '8081'
                    }
                    else if (params.ENVIRONMENT == 'UAT') {
                        env.GIT_BRANCH = 'release'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.DOCKER_NETWORK = 'customer-uat-net'
                        env.DOCKER_VOLUME = 'customer-db-uat-data'
                        env.APP_PORT = '8082'
                    }
                    else if (params.ENVIRONMENT == 'PRODUCTION') {
                        env.GIT_BRANCH = 'main'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.DOCKER_NETWORK = 'customer-prod-net'
                        env.DOCKER_VOLUME = 'customer-db-prod-data'
                        env.APP_PORT = '8083'

                        if (params.PRODUCTION_CONFIRMATION != 'YES') {
                            error('Production deployment requires PRODUCTION_CONFIRMATION=YES')
                        }
                    }

                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Action      : ${params.ACTION}"
                    echo "Version     : ${params.VERSION}"
                    echo "Git Branch  : ${env.GIT_BRANCH}"
                    echo "App         : ${env.APP_CONTAINER}"
                    echo "Database    : ${env.DB_CONTAINER}"
                    echo "Network     : ${env.DOCKER_NETWORK}"
                    echo "Volume      : ${env.DOCKER_VOLUME}"
                    echo "Port        : ${env.APP_PORT}"
                }
            }
        }

        stage('Docker Check') {
            steps {
                bat '''
                    docker version
                    docker info
                    echo Docker is ready.
                '''
            }
        }

        stage('Checkout Correct Branch') {
            steps {
                bat '''
                    echo Fetching repository...

                    if not exist .git (
                        git init
                    )

                    git remote remove origin 2>nul
                    git remote add origin "%REPO_URL%"

                    git fetch --prune origin

                    echo Checking out %GIT_BRANCH%...

                    git checkout -B "%GIT_BRANCH%" "origin/%GIT_BRANCH%"
                    git reset --hard "origin/%GIT_BRANCH%"

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
                    echo ========================================
                    echo RUNNING APPLICATION TESTS
                    echo ========================================

                    docker run --rm ^
                      -v "%CD%:/workspace" ^
                      -w /workspace ^
                      python:3.12-slim ^
                      sh -c "pip install --no-cache-dir -r app/requirements.txt && python -m unittest discover -s app -p 'test_*.py' -v"

                    if errorlevel 1 (
                        echo ERROR: Application tests failed.
                        exit /b 1
                    )

                    echo Application tests passed.
                '''
            }
        }

        stage('Capture Previous Deployment') {
            steps {
                bat '''
                    echo Capturing previous deployment information...

                    docker inspect "%APP_CONTAINER%" --format="{{.Config.Image}}" > previous-image.txt 2>nul

                    if exist previous-image.txt (
                        echo Previous image:
                        type previous-image.txt
                    ) else (
                        echo No previous application container found.
                        echo NONE > previous-image.txt
                    )
                '''
            }
        }

        stage('Prepare Docker Network') {
            steps {
                bat '''
                    echo Preparing Docker network...

                    docker network inspect "%DOCKER_NETWORK%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating network %DOCKER_NETWORK%...
                        docker network create "%DOCKER_NETWORK%"
                    ) else (
                        echo Network %DOCKER_NETWORK% already exists.
                    )

                    docker network inspect "%DOCKER_NETWORK%"
                '''
            }
        }

        stage('Prepare Docker Volume') {
            steps {
                bat '''
                    echo Preparing Docker volume...

                    docker volume inspect "%DOCKER_VOLUME%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating volume %DOCKER_VOLUME%...
                        docker volume create "%DOCKER_VOLUME%"
                    ) else (
                        echo Volume %DOCKER_VOLUME% already exists.
                    )

                    docker volume inspect "%DOCKER_VOLUME%"
                '''
            }
        }

        stage('Build Application Image') {
            steps {
                bat '''
                    echo ========================================
                    echo BUILDING APPLICATION IMAGE
                    echo ========================================

                    docker build ^
                      --build-arg VERSION="%VERSION%" ^
                      -t "%APP_IMAGE%:%VERSION%" ^
                      -t "%APP_IMAGE%:%ENVIRONMENT%" ^
                      .

                    if errorlevel 1 (
                        echo ERROR: Docker image build failed.
                        exit /b 1
                    )

                    echo Built image:
                    docker image inspect "%APP_IMAGE%:%VERSION%" --format="{{.Id}}"

                    docker images "%APP_IMAGE%"
                '''
            }
        }

        stage('Deploy Database') {
            steps {
                bat '''
                    echo ========================================
                    echo DEPLOYING DATABASE
                    echo ========================================

                    docker inspect "%DB_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo Creating database container...

                        docker run -d ^
                          --name "%DB_CONTAINER%" ^
                          --network "%DOCKER_NETWORK%" ^
                          -v "%DOCKER_VOLUME%:/var/lib/mysql" ^
                          -e MYSQL_DATABASE="%DB_NAME%" ^
                          -e MYSQL_USER="%DB_USER%" ^
                          -e MYSQL_PASSWORD="%DB_PASSWORD%" ^
                          -e MYSQL_ROOT_PASSWORD="%DB_ROOT_PASSWORD%" ^
                          "%DB_IMAGE%"
                    ) else (
                        echo Database container already exists.

                        docker start "%DB_CONTAINER%" >nul 2>&1
                    )

                    echo Checking database network membership...

                    docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}" | findstr /I /X "%DB_CONTAINER%" >nul

                    if errorlevel 1 (
                        echo Connecting database to network...
                        docker network connect "%DOCKER_NETWORK%" "%DB_CONTAINER%"
                    ) else (
                        echo Database is already connected to the correct network.
                    )

                    echo Waiting for MySQL...

                    set DB_READY=0

                    for /L %%i in (1,1,30) do (
                        docker exec "%DB_CONTAINER%" mysqladmin ping -h localhost -u root -p%DB_ROOT_PASSWORD% --silent >nul 2>&1

                        if not errorlevel 1 (
                            echo MySQL is ready.
                            set DB_READY=1
                            goto DB_READY
                        )

                        echo Waiting for MySQL attempt %%i of 30...
                        timeout /t 2 /nobreak >nul
                    )

                    :DB_READY

                    if "%DB_READY%"=="0" (
                        echo ERROR: MySQL did not become ready.
                        docker logs "%DB_CONTAINER%"
                        exit /b 1
                    )

                    echo Database deployment completed.
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                bat '''
                    echo ========================================
                    echo DEPLOYING APPLICATION
                    echo ========================================

                    docker rm -f "%APP_CONTAINER%" >nul 2>&1

                    docker run -d ^
                      --name "%APP_CONTAINER%" ^
                      --network "%DOCKER_NETWORK%" ^
                      -p "%APP_PORT%:8080" ^
                      -e DB_HOST="%DB_CONTAINER%" ^
                      -e DB_PORT="3306" ^
                      -e DB_NAME="%DB_NAME%" ^
                      -e DB_USER="%DB_USER%" ^
                      -e DB_PASSWORD="%DB_PASSWORD%" ^
                      -e APP_ENVIRONMENT="%ENVIRONMENT%" ^
                      -e APP_VERSION="%VERSION%" ^
                      "%APP_IMAGE%:%VERSION%"

                    if errorlevel 1 (
                        echo ERROR: Application deployment failed.
                        exit /b 1
                    )

                    echo Application container started.

                    docker ps --filter "name=%APP_CONTAINER%"
                '''
            }
        }

        stage('Validate Containers') {
            steps {
                bat '''
                    echo ========================================
                    echo VALIDATING CONTAINERS
                    echo ========================================

                    docker inspect "%APP_CONTAINER%" --format="{{.State.Running}}" > app-running.txt

                    set /p APP_RUNNING=<app-running.txt

                    if /I not "%APP_RUNNING%"=="true" (
                        echo ERROR: Application container is not running.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    docker inspect "%DB_CONTAINER%" --format="{{.State.Running}}" > db-running.txt

                    set /p DB_RUNNING=<db-running.txt

                    if /I not "%DB_RUNNING%"=="true" (
                        echo ERROR: Database container is not running.
                        docker logs "%DB_CONTAINER%"
                        exit /b 1
                    )

                    echo Both containers are running.
                    docker ps --filter "name=%APP_CONTAINER%" --filter "name=%DB_CONTAINER%"
                '''
            }
        }

        stage('Validate Network') {
            steps {
                bat '''
                    echo ========================================
                    echo VALIDATING NETWORK
                    echo ========================================

                    docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}" > network-containers.txt

                    echo Connected containers:
                    type network-containers.txt

                    findstr /I /X "%APP_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Application is not connected to %DOCKER_NETWORK%.
                        exit /b 1
                    )

                    findstr /I /X "%DB_CONTAINER%" network-containers.txt >nul

                    if errorlevel 1 (
                        echo ERROR: Database is not connected to %DOCKER_NETWORK%.
                        exit /b 1
                    )

                    echo Both containers are connected to the correct network.
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    echo ========================================
                    echo HEALTH CHECK
                    echo ========================================

                    echo Waiting for application...

                    set HEALTH_OK=0

                    for /L %%i in (1,1,30) do (
                        curl.exe -s -f "http://localhost:%APP_PORT%/health" > health-response.txt 2>nul

                        if not errorlevel 1 (
                            echo Application health check passed.
                            set HEALTH_OK=1
                            goto HEALTH_READY
                        )

                        echo Waiting for application attempt %%i of 30...
                        timeout /t 2 /nobreak >nul
                    )

                    :HEALTH_READY

                    if "%HEALTH_OK%"=="0" (
                        echo ERROR: Application health check failed.
                        type health-response.txt 2>nul
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Health response:
                    type health-response.txt
                '''
            }
        }

        stage('Validate App To DB Connectivity') {
            steps {
                bat '''
                    echo ========================================
                    echo VALIDATING APP TO DATABASE CONNECTIVITY
                    echo ========================================

                    docker exec "%APP_CONTAINER%" python -c "import socket; s=socket.create_connection(('%DB_CONTAINER%',3306),5); print('Database connection successful'); s.close()"

                    if errorlevel 1 (
                        echo ERROR: Application cannot connect to database.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Application-to-database connectivity validated.
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                bat '''
                    echo ========================================
                    echo VALIDATING ENVIRONMENT
                    echo ========================================

                    echo Environment response:
                    curl.exe -s "http://localhost:%APP_PORT%/environment"

                    echo.

                    echo Version response:
                    curl.exe -s "http://localhost:%APP_PORT%/version"

                    echo.

                    curl.exe -s "http://localhost:%APP_PORT%/environment" | findstr /I "%ENVIRONMENT%" >nul

                    if errorlevel 1 (
                        echo ERROR: Environment validation failed.
                        exit /b 1
                    )

                    curl.exe -s "http://localhost:%APP_PORT%/version" | findstr /I "%VERSION%" >nul

                    if errorlevel 1 (
                        echo ERROR: Version validation failed.
                        exit /b 1
                    )

                    echo Environment and version validation passed.
                '''
            }
        }

        stage('Validate Customer Search') {
            steps {
                bat '''
                    echo ========================================
                    echo VALIDATING CUSTOMER SEARCH
                    echo ========================================

                    curl.exe -s -f "http://localhost:%APP_PORT%/customers/search?name=John" > customer-search-response.txt

                    if errorlevel 1 (
                        echo ERROR: Customer search endpoint failed.
                        type customer-search-response.txt 2>nul
                        exit /b 1
                    )

                    echo Customer search response:
                    type customer-search-response.txt

                    echo.
                    echo Customer search validation passed.
                '''
            }
        }

        stage('Deployment Evidence') {
            steps {
                bat '''
                    echo ========================================
                    echo COLLECTING DEPLOYMENT EVIDENCE
                    echo ========================================

                    echo Environment=%ENVIRONMENT% > deployment-evidence.txt
                    echo Version=%VERSION% >> deployment-evidence.txt
                    echo Branch=%GIT_BRANCH% >> deployment-evidence.txt
                    echo AppContainer=%APP_CONTAINER% >> deployment-evidence.txt
                    echo DBContainer=%DB_CONTAINER% >> deployment-evidence.txt
                    echo Network=%DOCKER_NETWORK% >> deployment-evidence.txt
                    echo Volume=%DOCKER_VOLUME% >> deployment-evidence.txt
                    echo Port=%APP_PORT% >> deployment-evidence.txt

                    echo. >> deployment-evidence.txt
                    echo Containers: >> deployment-evidence.txt
                    docker ps --filter "name=%APP_CONTAINER%" --filter "name=%DB_CONTAINER%" >> deployment-evidence.txt

                    echo. >> deployment-evidence.txt
                    echo Network: >> deployment-evidence.txt
                    docker network inspect "%DOCKER_NETWORK%" >> deployment-evidence.txt

                    echo. >> deployment-evidence.txt
                    echo Volume: >> deployment-evidence.txt
                    docker volume inspect "%DOCKER_VOLUME%" >> deployment-evidence.txt

                    echo. >> deployment-evidence.txt
                    echo Application image: >> deployment-evidence.txt
                    docker image inspect "%APP_IMAGE%:%VERSION%" >> deployment-evidence.txt

                    echo Deployment evidence collected.
                '''
            }
        }
    }

    post {
        success {
            echo '========================================'
            echo 'DEPLOYMENT COMPLETED SUCCESSFULLY'
            echo '========================================'

            bat '''
                echo Containers:
                docker ps --filter "name=%APP_CONTAINER%" --filter "name=%DB_CONTAINER%"

                echo.
                echo Network:
                docker network inspect "%DOCKER_NETWORK%" --format="{{range .Containers}}{{.Name}}{{println}}{{end}}"

                echo.
                echo Volume:
                docker volume inspect "%DOCKER_VOLUME%"
            '''

            archiveArtifacts artifacts: 'deployment-evidence.txt,previous-image.txt,network-containers.txt,app-running.txt,db-running.txt,health-response.txt,customer-search-response.txt',
                             allowEmptyArchive: true
        }

        failure {
            echo '========================================'
            echo 'DEPLOYMENT FAILED'
            echo '========================================'

            bat '''
                echo Collecting failure information...

                docker ps -a > failure-containers.txt 2>&1

                docker logs "%APP_CONTAINER%" > failure-app-logs.txt 2>&1
                docker logs "%DB_CONTAINER%" > failure-db-logs.txt 2>&1
            '''

            archiveArtifacts artifacts: 'failure-app-logs.txt,failure-db-logs.txt,failure-containers.txt,previous-image.txt',
                             allowEmptyArchive: true
        }

        always {
            echo 'Pipeline completed.'
        }
    }
}