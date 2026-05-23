output "jenkins_master_public_ip" {
  value = aws_instance.jenkins_master.public_ip
}

output "jenkins_worker_public_ip" {
  value = aws_instance.jenkins_worker.public_ip
}

output "jenkins_master_id" {
  value = aws_instance.jenkins_master.id
}

output "jenkins_worker_id" {
  value = aws_instance.jenkins_worker.id
}

