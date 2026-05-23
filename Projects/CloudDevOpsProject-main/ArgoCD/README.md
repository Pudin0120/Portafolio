
# Argo CD Setup on Amazon EKS

This guide walks you through deploying **Argo CD** on an **Amazon EKS cluster**, including service exposure for web UI access.

---

## Prerequisites

- An existing EKS cluster
- `kubectl` configured to access your EKS cluster
- `awscli` authenticated with permissions to access your EKS environment

---

## 1 Create Namespace for Argo CD

```bash
kubectl create namespace argocd
```

---

## 2 Install Argo CD

Apply the official Argo CD installation manifest:

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

<img width="1134" height="629" alt="Image" src="https://github.com/user-attachments/assets/4edfe16a-67fb-4fbc-baac-5c39f4ff9695" />

Check that all Argo CD pods are running:

```bash
kubectl get pods -n argocd
```

---

## 3 Expose Argo CD UI Using a LoadBalancer

Patch the Argo CD server service:

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Wait for a few minutes, then retrieve the external IP:

```bash
kubectl get svc argocd-server -n argocd
```

Look for the `EXTERNAL-IP` field of the `argocd-server` service.

<img width="1196" height="276" alt="Image" src="https://github.com/user-attachments/assets/e7baf526-0d5b-451d-bf32-57f312302823" />

You can also see this on the EKS console:

<img width="1034" height="678" alt="Image" src="https://github.com/user-attachments/assets/50b37487-660e-46d4-9ed4-9922588d4ffa" />

---

## 4 Access the Argo CD UI

Once the LoadBalancer is available, access Argo CD from your browser using:

```
http://<EXTERNAL-IP>
```

Replace `<EXTERNAL-IP>` with the actual public endpoint retrieved above.

<img width="1920" height="1026" alt="Image" src="https://github.com/user-attachments/assets/c6e80825-785a-4aa7-b2f1-f88992d747f9" />

---

## Step 2: Access ArgoCD Web UI

1. Open a web browser and navigate to the ArgoCD URL.
2. Log in using credentials (username/password).
   - To get the password:
     ```bash
     kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
     ```
3. Verify you see the default ArgoCD dashboard.

<img width="1916" height="1025" alt="Image" src="https://github.com/user-attachments/assets/03f29f3e-8c07-4e3b-9dc4-59b7c7c33fb6" />

## Step 3: Configure Repository in ArgoCD

1. From settings, add a new repository:
   - Click **+ Connect Repo** button.
   - Choose your connection method: **VIA HTTPS**.
   - Fill in the connection details:
     - **Repository URL**: `https://github.com/Sherif127/kubernetes-manifests.git`
   - Click **Connect**.

2. Verify the connection:
   - Status should show "Successful".
   - Test the connection by clicking the **Refresh** button.

<img width="1631" height="298" alt="Image" src="https://github.com/user-attachments/assets/77969fc2-45ec-4cf3-83bc-d0f71961154c" />

## Step 4: Create New Application

1. Click the "+ New App" button in the top navigation.
2. Configure application settings:

**General Section:**
- Application Name: `ivolve-app`
- Project: `default`
- Sync Policy:
  - Automatic sync
  - Self-Heal

<img width="1868" height="889" alt="Image" src="https://github.com/user-attachments/assets/7b3a1109-734b-4df0-be80-fa07e8266087" />

**Source Section:**
- Repository URL: `https://github.com/Sherif127/kubernetes-manifests.git`
- Revision: `main`
- Path: `.` (root directory of the repo)

**Destination Section:**
- Cluster: `https://kubernetes.default.svc`
- Namespace: `ivolve`

3. Click the "Create" button.

<img width="1878" height="899" alt="Image" src="https://github.com/user-attachments/assets/54f430c0-6025-4695-8ddc-cb97772c32ee" />

## Step 4: Verify Initial Deployment

1. In the Applications list:
   - Locate `ivolve-app`
   - Verify status changes from "OutOfSync" to "Synced"
   - Health status should show "Healthy"

<img width="537" height="415" alt="Image" src="https://github.com/user-attachments/assets/55cf9d54-e7c2-4af1-adf3-0005fb46768a" />

2. Verify resources:
   - Click the application name.
   - Check the "Resources" tab for:
     - Deployment (1/1 available)
     - Service (LoadBalancer created)
     - Pods (Running status)

<img width="1639" height="873" alt="Image" src="https://github.com/user-attachments/assets/552632f1-8d7a-4fe9-9897-b09634ed80ea" />

## Step 6: Test Pipeline-Driven Deployment Flow

### 1. Manually Trigger Pipeline

1. In Jenkins UI:
   - Navigate to your `ivolve-app` job.
   - Click **Build Now**.

### 2. Verify Automated Manifest Update

1. Check Git commit (within 1 minute of pipeline completion):

<img width="1039" height="349" alt="Image" src="https://github.com/user-attachments/assets/a439ec9f-be54-4f3a-8a29-c0d7f1a6b1f2" />

### 3. Observe ArgoCD Response (Within 3 Minutes)

1. In ArgoCD UI:
   - Application status will transition:
     ```
     Synced  OutOfSync  Syncing  Synced
     ```
   - Health status may briefly show **Progressing** during rollout

<img width="1637" height="864" alt="Image" src="https://github.com/user-attachments/assets/884fc641-c447-46d6-bfba-dc6b81031899" />

2. Verify deployment update:

```bash
kubectl describe deployment ivolve-app -n ivolve | grep Image
```

Output should match the new BUILD_NUMBER from Jenkins.

<img width="891" height="41" alt="Image" src="https://github.com/user-attachments/assets/6b9adb41-4343-4bef-b84b-8f9dd88369c7" />
<img width="381" height="74" alt="Image" src="https://github.com/user-attachments/assets/b2e37f88-5e54-483b-9542-2546232529ee" />

### 4. Validate Pod Rotation

1. Check pod versions:
   - Old pods will be terminating (if using rolling updates).
   - New pods will show the updated image tag.

<img width="670" height="80" alt="Image" src="https://github.com/user-attachments/assets/84e53d71-fa7f-42b9-9a5b-9f8573f4d39d" />

Access the application:

<img width="1920" height="1029" alt="Image" src="https://github.com/user-attachments/assets/f6610888-ba98-432b-a640-60841f995080" />
