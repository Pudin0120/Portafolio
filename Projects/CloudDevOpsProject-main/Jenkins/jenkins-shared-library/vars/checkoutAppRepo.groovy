def call(String repo, String branch = 'main', String credentialsId) {
    git branch: branch, credentialsId: credentialsId, url: repo
}
