# DevOps Technical Test — Platform & DevOps Engineer

Prueba técnica de arquitectura cloud en AWS con microservicios contenedorizados, orquestados en EKS, desplegados mediante Terraform (IaC) y CI/CD con GitHub Actions.

> **Nota:** La infraestructura AWS fue destruida con `terraform destroy` al finalizar la entrega para evitar costos. El código, manifiestos e instrucciones de despliegue permanecen en este repositorio.

## URLs y entregables

| Recurso | Referencia |
|---------|------------|
| **Aplicación (ALB)** | `http://devops-test-alb-1769044833.us-east-1.elb.amazonaws.com/` ∏ |
| **Repositorio** | https://github.com/Maoamadob/DevOpstesting |
| **Docker Hub — API** | https://hub.docker.com/r/maoamadob/devops-api |
| **Docker Hub — Frontend** | https://hub.docker.com/r/maoamadob/devops-frontend |
| **Presentación** | PowerPoint con respuestas teóricas, capturas y diagramas |

---

## Arquitectura

![Diagrama de arquitectura AWS — CI/CD, EKS, ALB, RDS y monitoreo](docs/architecture.png)

La solución despliega microservicios contenedorizados en **Amazon EKS** dentro de una **VPC** segmentada, expuestos mediante **ALB**, con base de datos **RDS PostgreSQL** en subnet privada, aprovisionamiento **Terraform**, pipeline **GitHub Actions** y capa de **monitoreo Prometheus/Grafana**.

### Flujo de tráfico

```
Internet Users → ALB :80 → EKS NodePort 30080 → frontend (nginx) → api (Flask) :5000 → RDS :5432
```

### Componentes AWS

| Componente | Detalle |
|------------|---------|
| **VPC** | `10.0.0.0/16` — 2 subnets públicas + 2 privadas (us-east-1a/b) |
| **NAT Gateway** | 1 NAT (decisión costo/Free Tier; en prod: 1 por AZ) |
| **ALB** | HTTP:80 → Target Group puerto 30080 |
| **EKS** | `devops-test-eks` — Kubernetes 1.31 |
| **Node Group** | `t3.small` — EC2 gestionado por EKS (equivalente funcional a servidores EC2) |
| **RDS** | PostgreSQL 15 — `db.t3.micro`, subnet privada |
| **IAM** | Usuario `terraform-admin` + roles EKS automáticos |
| **CloudTrail** | Auditoría de API calls → bucket S3 |

### Flujo CI/CD

```
Developer → Git Push → GitHub Actions
    → Tests (pytest)
    → Build & Push (Docker linux/amd64 → Docker Hub)
    → Deploy to EKS (kubectl apply + rollout restart)
    → Notify on Failure
```

### Capa de monitoreo (Prometheus + Grafana)

| Componente | Función |
|------------|---------|
| **Prometheus** | Recolección y almacenamiento de métricas |
| **Grafana** | Dashboards y visualización |
| **kube-state-metrics** | Métricas del estado de objetos Kubernetes |
| **node-exporter** | Métricas de CPU, memoria y disco del nodo EC2 |
| **ServiceMonitor** | Scraping de `/metrics` en la API Flask |
| **Metrics Server** | Métricas de recursos para HPA |
| **HPA** | Autoescalado horizontal de pods por CPU |

**Métricas expuestas por la API (Flask + prometheus-client):**

- `http_requests_total` — volumen de requests por endpoint y status (2xx, 4xx)
- `http_request_duration_seconds` — latencia por ruta
- `api_errors_total` — conteo de errores internos del servidor (5xx) con ID de rastreo

**Métricas clave monitoreadas:**

- Disponibilidad: uptime, error rate, health checks ALB/pods
- Rendimiento: latencia, throughput (`rate(http_requests_total[1m])`)
- Infraestructura: CPU/memoria nodos y pods, restarts

```
App /metrics → Prometheus → Grafana dashboards
Kubernetes metrics → Prometheus → Alertas (prod)
HPA ← Metrics Server ← CPU pods
```

---

## Estructura del repositorio

```
.
├── .github/workflows/ci-cd.yml   # Pipeline CI/CD (punto 11)
├── app/
│   ├── api/                      # Microservicio API Flask + /metrics (puntos 7, 10)
│   │   ├── app.py
│   │   ├── test_app.py           # Tests automatizados (punto 11)
│   │   └── Dockerfile
│   └── frontend/                 # Microservicio frontend nginx (punto 7)
│       ├── nginx.conf
│       └── Dockerfile
├── docs/
│   └── architecture.png          # Diagrama IaaS (punto 7)
├── k8s/                          # Manifiestos Kubernetes + HPA (puntos 1, 7, 10)
├── monitoring/
│   ├── prometheus-values.yaml    # Helm values Prometheus/Grafana (punto 10)
│   └── servicemonitor-api.yaml   # Scraping métricas API (punto 10)
├── terraform/                    # Infrastructure as Code (puntos 2, 4, 5, 9)
│   ├── vpc.tf
│   ├── eks.tf
│   ├── alb.tf
│   ├── rds.tf
│   ├── security_groups.tf
│   ├── iam.tf
│   ├── variables.tf
│   └── output.tf
└── README.md
```

