---
name: commit-std
description: Crea commits con mensaje estándar Conventional Commits. Usar cuando el usuario pida commit, /commit-std, o "commitea con el estándar".
---

# commit-std

Skill para crear commits a solicitud de usuario el mismo se activara cada que se solicite crear commit por parte del usario o "commitear con standard"

## Convención de mensaje
Usar Conventional Commits:
```text
<tipo>(<scope opcional>): <descripción corta en imperativo, inglés>

```

## Pasos
git status + git diff
No stagear secretos, .env, *.tfstate, credenciales
Proponer el mensaje completo
Esperar confirmación explícita
git add (archivos acordados) + git commit
Mostrar git status
No hacer push salvo que lo pidan