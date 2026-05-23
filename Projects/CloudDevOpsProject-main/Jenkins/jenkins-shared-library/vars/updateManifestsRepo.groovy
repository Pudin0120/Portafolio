def call(String repo, String credentialsId, String file, String newImage) {
    withCredentials([usernamePassword(credentialsId: credentialsId, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
        sh """
            rm -rf manifests-repo
            git clone https://${GIT_USER}:${GIT_TOKEN}@${repo} manifests-repo
            sed -i 's|image: .*|image: ${newImage}|' manifests-repo/${file}
        """
    }
}
