variable "region" {
  type = string
  default = "us-east-1"
}

variable "sns_email" {
  description = "Email to receive CloudWatch alerts"
  type        = string
}

variable "jenkins_master_id" {
  type = string
}

variable "jenkins_worker_id" {
  type = string
}

variable "cluster_name" {}
variable "node_group_name" {}


