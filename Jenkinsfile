pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOYMENT_ACTION', choices: ['DEPLOY', 'ROLLBACK'], description: 'Choose the action to perform.')
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'UAT', 'PRODUCTION'], description: 'Target deployment environment.')
        string(name: 'VERSION', defaultValue: '5.0', description: 'Version tag to deploy (ignored during ROLLBACK).')
        string(name: 'ROLLBACK_VERSION', defaultValue: '', description: 'Explicit version/tag to revert to when action is ROLLBACK.')
        choice(name: 'CONFIRM_PROD', choices: ['NO', 'YES'], description: 'Explicit approval required for PRODUCTION operations.')
    }

    environment {
        IMAGE_NAME     = 'customer-app'
        CONTAINER_NAME = "customer-app-${params.ENVIRONMENT ? params.ENVIRONMENT.toLowerCase() : 'dev'}"
        APP_PORT       = "${params.ENVIRONMENT == 'PRODUCTION' ? '9083' : (params.ENVIRONMENT == 'UAT' ? '9082' : '9081')}"
        STAGING_PORT   = '8089'
        CURRENT_ACTIVE = 'Unknown'
        TARGET_VERSION = "${params.DEPLOYMENT_ACTION == 'DEPLOY' ? params.VERSION : params.ROLLBACK_VERSION}"
    }

    stages {
        stage('Guardrails & Validation') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' && params.CONFIRM_PROD != 'YES') {
                        error "ABORTED: Production deployment or rollback requested without setting CONFIRM_PROD=YES."
                    }

                    if (params.DEPLOYMENT_ACTION == 'ROLLBACK' && !params.ROLLBACK_VERSION?.trim()) {
                        error "ABORTED: Rollback action selected, but 'ROLLBACK_VERSION' was left empty."
                    }

                    echo "Validating target commit hash..."
                    def commitHash = bat(script: "@git rev-parse HEAD", returnStdout: true).trim()
                    echo "Target source commit: ${commitHash}"
                }
            }
        }

        stage('Record Audit State') {
            steps {
                script {
                    def inspectCmd = "@docker inspect --format=\"{{.Config.Image}}\" ${env.CONTAINER_NAME}"
                    try {
                        def output = bat(script: inspectCmd, returnStdout: true).trim()
                        env.CURRENT_ACTIVE = output.contains(':') ? output.tokenize(':')[-1] : output
                        echo "Currently active version in ${params.ENVIRONMENT}: ${env.CURRENT_ACTIVE}"
                    } catch (Exception e) {
                        echo "No active container found for ${env.CONTAINER_NAME}. Fresh deployment detected."
                        env.CURRENT_ACTIVE = "None (Fresh Setup)"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                bat "docker build -t ${IMAGE_NAME}:${params.VERSION} ."
            }
        }

        stage('Execute Deployment Flow') {
            when { expression { params.DEPLOYMENT_ACTION == 'DEPLOY' } }
            steps {
                script {
                    def tempContainer = "${env.CONTAINER_NAME}_staging"

                    echo "Removing stale staging container if present..."
                    bat "docker rm -f ${tempContainer} 2>nul || exit 0"

                    echo "Spinning up validation container on port ${env.STAGING_PORT}..."
                    bat "docker run -d --name ${tempContainer} -p ${env.STAGING_PORT}:8080 ${IMAGE_NAME}:${params.VERSION}"

                    // Health check validation loop
                    def healthCheckPassed = false
                    for (int i = 0; i < 6; i++) {
                        sleep 5
                        echo "Health check attempt ${i + 1}/6..."
                        def statusCode = bat(script: "@curl -s -o NUL -w \"%%{http_code}\" http://localhost:${env.STAGING_PORT}/health", returnStdout: true).trim()

                        if (statusCode == "200") {
                            healthCheckPassed = true
                            break
                        }
                    }

                    if (!healthCheckPassed) {
                        bat "docker rm -f ${tempContainer} 2>nul || exit 0"
                        currentBuild.description = 'HEALTH_CHECK_FAILED_DEPLOYMENT_REJECTED'
                        error "Deployment failed health validation on staging port. Active instance was not modified."
                    }

                    echo "Health check succeeded. Swapping traffic to active port..."
                    bat "docker rm -f ${tempContainer} 2>nul || exit 0"
                    bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker run -d --name ${env.CONTAINER_NAME} -p ${env.APP_PORT}:8080 ${IMAGE_NAME}:${params.VERSION}"

                    currentBuild.description = "DEPLOY_SUCCESS_${params.VERSION}"
                }
            }
        }

        stage('Execute Rollback Flow') {
            when { expression { params.DEPLOYMENT_ACTION == 'ROLLBACK' } }
            steps {
                script {
                    currentBuild.description = 'ROLLBACK_IN_PROGRESS'
                    echo "Reverting ${env.CONTAINER_NAME} from ${env.CURRENT_ACTIVE} to ${params.ROLLBACK_VERSION}..."

                    bat "docker stop ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker rm ${env.CONTAINER_NAME} 2>nul || exit 0"
                    bat "docker run -d --name ${env.CONTAINER_NAME} -p ${env.APP_PORT}:8080 ${IMAGE_NAME}:${params.ROLLBACK_VERSION}"

                    currentBuild.description = "ROLLBACK_SUCCESS_${params.ROLLBACK_VERSION}"
                }
            }
        }
    }

    post {
        always {
            script {
                def finalState = currentBuild.description ?: currentBuild.currentResult
                echo """
=======================================================
📋 PIPELINE EXECUTION SUMMARY
=======================================================
ENVIRONMENT:      ${params.ENVIRONMENT}
ACTION TAKEN:     ${params.DEPLOYMENT_ACTION}
PREVIOUS VERSION: ${env.CURRENT_ACTIVE}
TARGET VERSION:   ${env.TARGET_VERSION}
FINAL STATE:      ${finalState}
=======================================================
"""
            }
        }
    }
}