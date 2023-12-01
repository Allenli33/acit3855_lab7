// Define a function that encapsulates your pipeline logic
def call() {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage('Python Lint') {
                steps {
                    script {
                        def files = findFiles(glob: '*/app.py')
                        for (file in files) {
                            sh "echo ${file.path}"
                            sh "pylint --fail-under=5.0 --disable=E0401 ${file.path}"
                        }
                    }
                }
            }
            // Uncomment and modify the following stages according to your requirements
            /*
            stage('Security') {
                steps {
                    // Security steps go here
                }
            }
            stage('Package') {
                steps {
                    // Package steps go here
                }
            }
            stage('Deploy') {
                when {
                    expression { params.DEPLOY }
                }
                steps {
                    // Deploy steps go here
                }
            }
            */
        }
    }
}
