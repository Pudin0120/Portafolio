# Deploying a Flask Application on Kubernetes

This guide walks you through the process of deploying a Flask web application on a Kubernetes cluster. The deployment is organized into three main steps: namespace creation, application deployment, and service exposure using a LoadBalancer.

---

## Step 1: Create a Namespace

We start by creating a dedicated **namespace** to logically isolate application resources.

### YAML File: `namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ivolve
```

### Apply the Namespace

```bash
kubectl apply -f namespace.yaml
```

> OK This helps in managing, monitoring, and deleting all related resources easily.

<img width="516" height="140" alt="Image" src="https://github.com/user-attachments/assets/a2c518d4-ded7-4f7f-9baf-accdcf7b767c" />

---

## Step 2: Deploy the Flask Application

We create a **Deployment** that describes how the Flask container should run within the cluster.

### YAML File: `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ivolve-app
  namespace: ivolve
  labels:
    app: ivolve-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ivolve-app
  template:
    metadata:
      labels:
        app: ivolve-app
    spec:
      containers:
        - name: flask-container
          image: leoughhh/ivolve-app:latest
          ports:
            - containerPort: 5000
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
```

### Apply the Deployment

```bash
kubectl apply -f deployment.yaml
```

<img width="631" height="63" alt="Image" src="https://github.com/user-attachments/assets/91af9b6d-836d-4aa2-b003-c2c6c39af015" />


---

## Step 3: Expose the Application via a Service

Create a **Service** of type `LoadBalancer` to expose your Flask app externally.

### YAML File: `service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ivolve-service
  namespace: ivolve
spec:
  type: LoadBalancer
  selector:
    app: ivolve-app
  ports:
    - port: 80
      targetPort: 5000
```

### Apply the Service

```bash
kubectl apply -f service.yaml
```

---

##  Accessing the Flask App

Once the LoadBalancer is provisioned, you can access the Flask app using:

```
http://<EXTERNAL-IP>
```

<img width="1920" height="1029" alt="Image" src="https://github.com/user-attachments/assets/dcafbe7f-39ed-4178-bed4-23ac53aca85c" />

---

## Summary

| Resource   | File Name       | Status          |
|------------|------------------|------------------|
| Namespace  | `namespace.yaml` | OK Created        |
| Deployment | `deployment.yaml`| OK Flask running  |
| Service    | `service.yaml`   | OK External access|

---
