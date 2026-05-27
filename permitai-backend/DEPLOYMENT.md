# PermitAI Production Deployment Guide 🚀

This document outlines the architecture, AWS setup, environment variables, and migration workflows for deploying the PermitAI backend to production for the **Bruhat Bengaluru Mahanagara Palike (BBMP)** permit approval systems.

---

## 1. Production Architecture Overview

The production environment operates on AWS, containerized with Docker, using serverless container orchestration (AWS ECS Fargate):

```mermaid
graph TD
    Client[Citizens & Officers] -->|HTTPS / API| ALB[Application Load Balancer]
    ALB -->|Route /api| ECSWeb[ECS Fargate: FastAPI Web Service]
    ECSWeb -->|Publish Tasks| Redis[ElastiCache Redis: Broker]
    ECSWoker[ECS Fargate: Celery Async Worker] -->|Subscribe| Redis
    ECSWeb -->|Read/Write DB| RDS[RDS PostgreSQL Cluster]
    ECSWoker -->|Read/Write DB| RDS
    ECSWeb -->|Upload Forms| S3[S3 Bucket: Application PDF/Images]
    ECSWoker -->|AI Doc Extraction| Claude[Anthropic Claude API]
```

---

## 2. Infrastructure Setup Instructions

### 2.1 Database Setup (AWS RDS PostgreSQL)
1. Launch an **Amazon RDS PostgreSQL** instance (v15+ recommended) in a private subnet.
2. Select Multi-AZ deployment for high availability.
3. Configure a security group allowing ingress traffic on port `5432` only from the ECS tasks.
4. Record the database endpoint and credentials to form your `DATABASE_URL`.

### 2.2 Cache & Broker Setup (AWS ElastiCache Redis)
1. Launch an **Amazon ElastiCache Redis** cluster.
2. Disable cluster mode unless extreme load is expected.
3. Restrict ingress traffic on port `6379` to ECS task subnets.
4. Record the primary endpoint to form your `REDIS_URL` and `CELERY_BROKER_URL`.

### 2.3 Storage Setup (AWS S3)
1. Create a private **S3 Bucket** (e.g., `bbmp-permitai-applications`).
2. Enable bucket encryption (SSE-S3 or KMS).
3. Disable public read/write access.
4. Attach an IAM role policy to the ECS task execution role granting `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` permissions for the bucket.

### 2.4 Container Deployment (AWS ECS Fargate)
1. Create an **ECS Cluster** within your VPC.
2. Build and push your Docker image to **AWS ECR** (Elastic Container Registry).
3. Register two **ECS Task Definitions** using the same image:
   - **FastAPI Web Service**:
     - Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - CPU: 0.5 vCPU, Memory: 1 GB (minimum)
   - **Celery Async Worker**:
     - Command: `celery -A app.tasks.celery_app.celery_app worker --loglevel=info`
     - CPU: 1 vCPU, Memory: 2 GB (minimum - required for ReportLab and PDF operations)
4. Set up an **Application Load Balancer (ALB)** with target groups pointing to the Web service tasks on port `8000`. Set up HTTPS using an ACM (AWS Certificate Manager) SSL certificate.

---

## 3. Environment Variables Configuration

The following parameters must be configured in your ECS task definitions (or AWS Systems Manager Parameter Store/Secrets Manager):

| Variable Name | Description | Example / Recommended Value |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Deployment environment flag | `production` |
| `DEBUG` | Enable debug logs and Swagger schemas | `False` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@rds-endpoint:5432/dbname` |
| `REDIS_URL` | Redis Cache URL | `redis://elasticache-redis-endpoint:6379/0` |
| `CELERY_BROKER_URL` | Redis Broker URL for Celery | `redis://elasticache-redis-endpoint:6379/1` |
| `SECRET_KEY` | HS256 JWT signature seed | *[Generate secure 32-byte hex string]* |
| `CLAUDE_API_KEY` | Anthropic API access key | `sk-ant-api03-...` |
| `CLAUDE_MODEL` | Claude model name | `claude-3-5-sonnet-20241022` |
| `AWS_REGION` | Target AWS datacenter region | `ap-south-1` (Mumbai) |
| `S3_BUCKET_NAME` | Name of private storage bucket | `bbmp-permitai-applications` |
| `SENDGRID_API_KEY` | Production SendGrid API Key | `SG.xxxxxxxxxxxxxxxxxxxxxx` |
| `FROM_EMAIL` | From header for notification emails | `permits@bbmp.gov.in` |
| `FROM_NAME` | BBMP sender branding name | `BBMP Building Permit Department` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["https://permitai.bbmp.gov.in"]` |

---

## 4. Production Database Migrations

Before launching or updating the ECS services, run the database migrations:

1. Connect to the VPC using a bastion host or run a one-off ECS Fargate task.
2. Execute the Alembic upgrade command:
   ```bash
   alembic upgrade head
   ```
3. Verify that all tables, columns (`permit_number`, `approval_conditions`, `notification_preferences`), and index structures are present in the PostgreSQL database.

---

## 5. Production Readiness & Security Checklist

- [ ] **Enforce SSL/TLS**: Ensure the Load Balancer blocks all HTTP traffic and redirects to HTTPS.
- [ ] **S3 Lifecycle Rules**: Archive application PDFs older than 180 days to S3 Glacier for compliance auditing and cost saving.
- [ ] **Sentry Error Tracking**: Set up Sentry (or CloudWatch Logs Insights) to catch unhandled application errors.
- [ ] **VPC Restrictions**: Keep RDS and ElastiCache strictly in private subnets with security group rules allowing egress *only* to internal resources.
