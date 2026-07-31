---
name: tf-validate
description: Validate Terraform changes safely in this repo (providers, versions, resources) — runs terraform init/validate, checks for compatible plan output, and never applies (no apply, no destroy). Use when the user asks things like "valida terraform", "revisa providers", "¿el validate pasa?", "corre validate", "sin apply", "check terraform", "does it plan/validate cleanly", or otherwise wants to validate/verify Terraform code, provider versions, or an infra plan without touching real infrastructure.
---

# tf-validate

Skill para validar cambios de Terraform en este repo de forma segura, sin tocar infraestructura real.

## 1. Identificar en qué copia se está trabajando

Este repo tiene (o puede tener) dos copias de `terraform/`:

- **Copia git** (`DevOpstesting/terraform/` o la que esté bajo control de versiones): es la fuente de verdad para editar y commitear `.tf`. Normalmente NO tiene `.terraform/`, `.terraform.lock.hcl`, `terraform.tfvars` ni `*.tfstate*` (están en `.gitignore`).
- **Copia de trabajo** (por ejemplo `../terraform/` fuera del repo git, o la misma carpeta si ahí se corrió `terraform init`): tiene `.terraform/`, `.terraform.lock.hcl`, `terraform.tfvars` y `terraform.tfstate`. Aquí es donde se debe ejecutar `init`/`validate`/`plan`, porque es la única con provider descargado, variables reales y estado.

Antes de correr cualquier comando de Terraform, confirma con `ls -la` cuál carpeta tiene `.terraform/` y `terraform.tfstate`, y trabaja ahí. Si los `.tf` están duplicados entre ambas copias, cualquier edición debe reflejarse en ambas para que no queden desincronizadas.

## 2. Editar `.tf` solo si el usuario pidió un cambio

- Si el usuario solo pide **validar** (o "revisa que compile", "corre validate", etc.), no edites ningún archivo `.tf`. Limítate a leer, correr comandos de solo lectura y reportar.
- Si el usuario pidió explícitamente un cambio (ej. fijar versión de provider, ajustar un argumento porque la documentación oficial de esa versión lo exige), edita solo lo mínimo necesario y solo en archivos `.tf` (incluye `providers.tf`/`versions.tf` si existen). No inventes resources, módulos ni bloques que no estén en la documentación oficial del provider/módulo.

## 3. Correr `terraform init` y `terraform validate`

En la copia de trabajo:

```bash
terraform init            # sin -upgrade salvo que sea necesario para resolver el pin
terraform validate
```

Usa `-upgrade` únicamente si `init` falla porque el lock actual no satisface un constraint nuevo (por ejemplo, tras cambiar `required_providers`). Si tienes que usarlo, dilo explícitamente y muestra qué cambió en `.terraform.lock.hcl`.

## 4. NO correr `terraform apply`

Nunca ejecutes `terraform apply` (ni `-auto-approve`, ni destroy) como parte de esta skill. Esta skill es solo de validación/diagnóstico.

## 5. `terraform plan`: revisar el state antes de correrlo

Antes de correr `terraform plan`, revisa cuántos recursos
```bash
terraform state list
# o, si necesitas inspeccionar el archivo directamente sin exponer valores sensibles:
python3 -c "import json; d=json.load(open('terraform.tfstate')); print(len(d.get('resources', [])))"
```

- Si el state tiene **0 resources** (infra ya destruida, como indica `CLAUDE.md` de este proyecto tras pruebas manuales), **no corras `terraform plan`** sin avisar antes: el plan mostraría la creación completa del stack (VPC, EKS, RDS, ALB, CloudTrail, etc.) contra la cuenta AWS real, algo que probablemente no tiene relación con lo que el usuario pidió validar. En su lugar, explica este diagnóstico y pregunta si de todas formas quiere ver ese plan completo.
- Si el state ya tiene recursos, `terraform plan` es de solo lectura (no modifica nada) y sí se puede correr para confirmar el impacto del cambio. Clasifica cualquier cambio detectado como `none` / `safe update` / `risky replace-destroy`, y si aparece un `destroy` o `replace` no trivial, PARA y explica el riesgo antes de seguir.

## 6. Mostrar salidas y archivos tocados

Al terminar, muestra:
- La salida relevante de `init`/`validate` (y de `plan` si se corrió).
- La lista de archivos `.tf` modificados (diff pequeño, solo lo necesario).
- Si se tocó más de una copia del repo, deja explícito que se sincronizaron ambas.

## 7. Preguntar antes de commit

Nunca hagas `git add`/`git commit` como parte de esta skill sin preguntar primero. Al final, pregunta explícitamente al usuario si quiere que se haga commit de los cambios (y aclara que el commit solo aplica a la copia que es un repo git).
