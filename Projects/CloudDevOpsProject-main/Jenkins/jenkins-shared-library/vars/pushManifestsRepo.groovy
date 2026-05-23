def call(String repo, String credentialsId, String file) {
    dir('manifests-repo') {
        withCredentials([usernamePassword(credentialsId: credentialsId, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
            sh """
                git config user.name "Jenkins CI"
                git config user.email "jenkins@example.com"
                git add ${file}
                git commit -m "Update image to ${env.FULL_IMAGE}" || echo "No changes to commit"
                git push https://${GIT_USER}:${GIT_TOKEN}@${repo}
            """
        }
    }
}
