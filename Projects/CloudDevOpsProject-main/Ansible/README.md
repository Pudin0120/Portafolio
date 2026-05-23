# Jenkins CI/CD Infrastructure on AWS using Ansible

This repository provides an Ansible-based solution for automated provisioning, configuration, and management of a Jenkins CI/CD environment on AWS EC2 instances.

The infrastructure is fully automated and dynamically scalable using EC2 instance tags for host targeting, modular Ansible roles for clean separation of concerns, and Groovy scripts for Jenkins customization.

---

## Key Features

- Dynamic EC2 Inventory using AWS EC2 tags  
- Role-Based Configuration for Git, Java, Docker, Jenkins Master, Worker, and Trivy  
- Automated Jenkins Setup with plugin installation, user creation, and BlueOcean UI  
- Docker installed and configured across all nodes  
- SSH key integration for secure Jenkins master-agent communication  
- Tested with `ansible-inventory` and test playbooks

---

## Directory Structure

```
Ansible/
 ansible.cfg             # Ansible configuration
 aws_ec2.yaml            # AWS EC2 dynamic inventory
 jenkins-key.pem         # EC2 key pair (private key)
 jenkins-key.pub         # EC2 key pair (public key)
 playbook.yaml           # Main playbook
 roles/
     docker/             # Docker installation and setup
     git/                # Git installation
     java/               # OpenJDK 17 installation
     jenkins_master/     # Jenkins Master provisioning
     jenkins_slave/      # Jenkins Worker setup
     trivy/              # Trivy installation
```

---

## Prerequisites

- AWS CLI configured and authenticated  
- Python 3.x  
- Ansible 2.9+  
- Python packages `boto3` and `botocore`

Install dependencies:

```bash
pip install boto3 botocore
chmod 400 jenkins-key.pem
```

---

## Inventory Validation

Check the dynamic inventory:

```bash
ansible-inventory -i aws_ec2.yaml --graph
```

![Inventory Graph Screenshot](https://github.com/user-attachments/assets/c3b3179a-2659-45e6-96ab-25950eac7c2e)

Ping test:

```bash
ansible all -m ping -i aws_ec2.yaml
```

![Ping Output Screenshot](https://github.com/user-attachments/assets/ef218bf9-a380-4116-a5f1-4f3e08566f79)

---

## Running the Playbook

```bash
ansible-playbook -i aws_ec2.yaml playbook.yaml
```

---

## Access Jenkins

Once deployed, access Jenkins at:

```
http://<JENKINS_MASTER_PUBLIC_IP>:8080
```

**Credentials:**

- Username: `sherif`  
- Password: `123456`

![Jenkins UI Screenshot](https://github.com/user-attachments/assets/80115c1c-0688-4016-899f-80cfcbf96e85)

---

## Role Descriptions

| Role           | Description                                                    |
|----------------|----------------------------------------------------------------|
| git            | Installs Git on all nodes                                      |
| docker         | Installs Docker and adds users to the Docker group             |
| java           | Installs OpenJDK 17                                            |
| jenkins_master | Installs Jenkins, sets up admin user, installs plugins         |
| jenkins_slave  | Configures SSH, sets up slave agent, Docker access             |
| trivy          | Installs Trivy image scanner                                   |

![Roles Overview Screenshot 1](https://github.com/user-attachments/assets/5352d66c-16b6-412e-a85c-66e1ea8decb3)  
![Roles Overview Screenshot 2](https://github.com/user-attachments/assets/fff274fe-18c3-4b45-ba64-242f06dae6e4)  
![Roles Overview Screenshot 3](https://github.com/user-attachments/assets/7365fb0d-faba-4418-a224-37f949fc2dd8)  
![Roles Overview Screenshot 4](https://github.com/user-attachments/assets/811c9292-ce01-49c3-85a4-bc8423b64549)  
![Roles Overview Screenshot 5](https://github.com/user-attachments/assets/a84b2dbb-4eab-4058-9b46-01a242cfb9cc)  
![Roles Overview Screenshot 6](https://github.com/user-attachments/assets/a35d8561-ee7c-4105-8d79-2d02b258f2e2)  
![Roles Overview Screenshot 7](https://github.com/user-attachments/assets/b9fa84e2-f051-4b24-a178-085eb92cdb6d)
![All changes](https://github.com/user-attachments/assets/b0a87bdf-8e71-4fe8-8a47-654e090ea2c5)
---

## Jenkins Automation Highlights

- Admin user creation via Groovy  
- Plugin installation (BlueOcean, Git, Docker, etc.)  
- Disables setup wizard for faster deployment  
- Installs `jenkins-cli.jar` for CLI automation  
- SSH-based agent connection with master  
- Idempotent Ansible role design

---

## EC2 Tagging Convention

Ensure instances are tagged properly for Ansible inventory to detect them:

| Tag Key | Example Value    |
|---------|------------------|
| Name    | jenkins-master   |
| Name    | jenkins-worker   |

---

## Installed Software Summary

**Jenkins Master:**

- Java 17 (Amazon Corretto)  
- Docker, Git  
- Jenkins with pre-installed plugins and configuration  
- SSH setup for connecting agents  

**Jenkins Worker:**

- Java 17, Git, Docker, Trivy  
- Configured Jenkins agent  
- Public key-based SSH from master

---
