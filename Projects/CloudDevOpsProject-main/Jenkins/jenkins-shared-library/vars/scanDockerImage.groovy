def call(String image, String tag) {
    def reportName = "trivy-${tag}.json"
    sh "trivy image -f json -o ${reportName} ${image}"
    archiveArtifacts artifacts: reportName, fingerprint: true
}
