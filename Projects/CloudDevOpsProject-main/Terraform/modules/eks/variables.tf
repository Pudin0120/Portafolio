variable "cluster_name" {}
variable "cluster_version" {
  default = "1.29"
}
variable "cluster_role_arn" {}
variable "node_role_arn" {}
variable "subnet_ids" {
  type = list(string)
}
variable "instance_types" {
  type = list(string)
  default = ["t3.medium"]
}
variable "desired_size" {
  default = 2
}
variable "min_size" {
  default = 1
}
variable "max_size" {
  default = 2
}