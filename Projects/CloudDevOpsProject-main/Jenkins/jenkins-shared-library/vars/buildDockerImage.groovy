def call(String image) {
    dir("Docker/App") {
        sh "docker build -t ${image} ."
    }
}
