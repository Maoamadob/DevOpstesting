---
description: Sincroniza README/docs con comandos reales y CLAUDE.md. Usar con /docs-sync, "valida documentación", "chequea README", "sincroniza docu", "¿el README está al día?".
---

# docs-sync

Skill para detectar desincronizaciones del README.md respecto a CLAUDE.md y al repo.

Se activa cuando el usuario dice: "valida documentación", "chequea README", "chequea documentación", "sincroniza docu", "¿el README está al día?" o `/docs-sync`.

Si el working directory es el monorepo padre, leer `DevOpstesting/README.md` y `DevOpstesting/CLAUDE.md`.

## Señales de detección

Comparar `README.md` (+ `docs/` si aplica) contra `CLAUDE.md` y el diff actual
(`git diff` staged + unstaged). Si el diff no toca docs pero el usuario pide sync,
leer también los archivos actuales (no solo el diff).

| Señal | Ejemplo en este repo | Severidad |
|-------|----------------------|-----------|
| **Comando en README ausente en CLAUDE.md** | README dice `terraform plan` siempre; CLAUDE.md dice no plan con state vacío | ALTA |
| **Comando en CLAUDE.md no documentado en README** | CLAUDE.md lista `terraform validate`; README no lo menciona | MEDIA |
| **Comando que falla o no existe** | Script/ruta documentada que no está en el repo | ALTA |
| **Diff toca código/infra sin tocar docs** | Cambios en `terraform/` o `k8s/` y README sin actualizar cuando el flujo cambió | MEDIA |
| **Políticas contradictorias** | README invita a apply; CLAUDE.md prohíbe apply sin confirmación | ALTA |
| **Posible secreto en docs** | Credencial en README → reportar y sugerir `/secret-scan-diff` | CRÍTICA |

## Proceso

1. **Verificar estado**: `git status` + `git diff --cached` (staged) + `git diff` (unstaged)
2. **Leer fuentes de verdad**:
   - `CLAUDE.md` (comandos y workflow reales)
   - `README.md` (+ `docs/` si el diff o el pedido lo implican)
3. **Escanear señales de desync** (no regex de secretos):
   - Comandos en README vs comandos en `CLAUDE.md`
   - Comandos documentados que no existen en el repo
   - Diff que cambia flujo (`terraform/`, `k8s/`, `app/`, CI) sin actualizar docs
   - Políticas contradictorias (ej. README sugiere `apply`; `CLAUDE.md` lo restringe)
   - Posible secreto en docs → marcar crítico y sugerir `/secret-scan-diff`
4. **Reportar hallazgos**:
   - Si hay desync → 🚫 **DESACTUALIZADO**: listar `doc dice` / `realidad dice` / archivo
   - Si está alineado → ✅ **AL DÍA**: "README y CLAUDE.md concuerdan con el diff/repo"
5. **Proponer fix**: diff mínimo de documentación (no aplicar todavía)
6. **Esperar confirmación** antes de editar README/docs
7. **No hacer commit ni push**; si hubo cambios de docs, sugerir `/secret-scan-diff` → `/commit-std`

## Salida esperada

**Caso: Documentación desactualizada**
```
🚫 DESACTUALIZADO — Docs fuera de sync

Hallazgo 1: Doc dice: README.md → "correr siempre terraform plan" Realidad: CLAUDE.md → no correr plan si el state tiene 0 resources Archivo a actualizar: README.md

Hallazgo 2: Doc dice: (no documentado) Realidad: CLAUDE.md → terraform validate antes de terminar cambios .tf Archivo a actualizar: README.md

✋ Acciones propuestas:

Revisar el diff mínimo de documentación propuesto abajo
Confirmar si debo aplicar los cambios en README.md / docs/
Tras aplicar: /secret-scan-diff
Luego: /commit-std
```


**Caso: Documentación al día**
```
✅ AL DÍA — README y CLAUDE.md concuerdan con el diff/repo

Comparado:

CLAUDE.md (comandos/workflow)
README.md (+ docs/ si aplica)
git diff staged + unstaged
No se requieren cambios de documentación. Puedes continuar con /secret-scan-diff → /commit-std si vas a commitear.
```


## Integración con otras skills

El flujo recomendado es:
1. Editar código / infra / docs
2. `/docs-sync` ← alinear README con CLAUDE.md y el diff
3. `/secret-scan-diff` ← gate de secretos
4. `/commit-std` ← commit con mensaje estándar

## Notas

- No inventar comandos: solo documentar lo que exista en CLAUDE.md o en el repo
- Si el diff no toca docs pero el usuario pide sync, leer archivos actuales (no solo el diff)
- Proponer el fix primero; editar solo tras confirmación explícita
- No hacer commit ni push desde esta skill
- Si aparece un posible secreto en README/docs, reportarlo como CRÍTICO y sugerir `/secret-scan-diff` (no bypassear)
- Mantener cambios de docs mínimos y revisables (evitar reescribir el README completo sin necesidad)
