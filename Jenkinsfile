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
            description: 'Select deployment action'
        )

        string(
            name: 'VERSION',
            defaultValue: '5.0',
            description: 'Application version'
        )

        choice(
            name: 'RUN_TESTS',
            choices: ['YES', 'NO'],
            description: 'Run application tests before deployment'
        )

        booleanParam(
            name: 'PRODUCTION_CONFIRMATION',
            defaultValue: false,
            description: 'Confirm production deployment'
        )
    }

    environment {

        DOCKER_IMAGE = "customer-app"

        DB_NAME = "customerdb"
        DB_USER = "customeruser"
        DB_PASSWORD = "customerpass"
        MYSQL_ROOT_PASSWORD = "rootpass"
    }

    stages {

        // ============================================================
        // 1. RESOLVE ENVIRONMENT CONFIGURATION
        // ============================================================

        stage('Resolve Configuration') {

            steps {

                script {

                    if (params.ENVIRONMENT == 'DEV') {

                        env.GIT_BRANCH_NAME = 'develop'
                        env.APP_CONTAINER = 'customer-app-dev'
                        env.DB_CONTAINER = 'customer-db-dev'
                        env.DOCKER_NETWORK = 'customer-dev-net'
                        env.DOCKER_VOLUME = 'customer-db-dev-data'
                        env.HOST_PORT = '8081'

                    }

                    else if (params.ENVIRONMENT == 'UAT') {

                        env.GIT_BRANCH_NAME = 'release'
                        env.APP_CONTAINER = 'customer-app-uat'
                        env.DB_CONTAINER = 'customer-db-uat'
                        env.DOCKER_NETWORK = 'customer-uat-net'
                        env.DOCKER_VOLUME = 'customer-db-uat-data'
                        env.HOST_PORT = '8082'

                    }

                    else if (params.ENVIRONMENT == 'PRODUCTION') {

                        env.GIT_BRANCH_NAME = 'main'
                        env.APP_CONTAINER = 'customer-app-prod'
                        env.DB_CONTAINER = 'customer-db-prod'
                        env.DOCKER_NETWORK = 'customer-prod-net'
                        env.DOCKER_VOLUME = 'customer-db-prod-data'
                        env.HOST_PORT = '8083'

                    }

                    echo "========================================"
                    echo "DEPLOYMENT CONFIGURATION"
                    echo "========================================"
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Action      : ${params.ACTION}"
                    echo "Version     : ${params.VERSION}"
                    echo "Git Branch  : ${env.GIT_BRANCH_NAME}"
                    echo "App         : ${env.APP_CONTAINER}"
                    echo "Database    : ${env.DB_CONTAINER}"
                    echo "Network     : ${env.DOCKER_NETWORK}"
                    echo "Volume      : ${env.DOCKER_VOLUME}"
                    echo "Port        : ${env.HOST_PORT}"
                    echo "Run Tests   : ${params.RUN_TESTS}"
                    echo "========================================"
                }
            }
        }


        // ============================================================
        // 2. DOCKER CHECK
        // ============================================================

        stage('Docker Check') {

            steps {

                bat '''
                    echo ========================================
                    echo DOCKER CHECK
                    echo ========================================

                    docker version

                    if errorlevel 1 (
                        echo ERROR: Docker is not available.
                        exit /b 1
                    )

                    docker info

                    if errorlevel 1 (
                        echo ERROR: Docker daemon is not running.
                        exit /b 1
                    )

                    echo Docker is available.
                '''
            }
        }


        // ============================================================
        // 3. CHECKOUT CORRECT APPLICATION BRANCH
        // ============================================================

        stage('Checkout Correct Branch') {

            steps {

                bat '''
                    echo ========================================
                    echo CHECKOUT APPLICATION BRANCH
                    echo ========================================

                    git fetch --all

                    git checkout -B "%GIT_BRANCH_NAME%" "origin/%GIT_BRANCH_NAME%"

                    if errorlevel 1 (
                        echo ERROR: Failed to checkout application branch.
                        exit /b 1
                    )

                    git branch --show-current

                    git log -1 --oneline

                    echo Application branch checked out successfully.
                '''
            }
        }


        // ============================================================
        // 4. RUN APPLICATION TESTS
        // ============================================================

        stage('Run Tests') {

            when {

                expression {

                    return params.RUN_TESTS == 'YES'

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
                      sh -c "pip install --no-cache-dir -r app/requirements.txt && pytest -v app"

                    if errorlevel 1 (
                        echo ERROR: Application tests failed.
                        exit /b 1
                    )

                    echo ========================================
                    echo APPLICATION TESTS PASSED
                    echo ========================================
                '''
            }
        }


        // ============================================================
        // 5. PRODUCTION CONFIRMATION
        // ============================================================

        stage('Production Confirmation') {

            when {

                expression {

                    return params.ENVIRONMENT == 'PRODUCTION'
                }
            }

            steps {

                script {

                    if (!params.PRODUCTION_CONFIRMATION) {

                        error(
                            "Production deployment requires PRODUCTION_CONFIRMATION=true"
                        )
                    }

                    echo "Production deployment confirmed."
                }
            }
        }


        // ============================================================
        // 6. CREATE DOCKER NETWORK
        // ============================================================

        stage('Create Docker Network') {

            steps {

                bat '''
                    echo ========================================
                    echo CREATE DOCKER NETWORK
                    echo ========================================

                    docker network inspect "%DOCKER_NETWORK%" >nul 2>&1

                    if errorlevel 1 (

                        echo Creating network %DOCKER_NETWORK%

                        docker network create "%DOCKER_NETWORK%"

                        if errorlevel 1 (
                            echo ERROR: Failed to create Docker network.
                            exit /b 1
                        )

                    ) else (

                        echo Network %DOCKER_NETWORK% already exists.

                    )

                    docker network inspect "%DOCKER_NETWORK%"
                '''
            }
        }


        // ============================================================
        // 7. CREATE DATABASE VOLUME
        // ============================================================

        stage('Create Database Volume') {

            steps {

                bat '''
                    echo ========================================
                    echo CREATE DATABASE VOLUME
                    echo ========================================

                    docker volume inspect "%DOCKER_VOLUME%" >nul 2>&1

                    if errorlevel 1 (

                        echo Creating volume %DOCKER_VOLUME%

                        docker volume create "%DOCKER_VOLUME%"

                        if errorlevel 1 (
                            echo ERROR: Failed to create Docker volume.
                            exit /b 1
                        )

                    ) else (

                        echo Volume %DOCKER_VOLUME% already exists.

                    )

                    docker volume inspect "%DOCKER_VOLUME%"
                '''
            }
        }


        // ============================================================
        // 8. DEPLOY DATABASE
        // ============================================================

        stage('Deploy Database') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo DEPLOY DATABASE
                    echo ========================================

                    docker rm -f "%DB_CONTAINER%" >nul 2>&1

                    docker run -d ^
                      --name "%DB_CONTAINER%" ^
                      --network "%DOCKER_NETWORK%" ^
                      --restart unless-stopped ^
                      -e MYSQL_ROOT_PASSWORD="%MYSQL_ROOT_PASSWORD%" ^
                      -e MYSQL_DATABASE="%DB_NAME%" ^
                      -e MYSQL_USER="%DB_USER%" ^
                      -e MYSQL_PASSWORD="%DB_PASSWORD%" ^
                      -v "%DOCKER_VOLUME%:/var/lib/mysql" ^
                      mysql:8.0

                    if errorlevel 1 (
                        echo ERROR: Failed to start database container.
                        exit /b 1
                    )

                    echo Waiting for MySQL database...

                    set DB_READY=0

                    for /L %%i in (1,1,30) do (

                        docker exec "%DB_CONTAINER%" ^
                          mysqladmin ping ^
                          -h 127.0.0.1 ^
                          -uroot ^
                          -p"%MYSQL_ROOT_PASSWORD%" ^
                          --silent >nul 2>&1

                        if not errorlevel 1 (

                            echo MySQL is ready.

                            set DB_READY=1

                            goto DB_READY

                        )

                        echo Waiting for MySQL... attempt %%i/30

                        timeout /t 2 /nobreak >nul
                    )

                    :DB_READY

                    if "%DB_READY%"=="0" (

                        echo ERROR: MySQL did not become ready.

                        docker logs "%DB_CONTAINER%"

                        exit /b 1
                    )

                    echo Database deployment successful.

                    docker ps --filter "name=%DB_CONTAINER%"
                '''
            }
        }


        // ============================================================
        // 9. DATABASE VALIDATION
        // ============================================================

        stage('Validate Database') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE DATABASE
                    echo ========================================

                    docker exec "%DB_CONTAINER%" ^
                      mysql ^
                      -uroot ^
                      -p"%MYSQL_ROOT_PASSWORD%" ^
                      -e "SELECT VERSION();"

                    if errorlevel 1 (
                        echo ERROR: Database validation failed.
                        exit /b 1
                    )

                    docker exec "%DB_CONTAINER%" ^
                      mysql ^
                      -uroot ^
                      -p"%MYSQL_ROOT_PASSWORD%" ^
                      -e "SHOW DATABASES;"

                    echo Database validation successful.
                '''
            }
        }


        // ============================================================
        // 10. BUILD APPLICATION IMAGE
        // ============================================================

        stage('Build Application Image') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo BUILD APPLICATION IMAGE
                    echo ========================================

                    docker build ^
                      --build-arg VERSION="%VERSION%" ^
                      -t "%DOCKER_IMAGE%:%VERSION%" ^
                      -t "%DOCKER_IMAGE%:latest" ^
                      .

                    if errorlevel 1 (
                        echo ERROR: Docker image build failed.
                        exit /b 1
                    )

                    docker images "%DOCKER_IMAGE%"
                '''
            }
        }


        // ============================================================
        // 11. DEPLOY APPLICATION
        // ============================================================

        stage('Deploy Application') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo DEPLOY APPLICATION
                    echo ========================================

                    docker rm -f "%APP_CONTAINER%" >nul 2>&1

                    docker run -d ^
                      --name "%APP_CONTAINER%" ^
                      --network "%DOCKER_NETWORK%" ^
                      -p "%HOST_PORT%:8080" ^
                      -e DB_HOST="%DB_CONTAINER%" ^
                      -e DB_PORT="3306" ^
                      -e DB_NAME="%DB_NAME%" ^
                      -e DB_USER="%DB_USER%" ^
                      -e DB_PASSWORD="%DB_PASSWORD%" ^
                      -e APP_ENV="%ENVIRONMENT%" ^
                      -e APP_VERSION="%VERSION%" ^
                      "%DOCKER_IMAGE%:%VERSION%"

                    if errorlevel 1 (
                        echo ERROR: Failed to start application container.
                        exit /b 1
                    )

                    echo Application container started.

                    docker ps --filter "name=%APP_CONTAINER%"
                '''
            }
        }


        // ============================================================
        // 12. VALIDATE APPLICATION CONTAINER
        // ============================================================

        stage('Validate Application Container') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE APPLICATION CONTAINER
                    echo ========================================

                    docker inspect "%APP_CONTAINER%" >nul 2>&1

                    if errorlevel 1 (
                        echo ERROR: Application container does not exist.
                        exit /b 1
                    )

                    docker inspect -f "{{.State.Running}}" "%APP_CONTAINER%"

                    if errorlevel 1 (
                        echo ERROR: Unable to inspect application container.
                        exit /b 1
                    )

                    docker inspect -f "{{.State.Running}}" "%APP_CONTAINER%" | findstr /I "true"

                    if errorlevel 1 (
                        echo ERROR: Application container is not running.
                        docker logs "%APP_CONTAINER%"
                        exit /b 1
                    )

                    echo Application container is running.
                '''
            }
        }


        // ============================================================
        // 13. VALIDATE DOCKER NETWORK
        // ============================================================

        stage('Validate Docker Network') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE DOCKER NETWORK
                    echo ========================================

                    docker network inspect "%DOCKER_NETWORK%"

                    if errorlevel 1 (
                        echo ERROR: Network inspection failed.
                        exit /b 1
                    )

                    echo Checking application container network...

                    docker inspect -f "{{json .NetworkSettings.Networks}}" "%APP_CONTAINER%"

                    echo Checking database container network...

                    docker inspect -f "{{json .NetworkSettings.Networks}}" "%DB_CONTAINER%"

                    echo Docker network validation completed.
                '''
            }
        }


        // ============================================================
        // 14. VALIDATE APP TO DATABASE CONNECTIVITY
        // ============================================================

        stage('Validate App to Database Connectivity') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE APP TO DATABASE CONNECTIVITY
                    echo ========================================

                    docker exec "%APP_CONTAINER%" ^
                      python -c "import socket; s=socket.create_connection(('%DB_CONTAINER%',3306),5); print('Database connection successful'); s.close()"

                    if errorlevel 1 (

                        echo ERROR: Application cannot connect to database.

                        docker logs "%APP_CONTAINER%"

                        exit /b 1
                    )

                    echo Application-to-database connectivity successful.
                '''
            }
        }


        // ============================================================
        // 15. HEALTH CHECK
        // ============================================================

        stage('Application Health Check') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo APPLICATION HEALTH CHECK
                    echo ========================================

                    timeout /t 3 /nobreak >nul

                    curl --fail --silent ^
                      "http://localhost:%HOST_PORT%/health"

                    if errorlevel 1 (

                        echo ERROR: Application health check failed.

                        docker logs "%APP_CONTAINER%"

                        exit /b 1
                    )

                    echo Application health check successful.
                '''
            }
        }


        // ============================================================
        // 16. VALIDATE ENVIRONMENT
        // ============================================================

        stage('Validate Environment') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE ENVIRONMENT
                    echo ========================================

                    curl --fail --silent ^
                      "http://localhost:%HOST_PORT%/environment"

                    if errorlevel 1 (
                        echo ERROR: Environment endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Environment validation completed.
                '''
            }
        }


        // ============================================================
        // 17. VALIDATE VERSION
        // ============================================================

        stage('Validate Version') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE VERSION
                    echo ========================================

                    curl --fail --silent ^
                      "http://localhost:%HOST_PORT%/version"

                    if errorlevel 1 (
                        echo ERROR: Version endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Expected version: %VERSION%

                    echo Version validation completed.
                '''
            }
        }


        // ============================================================
        // 18. VALIDATE CUSTOMER SEARCH
        // ============================================================

        stage('Validate Customer Search') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo VALIDATE CUSTOMER SEARCH
                    echo ========================================

                    curl --fail --silent ^
                      "http://localhost:%HOST_PORT%/customers/search?name=John"

                    if errorlevel 1 (
                        echo ERROR: Customer search endpoint failed.
                        exit /b 1
                    )

                    echo.
                    echo Customer search validation successful.
                '''
            }
        }


        // ============================================================
        // 19. SHOW DEPLOYMENT STATUS
        // ============================================================

        stage('Deployment Status') {

            when {

                expression {

                    return params.ACTION == 'DEPLOY'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo FINAL DEPLOYMENT STATUS
                    echo ========================================

                    echo.
                    echo DOCKER CONTAINERS
                    docker ps -a

                    echo.
                    echo APPLICATION CONTAINER
                    docker inspect "%APP_CONTAINER%"

                    echo.
                    echo DATABASE CONTAINER
                    docker inspect "%DB_CONTAINER%"

                    echo.
                    echo NETWORK
                    docker network inspect "%DOCKER_NETWORK%"

                    echo.
                    echo VOLUME
                    docker volume inspect "%DOCKER_VOLUME%"

                    echo.
                    echo ========================================
                    echo DEPLOYMENT SUCCESSFUL
                    echo ========================================
                    echo Environment : %ENVIRONMENT%
                    echo Version     : %VERSION%
                    echo Application : %APP_CONTAINER%
                    echo Database    : %DB_CONTAINER%
                    echo Port        : %HOST_PORT%
                    echo Network     : %DOCKER_NETWORK%
                    echo Volume      : %DOCKER_VOLUME%
                    echo ========================================
                '''
            }
        }


        // ============================================================
        // 20. ROLLBACK
        // ============================================================

        stage('Rollback') {

            when {

                expression {

                    return params.ACTION == 'ROLLBACK'
                }
            }

            steps {

                bat '''
                    echo ========================================
                    echo ROLLBACK
                    echo ========================================

                    echo Requested rollback version: %VERSION%

                    docker images "%DOCKER_IMAGE%"

                    docker image inspect "%DOCKER_IMAGE%:%VERSION%" >nul 2>&1

                    if errorlevel 1 (

                        echo ERROR: Rollback image %DOCKER_IMAGE%:%VERSION% does not exist.

                        exit /b 1
                    )

                    echo Rollback image exists.

                    docker rm -f "%APP_CONTAINER%" >nul 2>&1

                    docker run -d ^
                      --name "%APP_CONTAINER%" ^
                      --network "%DOCKER_NETWORK%" ^
                      -p "%HOST_PORT%:8080" ^
                      -e DB_HOST="%DB_CONTAINER%" ^
                      -e DB_PORT="3306" ^
                      -e DB_NAME="%DB_NAME%" ^
                      -e DB_USER="%DB_USER%" ^
                      -e DB_PASSWORD="%DB_PASSWORD%" ^
                      -e APP_ENV="%ENVIRONMENT%" ^
                      -e APP_VERSION="%VERSION%" ^
                      "%DOCKER_IMAGE%:%VERSION%"

                    if errorlevel 1 (
                        echo ERROR: Rollback deployment failed.
                        exit /b 1
                    )

                    timeout /t 3 /nobreak >nul

                    echo Validating rollback application...

                    docker inspect -f "{{.State.Running}}" "%APP_CONTAINER%" | findstr /I "true"

                    if errorlevel 1 (

                        echo ERROR: Rollback container is not running.

                        docker logs "%APP_CONTAINER%"

                        exit /b 1
                    )

                    curl --fail --silent ^
                      "http://localhost:%HOST_PORT%/health"

                    if errorlevel 1 (

                        echo ERROR: Rollback health check failed.

                        docker logs "%APP_CONTAINER%"

                        exit /b 1
                    )

                    echo.
                    echo ========================================
                    echo ROLLBACK SUCCESSFUL
                    echo ========================================
                    echo Environment : %ENVIRONMENT%
                    echo Version     : %VERSION%
                    echo Application : %APP_CONTAINER%
                    echo ========================================
                '''
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo "========================================"
            echo "JENKINS PIPELINE SUCCESSFUL"
            echo "========================================"
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Action      : ${params.ACTION}"
            echo "Version     : ${params.VERSION}"
            echo "========================================"
        }

        failure {

            echo "========================================"
            echo "JENKINS PIPELINE FAILED"
            echo "========================================"

            bat '''
                echo.
                echo ===== APPLICATION LOGS =====
                docker logs "%APP_CONTAINER%" 2>nul

                echo.
                echo ===== DATABASE LOGS =====
                docker logs "%DB_CONTAINER%" 2>nul

                echo.
                echo ===== DOCKER PS =====
                docker ps -a

                echo.
                echo ===== NETWORK =====
                docker network inspect "%DOCKER_NETWORK%" 2>nul

                echo.
                echo ===== VOLUME =====
                docker volume inspect "%DOCKER_VOLUME%" 2>nul
            '''

            echo "Failure logs collected."
        }

        always {

            echo "========================================"
            echo "PIPELINE COMPLETED"
            echo "========================================"
        }
    }
}