---

## Mapa de la prueba técnica (PDF — 13 puntos)

Leyenda: **✅ Implementado en repo** · **📊 Documentado en PowerPoint** · **⚠️ Parcial / mejora propuesta**

---

### 1. Administración de Infraestructura

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Configurar y gestionar un servidor en AWS utilizando EC2 | ✅ | Nodos EC2 del EKS Managed Node Group (`terraform/eks.tf`) — instancias `t3.small` en subnets privadas |
| Asegurar alta disponibilidad y escalabilidad del servidor | ⚠️ | HPA en `k8s/hpa-api.yaml`, `k8s/hpa-frontend.yaml`; 1 nodo en prueba. HA multi-AZ documentada en PPT |
| Explicar alta disponibilidad en servidores críticos | 📊 | PowerPoint: ALB, multi-AZ, ASG, health checks, RDS Multi-AZ |
| Actualizar SO en múltiples servidores sin afectar servicio | 📊 | PowerPoint: rolling updates K8s, `maxSurge: 0` en Deployments, drain/cordon |
| Gestionar entorno mixto Linux/Windows (AD, GPO, PowerShell) | 📊 | PowerPoint: respuesta teórica de integración híbrida |

---

### 2. Servicios de Red

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Configurar DNS, DHCP, FTP en Linux | 📊 | PowerPoint: respuesta teórica (entorno lab/on-premise) |
| Diagnosticar latencia de red multi-región | 📊 | PowerPoint: Route 53 latency-based, CloudWatch, traceroute |
| Diseñar red AWS: VPC, subnets, SG, NACLs, ALB | ✅ / 📊 | **Implementado:** `terraform/vpc.tf`, `terraform/security_groups.tf`, `terraform/alb.tf`. **NACLs custom:** 📊 documentadas en PPT (VPC module usa NACLs por defecto) |
| Segmentación de red y decisiones tomadas | ✅ / 📊 | Subnets públicas (ALB) / privadas (EKS, RDS); SG restrictivos; NAT para salida. Detalle en sección *Decisiones de arquitectura* |

---

### 3. Contenedores y Virtualización

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Entorno virtualizado VMware o Hyper-V | 📊 | PowerPoint: VirtualBox en Mac ARM con 2 VMs Ubuntu (equivalente funcional) |
| Crear y gestionar al menos dos máquinas virtuales | 📊 | PowerPoint: 2 VMs con red Host-only, IPs estáticas, conectividad verificada |
| Almacenamiento persistente en contenedores | 📊 | PowerPoint: demo `docker volume` + persistencia de datos entre reinicios |

---

### 4. Ciberseguridad Integrada

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Prácticas de ciberseguridad en servidores y VMs | ✅ / 📊 | Security Groups, RDS no público, subnets privadas, secrets en GitHub Actions |
| Configurar firewall y políticas de seguridad | ✅ | `terraform/security_groups.tf` — SG ALB (80/443), EKS nodes (solo desde ALB), RDS (solo desde EKS) |
| WAF, OWASP, rate limiting | 📊 | PowerPoint: AWS WAF asociado a ALB, managed rules, logs (no desplegado en prueba) |

---

### 5. Gestión de Nube

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Servicios AWS incluyendo RDS | ✅ | `terraform/rds.tf` — PostgreSQL 15 en subnet privada |
| Acceso y seguridad en arquitectura multinube | 📊 | PowerPoint: IAM Identity Center, roles cross-account, cifrado, VPN/Direct Connect |
| IAM: roles, mínimo privilegio, MFA, auditoría CloudTrail | ✅ / 📊 | **CloudTrail:** `terraform/iam.tf`. **Roles EKS:** automáticos en `terraform/eks.tf`. **MFA:** 📊 documentado en PPT como práctica recomendada |

---

### 6. Soporte 24/7

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Manejar incidencia crítica fuera de horario | 📊 | PowerPoint: ejemplo de caída de pods, escalamiento, runbooks |
| Responder a incidente de alta prioridad con comunicación | 📊 | PowerPoint: flujo de escalamiento, war room, status page |
| Postmortem: causa raíz, timeline, SLA, acciones ITIL | 📊 | PowerPoint: postmortem de incidente simulado (gestión de incidentes/problemas/cambios) |

---

