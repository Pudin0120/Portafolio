# Jenkins CI/CD for iVolve Web Application

This guide documents the Jenkins CI/CD pipeline for the **iVolve Flask application**, integrating Docker, GitHub, Trivy scanning, and Kubernetes deployment via Jenkins Shared Libraries.

---

##  Overview

The Jenkins pipeline automates:

- Cloning the application repository  
- Building and scanning Docker images  
- Pushing the image to Docker Hub  
- Updating Kubernetes manifests with the new image tag  
- Pushing manifests to GitHub  
- Deploying the updated image to Kubernetes  

---

##  1. Jenkins Environment Setup

Ensure the following before running the pipeline:

- Jenkins master and slave nodes are properly provisioned (e.g., via Ansible)  
- Java, Docker, and Git are installed  
- The Jenkins slave has Docker access  

### Jenkins Agent Setup

1. Go to **Manage Jenkins > Nodes > New Node**  
2. Select **Permanent Agent**  
3. Configure:  
   - **Remote root directory**: `/home/jenkins`  
   - **Labels**: `agent-ec2`  
   - **Launch method**: SSH (with private key credentials)  
   - **Host Key Verification Strategy**: Non-verifying  
4. Verify the agent shows as **Online**  

    ![Agent Config](https://github.com/user-attachments/assets/1a480afe-6884-4e45-89b5-9d2833748af5)  
    ![Agent Online](https://github.com/user-attachments/assets/1dfa6e92-9ae8-45a9-b30e-b70c72fb9078)  
    <img width="1855" height="783" alt="Image" src="https://github.com/user-attachments/assets/7ab835d4-ceaa-442d-bb80-3f46a4d84368" />
    <img width="1920" height="568" alt="Image" src="https://github.com/user-attachments/assets/96705cd6-a798-40bd-815f-4ff08d1190e8" />
---

##  2. Jenkins Shared Library Setup

The pipeline uses a shared library to modularize Groovy logic.

### Library Structure

```
jenkins-shared-library/
 vars/
     buildDockerImage.groovy
     checkoutAppRepo.groovy
     deleteLocalImage.groovy
     pushDockerImage.groovy
     scanDockerImage.groovy
     updateManifestsRepo.groovy
     pushManifestsRepo.groovy
```

![Library Files](https://github.com/user-attachments/assets/f46f587d-ea76-413f-a619-902b0f78e4db)


### Register Library in Jenkins

1. Go to **Manage Jenkins > Configure System**  
2. Scroll to **Global Pipeline Libraries**  
3. Add a new library:  
   - **Name**: `jenkins-shared-library`  
   - **SCM**: Git  
   - **URL**: *your GitHub repo*  
   - **Default version**: `main`  
   - Add credentials if needed  

![Library Registration](https://github.com/user-attachments/assets/31592ede-34be-4606-9f95-ba64a2cbfe84)

---

##  3. Credentials Configuration

Add these credentials via **Manage Jenkins > Credentials**:

| ID                | Type                  | Usage                         |
|-------------------|-----------------------|-------------------------------|
| `github`          | Username + Token      | Cloning app/manifests repos   |
| `docker`          | Username + Password   | Docker Hub authentication     |
| `Jenkins-ssh-key` | Username + SSH Key    | Connecting agent via SSH      |

![Credentials](https://github.com/user-attachments/assets/8fe95bdf-70ca-43c5-8065-88283957645d)

---

##  4. Jenkinsfile Pipeline Logic

The `Jenkinsfile` in your app repo controls the pipeline.

### Stages:

- `checkoutAppRepo`: Clone application repository  
- `buildDockerImage`: Build Docker image  
- `scanDockerImage`: Scan using Trivy  
- `pushDockerImage`: Push image to Docker Hub  
- `deleteLocalImage`: Remove image locally  
- `updateManifestsRepo`: Update image tag in `deployment.yaml`  
- `pushManifestsRepo`: Commit updated manifests to GitHub  

![Pipeline Stages](https://github.com/user-attachments/assets/d95cb0b3-f3bc-4d36-96df-3a4c6f7844d5)

---

##  5. Kubernetes Manifests Repo

In a separate GitHub repository, store your K8s manifests:

```
kubernetes-manifests/
 deployment.yaml
 service.yaml
 namespace.yaml
```

>  Make sure `deployment.yaml` uses a placeholder image tag that can be replaced by the Jenkins pipeline.

---

##  6. Run the Pipeline

To trigger the CI/CD process:

1. Go to the Jenkins job and click **Build Now**  
2. Monitor build output  
3. Verify:  
   - Docker Hub has a new tag (e.g., `leoughhh/ivolve-app:v2`)  
   - GitHub manifests repo is updated  
   - Kubernetes is running the updated image  


- Docker Hub with new image tag  
  ![DockerHub](https://github.com/user-attachments/assets/01b1d85a-32c0-41e5-9257-edee14d07e54)  
- GitHub commit with updated manifest  
  ![GitHub Commit](https://github.com/user-attachments/assets/b063325b-1a7a-44b6-89ce-488a3777ea28)  
- Output of `kubectl get pods`  
  ![Pods Updated](https://github.com/user-attachments/assets/dcaf938e-b700-413a-8350-24069e62e988)  
- Build artifacts including `trivy-BUILDNUMBER.jar`  
  ![jarfile](https://github.com/user-attachments/assets/f32051fd-108b-4dcc-8b7f-f3f86f3aae78)

---

## OK 7. Final Verification

-  **Docker Image**: Pushed and tagged in Docker Hub  
-  **Manifests**: Committed with updated tag  
-  **Kubernetes**: Pods restarted with new image  
-  **Application**: Accessible via LoadBalancer/Ingress  

![App Browser](https://github.com/user-attachments/assets/5d499f21-3ec6-4e1c-9202-62b67f931de7)

---
