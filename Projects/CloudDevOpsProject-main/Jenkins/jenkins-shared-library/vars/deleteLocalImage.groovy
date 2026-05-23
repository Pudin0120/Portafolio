def call(String image) {
    sh "docker rmi ${image} || true"
}
