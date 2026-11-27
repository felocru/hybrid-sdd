---
description: Instala el subagente sdt-tester para los arneses detectados (.opencode/agents y/o .agents/agents).
---

Instala el subagente de aceptación `sdt-tester` en este proyecto ejecutando el script de instalación desde la raíz del repositorio Spec Kit.

## Entrada del usuario

```text
$ARGUMENTS
```

## Instrucciones

1. Ejecuta en la terminal, desde la raíz del proyecto:
   - Si `$ARGUMENTS` indica explícitamente un destino (`opencode`, `agy` o `all`, o `--target ...`), pásalo al script (`bash .specify/extensions/hybrid-sdt/scripts/install-agent.sh --target <destino>`).
   - En cualquier otro caso, ejecuta la autodetección:
     `bash .specify/extensions/hybrid-sdt/scripts/install-agent.sh`
2. Verifica el código de salida del comando y reporta exactamente en qué rutas quedó instalado `sdt-tester` (`.opencode/agents/sdt-tester.md` y/o `.agents/agents/sdt-tester/agent.md`).
3. Si el proyecto usa Antigravity CLI, recuerda al usuario que en `.agents/agents/sdt-tester/agent.md` el subagente queda configurado con `model: inherit` y `commandExecutionPolicy: sandbox` para correr en contexto limpio bajo el modelo ejecutor.
