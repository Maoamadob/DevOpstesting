---
name: secret-scan-diff
description: Escanea git diff por secretos antes de commit (AKIA, passwords, tokens, .env, keys). Gate de seguridad pre-commit.
---

# secret-scan-diff

Skill para detectar secretos, credenciales y datos sensibles en `git diff` antes de hacer commit. Actúa como gate de seguridad.

Se activa cuando el usuario dice: "escanea el diff por secretos", "busca secretos", "chequea secretos", o `/secret-scan-diff`.

## Patrones de detección

Buscar en `git diff` (staged + unstaged):

| Patrón | Ejemplos | Severidad |
|--------|----------|-----------|
| **AWS Access Keys** | `AKIA[0-9A-Z]{16}` | 🔴 CRÍTICA |
| **Passwords/Secrets** | `password\s*[=:]\s*['\"].*['\"]` | 🔴 CRÍTICA |
| **Private Keys** | `-----BEGIN (RSA\|DSA\|EC) PRIVATE KEY-----` | 🔴 CRÍTICA |
| **.env files** | `\.env` (archivos completos) | 🔴 CRÍTICA |
| **Tokens** | `token\s*[=:]\s*['\"]` | 🟠 ALTA |
| **DB Credentials** | `(user\|pass)\s*[=:]\s*['\"]` | 🟠 ALTA |
| **API Keys** | `api[_-]?key\s*[=:]\s*['\"]` | 🟠 ALTA |
| **OAuth Tokens** | `Bearer\s+[A-Za-z0-9\-._~+/]+=*` | 🟠 ALTA |

## Proceso

1. **Verificar estado**: `git diff --cached` (staged) + `git diff` (unstaged)
2. **Escanear patrones**: aplicar regex para cada patrón
3. **Reportar hallazgos**:
   - Si hay secretos → 🚫 **BLOQUEADO**: listar archivos + líneas + tipo de secreto
   - Si está limpio → ✅ **SEGURO**: "No se detectaron secretos"
4. **No hacer commit**: detener si hay hallazgos; esperar a que el usuario corrija

## Salida esperada

**Caso: Secreto detectado**
```
🚫 SECRETOS DETECTADOS — Commit bloqueado

Archivo: app/api/.env (línea 3)
  Patrón: PASSWORD DETECTED
  Contenido: password="super_secret_123"

Archivo: terraform/terraform.tfvars (línea 2)
  Patrón: AWS ACCESS KEY
  Contenido: AKIAIOSFODNN7EXAMPLE

✋ Acciones:
  1. git checkout app/api/.env terraform/terraform.tfvars
  2. Agregá .env a .gitignore
  3. Usa secretos en GitHub Actions/env vars
  4. Vuelve a escanear: /secret-scan-diff
```

**Caso: Limpio**
```
✅ SEGURO — No se detectaron secretos en git diff

Staging: X archivos, Y líneas analizadas
Working tree: A archivos, B líneas analizadas

Procede con commit.
```

## Integración con commit-std

El flujo recomendado es:
1. Editar código
2. `git add archivos`
3. `/secret-scan-diff` ← **primero**
4. `/commit-std` ← después (si pasa escaneo)

## Notas

- No almacenar salida de escaneo en logs públicos (contendría líneas con secretos)
- Si el usuario pide bypassear: NO permitir (seguridad no es negociable)
- False positives: strings tipo `password = getenv("DB_PASSWORD")` son OK (no el valor real)
