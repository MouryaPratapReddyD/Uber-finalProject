# CSYE7220 DevOps Uber application
### Mourya Pratap Reddy Dasarapalli
---



# About Application
* Uber bus application to allow users to Sign Up, Sign In, Book a trip, and View booking history
* Token based authentication for user Sign in and Sign up
* React and NginX server for frontend
* Flask and Gunicorn server for backend
* Users and Bookings information stored in MongoDb Atlas service
* IaC - Terraform to provision EKS cluster
* CI - AWS Codebuild
* CD - K8S yaml files

---

## To run the app on localhost
* Change fetch() to http://localhost* statements in /fe/Pages/*
1. cd be
2. python uber.py
-
1. cd fe
2. npm install
3. npm start

---

## To run on AWS
* Change fetch() to relevant statements in /fe/Pages/*
1. Go to AWS ECR and create two repos:
    * uberfe
    * uberbe
2. Go to AWS Codebuild and create the build project
    * Connect my github repo to this build project
    * Enable webhooks for automatic project build
3. In root directory of my github repo, build and push docker images to ECR
    * RUN - docker build -f be/Dockerfile -t 123456789012.dkr.ecr.us-east-2.amazonaws.com/uberbe:dev ./be
    * RUN - docker build -f fe/Dockerfile -t 123456789012.dkr.ecr.us-east-2.amazonaws.com/uberfe:dev ./be
    * Authenticate the Docker CLI to use the ECR registry:
        *  aws ecr get-login-password --region us-east-2 | docker login
--username AWS password-stdin 123456789012.dkr.ecr.us-east-2.amazonaws.com
    * RUN - docker push 123456789012.dkr.ecr.us-east-2.amazonaws.com/uberbe:dev
    * RUN - docker push 123456789012.dkr.ecr.us-east-2.amazonaws.com/uberfe:dev
4. Now go to EKS_terraform directory to provision EKS cluster:
    * RUN terraform init, plan and apply
    * Then follow the cheatsheet in this directory
5. Now go to CD_k8s directory:
    * RUN - 
        * kubectl apply -f uberbe-deployment.yaml
        * kubectl apply -f uberfe-deployment.yaml
        * kubectl apply -f service-uberbe.yaml
        * kubectl apply -f service-uberfe.yaml
        * kubectl get nodes
        * kubectl apply -f service-ubere-scale.yaml
        * kubectl get nodes
        * kubectl get deployments
        * kubectl get svc
    * Copy the uberfe service external ip and paste it on your browser and run

---

Things to remember:
* choco install -y aws-iam-authenticator

