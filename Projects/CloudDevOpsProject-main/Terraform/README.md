# Jenkins & EKS Infrastructure Deployment on AWS using Terraform

##  Overview
This repository contains the complete Terraform-based deployment of a Jenkins & EKS infrastructure on AWS. It provisions networking, EC2 instances for Jenkins master/worker, an EKS cluster, CloudWatch monitoring, and SNS notifications-all modularized for scalability and clarity.

---

##  What's Included

###  S3 Backend Configuration
- Stores Terraform state remotely in an S3 bucket for state locking and versioning.

###  Networking Module
- Provisions a VPC with a specified CIDR block.
- Creates public subnets across multiple Availability Zones.
- Configures Internet Gateway and route tables for public internet access.

###  Server Module
- Provisions two EC2 instances (Jenkins Master & Worker) in separate AZs.
- Associates security groups allowing SSH (22), HTTP (80), HTTPS (443), Jenkins (8080), and custom ports (5000).
- Utilizes Amazon Linux 2 with EBS root volumes.

###  EKS Module
- Provisions an EKS cluster using Terraform.
- Creates a managed node group.
- Configurable instance types and autoscaling settings.

###  Monitoring Module
- Sets up CloudWatch dashboards for Jenkins and EKS nodes.
- Creates CloudWatch alarms for high CPU utilization.
- Sends alert notifications via Amazon SNS.

---

##  Project Structure

```
jenkins-infrastructure/
 main.tf
 backend.tf
 variables.tf
 terraform.tfvars
 outputs.tf
 modules/
     network/
        main.tf
        variables.tf
        outputs.tf
     server/
        main.tf
        variables.tf
        outputs.tf
     eks/
        main.tf
        variables.tf
        outputs.tf
     monitoring/
         main.tf
         variables.tf
         outputs.tf
```

---

##  Deployment Steps

### 1. Configure Remote Backend
Create and configure an S3 bucket for Terraform state:

```bash
aws s3api create-bucket --bucket terraform-lock-ivolve --region us-east-1
aws s3api put-bucket-versioning --bucket terraform-lock-ivolve --versioning-configuration Status=Enabled
```

### 2. Create EC2 Key Pair
Generate key to access EC2 instances:

```bash
aws ec2 create-key-pair --key-name jenkins-key --query 'KeyMaterial' --output text > jenkins-key.pem
chmod 400 jenkins-key.pem
```

### 3. Initialize and Deploy Terraform Modules

```bash
terraform init
terraform plan
terraform apply -auto-approve
```

---

## OK Post-Deployment Verification

### Terraform Outputs

```bash
terraform output
```
![Output](https://github.com/user-attachments/assets/cf6b23de-cb7f-4cff-a504-4c767ce302f1)

---

### EKS Verification

```bash
aws eks list-clusters
aws eks update-kubeconfig --region us-east-1 --name eks-cluster
kubectl get nodes
```

![EKS Clusters](https://github.com/user-attachments/assets/03ac05a2-5502-48f0-8716-41db052f3bf9)
![Nodes](https://github.com/user-attachments/assets/031d1ecc-1588-49bf-b0a3-ca36cab328ec)
---

### AWS Console Checks

- OK VPC and Subnets  
  ![VPC](https://github.com/user-attachments/assets/8d64028e-02d7-4a8e-9ef9-eca570ec05b0)

- OK EC2 Instances Running  
  ![EC2](https://github.com/user-attachments/assets/2449e809-f6d4-45a3-af5b-9a14aa5a8308)

- OK Security Groups Applied  
  ![Security Groups](https://github.com/user-attachments/assets/2693b7e3-a569-4d54-a00b-46cf90169534)

- OK EKS Cluster and Node Group  
  ![EKS Cluster](https://github.com/user-attachments/assets/7f4c5a4f-ddf5-446a-a2c6-ebaa10118c46)  
  ![Node Group](https://github.com/user-attachments/assets/0f71d18b-099d-4af9-8eff-4588257e574a)
  ![node capacity](https://github.com/user-attachments/assets/44a11c61-3827-4582-ac40-4144120325d5)
- OK CloudWatch Monitoring  
  ![Alarms](https://github.com/user-attachments/assets/d279fcd8-471f-4de4-8177-6c5189f05fd3)  
  ![Dashboard](https://github.com/user-attachments/assets/d70c4c30-93cc-49c9-a5ea-d97c5bcf61ac)

- OK SNS Email Notifications  
  ![Email](https://github.com/user-attachments/assets/c831e5dc-4dbc-4aee-a4c1-44c6d1279b07)  
  ![SNS Topic](https://github.com/user-attachments/assets/d765b674-8b3c-420e-8510-d9b2acc500af)

---

##  SSH Access to Instances

Retrieve public IPs:

```bash
terraform output
```

SSH into Jenkins master:
```bash
ssh -i jenkins-key.pem ec2-user@<jenkins_master_public_ip>
```
![Master SSH](https://github.com/user-attachments/assets/b417d912-8d7b-4e83-bfe5-9db4a8294655)

SSH into Jenkins worker:
```bash
ssh -i jenkins-key.pem ec2-user@<jenkins_slave_public_ip>
```
![Worker SSH](https://github.com/user-attachments/assets/0fbe868a-0b5b-4ec1-a7f9-3135450aadde)

---

##  Modules & Inputs Used

Each Terraform module is decoupled and reusable.

### Input Variables Example

```hcl
project_name           = "ivolve"
vpc_cidr               = "10.0.0.0/16"
public_subnet_cidrs    = ["10.0.1.0/24", "10.0.2.0/24"]
azs                    = ["us-east-1a", "us-east-1b"]
cluster_name           = "eks-cluster"
key_name               = "jenkins-key"
cluster_role_arn       = "arn:aws:iam::<ACCOUNT_ID>:role/ClusterRole"
node_role_arn          = "arn:aws:iam::<ACCOUNT_ID>:role/NodeRole"
sns_email              = "your-email@example.com"
region                 = "us-east-1"
```

---

##  Notes
- All Terraform code uses latest AWS provider best practices.
- CloudWatch integrates both EC2 and EKS monitoring.
- Jenkins instances and EKS worker nodes are monitored separately.
- Alarms are triggered based on CPU thresholds and notify via email.

---

##  Cleanup
To destroy all infrastructure:

```bash
terraform destroy -auto-approve
```

---