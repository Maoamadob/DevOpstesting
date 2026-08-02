# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

AWS DevOps technical test: two containerized microservices (Flask API + nginx frontend) deployed on
EKS, provisioned via Terraform, shipped through GitHub Actions CI/CD, observed via Prometheus/Grafana.
AWS infra has been destroyed (`terraform destroy`) — only code/manifests remain. See `README.md` for
the architecture diagram and full deployment walkthrough.

## Stack

- **API**: Python 3.11, Flask, `prometheus-client` (`app/api/`)
- **Frontend**: nginx, static HTML (`app/frontend/`)
- **Infra**: Terraform (`terraform-aws-modules/vpc`, `terraform-aws-modules/eks`) — VPC, EKS 1.31, RDS
  PostgreSQL 15, ALB, CloudTrail
- **Orchestration**: Kubernetes manifests (`k8s/`) — Deployments, Services, HPA
- **CI/CD**: GitHub Actions (`.github/workflows/ci-cd.yml`)
- **Monitoring**: kube-prometheus-stack via Helm (`monitoring/`)

## Key Commands

```bash
# API tests
cd app/api && pytest test_app.py -v
pytest test_app.py -v -k test_health_endpoint   # single test

# Docker (amd64 required — EKS nodes are amd64 even from ARM hosts)
docker build --platform linux/amd64 -t maoamadob/devops-api:latest app/api

# Terraform
cd terraform && terraform init && terraform validate && terraform plan && terraform apply
terraform destroy   # always run after manual testing

# Kubernetes
aws eks update-kubeconfig --region us-east-1 --name devops-test-eks
kubectl apply -f k8s/namespace.yaml
sleep 5
kubectl apply -f k8s/
```

## Conventions

1. **No real DB connection in the API** — `app/api/app.py` reads `DB_HOST` only to display it in
   `/api/info`; there's no psycopg2/SQLAlchemy. Don't assume DB connectivity works.
2. **Security groups form a strict chain**: ALB → EKS nodes → RDS (`terraform/security_groups.tf`).
   Extend this chain for new access paths; don't open a parallel one.
3. **`maxSurge: 0`** in `k8s/*-deployment.yaml` because the test cluster runs a single node — revisit
   only if `eks_node_desired_size` increases.
4. **Metrics stay in sync**: `/metrics` in `app.py` (Counter + Histogram via before/after_request hooks)
   must match what `monitoring/servicemonitor-api.yaml` scrapes.
5. **Cost tradeoffs are intentional**: `single_nat_gateway = true`, `backup_retention_period = 0`,
   `skip_final_snapshot = true` — don't "fix" these without checking README's decisions table.

## Security Rules

- Never commit `terraform/terraform.tfvars` — it holds `db_password` and `my_ip`, gitignored by design.
- `my_ip` feeds an SSH ingress CIDR (`terraform/security_groups.tf`) — never default it to `0.0.0.0/0`.
- RDS must stay `publicly_accessible = false`, reachable only from the EKS node security group on 5432.
- CI/CD secrets (`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
  live only in GitHub Actions secrets — never hardcode credentials in workflows or manifests.
- Destroy AWS infra (`terraform destroy`) after any manual testing session to avoid cost exposure.
