def call(String image) {
    withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
        sh """
            echo "${PASS}" | docker login -u "${USER}" --password-stdin
            docker push ${image}
        """
    }
}