### 7. Diseño de Infraestructura

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Arquitectura web con microservicios Docker + Kubernetes | ✅ | `app/api/`, `app/frontend/`, `k8s/`, imágenes en Docker Hub |
| Diagrama Cloud PaaS | 📊 | PowerPoint: diagrama PaaS (EKS, RDS managed, ALB) |
| Diagrama On-premise | 📊 | PowerPoint: diagrama infraestructura local |
| Diagrama Cloud IaaS | ✅ / 📊 | `docs/architecture.png` + PowerPoint |

---

### 8. Políticas de Respaldo y Recuperación

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Políticas de respaldo y recuperación en la nube | ⚠️ / 📊 | RDS con snapshots automáticos deshabilitados en prueba (`backup_retention_period = 0` en `terraform/rds.tf`). Estrategia DR documentada en PPT |
| Probar respaldos y planes de recuperación | 📊 | PowerPoint: RTO/RPO, restore de snapshot RDS, `terraform apply` para recrear infra |

---

### 9. Diseño de Arquitectura y Automatización

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Automatización para reducir error humano y tiempos de despliegue | ✅ | Terraform + GitHub Actions + manifiestos K8s reproducibles |
| Infrastructure as Code con Terraform/Ansible/Puppet | ✅ | `terraform/` — VPC, EKS, ALB, RDS, SG, CloudTrail |

---

### 10. Monitoreo y Optimización de Rendimiento

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Herramientas de monitoreo (Prometheus, Grafana, etc.) | ✅ | `monitoring/prometheus-values.yaml`, `monitoring/servicemonitor-api.yaml` |
| Ajustar recursos según necesidad | ✅ | HPA (`k8s/hpa-*.yaml`), `resources` en Deployments, Helm values con límites |
| Métricas clave para producción | ✅ / 📊 | `http_requests_total`, latencia, CPU/memoria. Detalle en PPT |
| Automatizar respuesta a picos de carga | ✅ | HPA escala pods por CPU; en prod: Karpenter/Cluster Autoscaler documentado en PPT |

---

### 11. Buenas prácticas de CI/CD

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Pipeline Jenkins / GitLab CI / GitHub Actions | ✅ | `.github/workflows/ci-cd.yml` |
| ArgoCD + GitOps en Kubernetes | ⚠️ / 📊 | Push-based deploy con `kubectl apply`. ArgoCD documentado en PPT como evolución a GitOps |
| Pruebas automatizadas (unitarias, integración) | ✅ | `app/api/test_app.py` — pytest en job `test` del pipeline |
| Notificaciones de fallos en el Pipeline | ✅ | Job `notify-failure` en `.github/workflows/ci-cd.yml` |
| Diferencias entre CI y CD | 📊 | PowerPoint |
| Pipeline seguro multi-entorno (dev/staging/prod) | 📊 | PowerPoint: branches, environments, secrets, approval gates |

---

### 12. Documentación y Mejora Continua

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Documentación actualizada de procesos e infraestructura | ✅ | Este `README.md` + comentarios en Terraform + PowerPoint |
| Importancia de documentar cambios en infraestructura | 📊 | PowerPoint: Git como fuente de verdad, PRs, CHANGELOG |

---

### 13. Entregable

| Sub-requisito (PDF) | Estado | Referencia |
|---------------------|--------|------------|
| Presentación PowerPoint con respuestas y pantallazos | ✅ | Entregable externo al repo |
| Aplicación/scripting (Python, Bash, PowerShell) | ✅ | API Flask (`app/api/`), tests pytest, pipeline Bash/YAML |
| Repositorio Git con README, despliegue y referencias a cada punto | ✅ | Este repositorio |
| Aplicación desplegada en la nube accesible por URL | ✅ | ALB público (capturas en PowerPoint; infra destruida post-entrega) |

---

## Requisitos previos

