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
        // stage('Security') {
        //     steps {
        //         // install docker scout
        //         sh 'curl -sSfL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh -s --'
        //         // login to dockerhub
        //         withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) {
        //             sh "docker login -u 'dislocatedleg' -p '$TOKEN' docker.io"
        //         }
        //         // Analyze and fail on critical or high vulnerabilities on the python image
        //         // script {
        //         //     def images = ['audit_log', 'dashboard-ui', 'health', 'processing', 'receiver', 'storage'] as String[]
        //         //     for (image in images) {
        //         //         sh "docker scout cves dislocatedleg/${image}"
        //         //     }
        //         // }
        //         sh "docker scout cves python --exit-code --only-severity critical,high"
        //     }
        // }
        // stage('Package') {
        //     steps {
        //         script {
        //             withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) {
        //                 def images = ['audit_log', 'dashboard-ui', 'health', 'processing', 'receiver', 'storage'] as String[]
        //                 for (image in images) {
        //                     sh "docker build -t dislocatedleg/${image} ${image}/"
        //                     sh "docker push dislocatedleg/${image}"
        //                 }
        //             }
        //         }
        //     }
        // }
        // stage('Deploy') {
        //     when {
        //         expression { params.DEPLOY }
        //     }
        //     steps {
        //         sshagent(['docker-vm']) {
        //             sh "ssh -o StrictHostKeyChecking=no -l azureuser acit3855docker.westus3.cloudapp.azure.com 'git -C acit3855/ pull'"
        //             script {
        //                 def images = ['audit_log', 'dashboard-ui', 'health', 'processing', 'receiver', 'storage'] as String[]
        //                 for (image in images) {
        //                     sh "ssh -o StrictHostKeyChecking=no -l azureuser acit3855docker.westus3.cloudapp.azure.com 'docker pull dislocatedleg/$image'"
        //                 }
        //             }
        //             sh "ssh -o StrictHostKeyChecking=no -l azureuser acit3855docker.westus3.cloudapp.azure.com 'docker compose -f acit3855/deployment/docker-compose.yml up -d'"
        //         }
        //     }
        // }
    }
}
