pipeline {
    agent any
    
    parameters {
        choice(name: 'DEPLOYMENT_ACTION', choices: ['DEPLOY', 'ROLLBACK'], description: 'Choose the action to perform.')
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'UAT', 'PRODUCTION'], description: 'Target deployment environment.')
        string(name: 'VERSION', defaultValue: '5.0', description: 'Enter the Git branch, tag, or version name to validate.')
        choice(name: 'CONFIRM_PROD', choices: ['NO', 'YES'], description: 'Explicit approval required for PRODUCTION deployments.')
    }

    environment {
        IMAGE_NAME = 'customer-app'
        CONTAINER_NAME = "customer-app-${params.ENVIRONMENT.toLowerCase()}"
        // Map native host ports precisely out of architecture spec sheets
        APP_PORT = "${params.ENVIRONMENT == 'PRODUCTION' ? '8083' : (params.ENVIRONMENT == 'UAT' ? '8082' : '8081')}"
        OLD_VERSION = 'Unknown'
        NEW_VERSION = "${params.VERSION}"
    }

    stages {
        stage('Guardrails & Validation') {
            steps {
                script {
                    // 1. Production Approval Gate
                    if (params.ENVIRONMENT == 'PRODUCTION' && params.DEPLOYMENT_ACTION == 'DEPLOY' && params.CONFIRM_PROD != 'YES') {
                        error "Deployment ABORTED: Production deployment requested but CONFIRM_PROD was not set to YES."
                    }
                    
                    // 2. Identify selected Git Commit automatically
                    echo "Validating workspace code state..."
                    def commitHash = bat(script: "@git rev-parse HEAD", returnStdout: true).trim()
                    echo "Successfully validated target code commit hash: ${commitHash}"
                }
            }
        }

        stage('Build Docker Image') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                // 3. Build image using unique tag matching repository conventions
                bat "docker build -t ${IMAGE_NAME}:${params.VERSION} ."
            }
        }

        stage('Record Audit State') {
            steps {
                script {
                    // 4. Record the previous image version before modifying active runtimes
                    def inspectCmd = "@docker inspect --format=\"{{.Config.Image}}\" ${env.CONTAINER_NAME}"
                    try {
                        def output = bat(script: inspectCmd, returnStdout: true).trim()
                        env.OLD_VERSION = output.tokenize(':')[-1]
                        echo "Audited Architecture: Current active version running is ${env.OLD_VERSION}"
                    } catch (Exception e) {
                        echo "No previous active container instance found. Defaulting old version to none."
                        env.OLD_VERSION = "None (Fresh Setup)"
                    }
                }
            }
        }

        stage('Execute Deployment Flow') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                script {
                    def tempContainer = "${env.CONTAINER_NAME}_new"
                    
                    // CRITICAL FIX: Allocate a non-conflicting staging buffer port (8089) 
                    // This separates the test inspection layer from active port bindings to prevent crash 125.
                    def stagingPort = "8089" 
                    
                    echo "Cleaning out lingering temporary staging structures..."
                    bat "docker rm -f ${tempContainer} 2>nul || exit 0"
                    
                    echo "Launching validation container on isolated staging port ${stagingPort}..."
                    bat "docker run -d --name ${tempContainer} -p ${stagingPort}:8080 ${IMAGE_NAME}:${params.VERSION}"
                    
                    // 5. Perform application health check
                    def healthCheckPassed = false
                    for (int i = 0; i < 6; i++) {
                        sleep 5
                        echo "Performing health probe attempt ${i+1}/6 on staging port ${stagingPort}..."
                        
                        // Escaped double percentage sign (%%) for Windows cmd/bat environment parsing stability
                        def statusCode = bat(script: "@curl -s -o NUL -w \"%%{http_code}\" http://localhost:${stagingPort}/health", returnStdout: true).trim()
                        
                        if (statusCode == "200") {
                            healthCheckPassed = true
                            break
                        }
                        echo "Health check status caught: (${statusCode}). Retrying..."
                    }
                    
                    // 6. Automatic rollback handling if health validation fails
                    if (!healthCheckPassed) {
                        bat "docker stop ${tempContainer} && docker rm ${tempContainer}"
                        currentBuild.description = 'HEALTH_CHECK_FAILED_TRIGGERING_ROLLBACK'
                        error "Deployment failed health validation. Automated rollback executed."
                    } else {
                        echo "Health validation cleared. Swapping production layers..."
                        
                        // Clean out the old container block actively occupying the destination host port
                        bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                        bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                        
                        // Clean down the temporary test buffer template
                        bat "docker stop ${tempContainer} 2>nul || exit 0"
                        bat "docker rm ${tempContainer} 2>nul || exit 0"
                        
                        // Re-launch cleanly on the core assigned operational host port (8081, 8082, or 8083)
                        bat "docker run -d --name ${env.CONTAINER_NAME} -p ${env.APP_PORT}:8080 ${IMAGE_NAME}:${params.VERSION}"
                        currentBuild.description = 'DEPLOYMENT_SUCCESSFUL'
                    }
                }
            }
        }

        stage('Manual Rollback Engine') {
            when { expression { params.DEPLOYMENT_ACTION == 'ROLLBACK' } }
            steps {
                script {
                    currentBuild.description = 'MANUAL_ROLLBACK_EXECUTING'
                    if (env.OLD_VERSION == "None (Fresh Setup)" || env.OLD_VERSION == "Unknown") { 
                        error "Rollback aborted: No history recorded for this cluster deployment profile." 
                    }
                    bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker run -d --name ${env.CONTAINER_NAME} -p ${env.APP_PORT}:8080 ${IMAGE_NAME}:${env.OLD_VERSION}"
                    currentBuild.description = 'MANUAL_ROLLBACK_COMPLETE'
                }
            }
        }
    }

    post {
        always {
            script {
                // 7. Extract build description details cleanly for the console summary block
                def finalState = currentBuild.description ?: 'NOT STARTED / ABORTED'
                echo """
                =======================================================
                📋 PIPELINE EXECUTION SUMMARY
                =======================================================
                ENVIRONMENT:   ${params.ENVIRONMENT}
                ACTION TAKEN:  ${params.DEPLOYMENT_ACTION}
                OLD VERSION:   ${env.OLD_VERSION}
                NEW VERSION:   ${env.NEW_VERSION}
                FINAL STATE:   ${finalState}
                =======================================================
                """
            }
        }
    }
}