- [AWS CLI](https://aws.amazon.com/cli/) configurado (`aws configure`)
- [Terraform](https://www.terraform.io/) >= 1.5
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/) >= 3
- [Docker](https://www.docker.com/)
- Cuenta [Docker Hub](https://hub.docker.com/)
- Cuenta AWS con permisos para EC2, EKS, RDS, VPC, IAM

---

## Despliegue de infraestructura (Terraform)

### 1. Configurar variables

Crear `terraform/terraform.tfvars` (no se sube a Git):

```hcl
aws_region            = "us-east-1"
project_name          = "devops-test"
my_ip                 = "TU_IP_PUBLICA/32"
db_password           = "PasswordSeguro123!"
eks_node_instance_types = ["t3.small"]
eks_node_desired_size   = 1
eks_node_min_size       = 1
eks_node_max_size       = 2
```

Obtener tu IP pública:

```bash
curl -4 ifconfig.me
```

### 2. Desplegar

```bash
cd terraform
terraform init
terraform validate
terraform plan
terraform apply
```

El apply tarda ~20–30 minutos (EKS es el componente más lento).

### 3. Conectar kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name devops-test-eks
kubectl get nodes
```

### 4. Actualizar endpoint RDS en el manifest

Tras el apply, copiar el endpoint y actualizar `k8s/api-deployment.yaml` (`DB_HOST`):

```bash
terraform output rds_endpoint
```

---

## Despliegue de la aplicación

### Opción A — Manual

```bash
docker build --platform linux/amd64 -t maoamadob/devops-api:latest app/api
docker build --platform linux/amd64 -t maoamadob/devops-frontend:latest app/frontend
docker push maoamadob/devops-api:latest
docker push maoamadob/devops-frontend:latest

kubectl apply -f k8s/namespace.yaml
sleep 5
kubectl apply -f k8s/
kubectl get pods -n devops-test
```

### Opción B — CI/CD automático

Push a la rama `main` dispara el pipeline en GitHub Actions.

**Secrets requeridos en GitHub** (Settings → Secrets → Actions):

| Secret | Descripción |
|--------|-------------|
| `DOCKER_USERNAME` | Usuario Docker Hub |
| `DOCKER_PASSWORD` | Personal Access Token de Docker Hub |
| `AWS_ACCESS_KEY_ID` | Access Key IAM |
| `AWS_SECRET_ACCESS_KEY` | Secret Key IAM |

---

## Monitoreo (Prometheus + Grafana)

### Instalar monitoreo

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

kubectl scale deployment coredns -n kube-system --replicas=1

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring -f monitoring/prometheus-values.yaml

kubectl apply -f monitoring/servicemonitor-api.yaml
kubectl apply -f k8s/hpa-api.yaml
kubectl apply -f k8s/hpa-frontend.yaml
```

### Acceder a Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

- URL: http://localhost:3000
- Usuario: `admin`
- Contraseña: `devops-test`

**Query de ejemplo:**

```promql
rate(http_requests_total{status=~"4.."}[1m])
```

### Apagar monitoreo

```bash
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```

---

## Verificación

```bash
kubectl get nodes
kubectl get pods -n devops-test
kubectl get pods -n monitoring
kubectl get hpa -n devops-test
kubectl top pods -n devops-test

# URL del ALB (tras terraform apply)
terraform -chdir=terraform output alb_dns_name
```

Respuesta esperada de la API en `/api/info`:

```json
{
  "service": "api",
  "environment": "dev",
  "db_host": "<rds-endpoint>",
  "message": "DevOps Technical Test - Platform Engineer"
}
```

---

## Decisiones de arquitectura

| Decisión | Justificación |
|----------|---------------|
| **EKS en lugar de EC2 standalone** | Cumple puntos 1 y 7: orquestación K8s + nodos EC2 gestionados |
| **1 NAT Gateway** | Reduce costo en entorno de prueba / Free Tier |
| **t3.small en EKS** | Compatible con Free Tier; límite ~11 pods/nodo |
| **NodePort 30080 + ALB** | Integración directa ALB → EKS sin Load Balancer Controller |
| **Docker Hub** | Simplicidad; en prod se usaría Amazon ECR |
| **Push-based deploy (GitHub Actions + kubectl)** | CI/CD funcional; ArgoCD/GitOps documentado en PPT como evolución |
| **backup_retention_period = 0 en RDS** | Entorno temporal de prueba; en prod: retención ≥ 7 días |
| **Prometheus on-demand** | Stack pesado; se instala/desinstala según necesidad de demo |
| **maxSurge: 0 en Deployments** | Rollout en nodo único sin pods Pending extra |
| **Sin Route 53 / WAF en prueba** | DNS del ALB nativo; WAF y dominio propio documentados en PPT |

---

## Destruir la infraestructura

> Ejecutar después de entregar la prueba, para evitar costos.

```bash
cd terraform
terraform destroy
```

Validar que no queden recursos:

```bash
export AWS_REGION=us-east-1
aws eks list-clusters
aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, `devops`)].DBInstanceIdentifier'
aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `devops`)].LoadBalancerName'
```

> Tras `terraform destroy`, comandos `kubectl` y `helm` fallarán — es el comportamiento esperado.

---

## Costos estimados

| Recurso | Costo aproximado |
|---------|------------------|
| EKS control plane | ~$0.10/hora |
| NAT Gateway | ~$0.045/hora + tráfico |
| ALB | ~$0.0225/hora |
| EC2 t3.small (nodo EKS) | Free Tier / ~$0.02/hora |
| RDS db.t3.micro | Free Tier (12 meses) |

**Recomendación:** ejecutar `terraform destroy` al finalizar la prueba.

---

## Autor

**Mauricio Amado** — Platform & DevOps Engineer Technical Test (2026)
