output "vpc_id" {
  value = module.network.vpc_id
}

output "eks_cluster_name" {
  value = module.eks.eks_cluster_name
}

output "node_group_name" {
  value = module.eks.node_group_name
}

output "jenkins_master_ip" {
  value = module.server.jenkins_master_public_ip
}

output "jenkins_worker_ips" {
  value = module.server.jenkins_worker_public_ip
}

output "cloudwatch_dashboard_url" {
  value = module.monitoring.cloudwatch_dashboard_url
}
