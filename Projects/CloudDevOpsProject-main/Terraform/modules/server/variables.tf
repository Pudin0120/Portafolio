variable "project_name" {}
variable "vpc_id" {}
variable "public_subnet_ids" {
  type = list(string)
}
variable "key_name" {}
variable "ami_id" {default     = "ami-08a6efd148b1f7504"}
