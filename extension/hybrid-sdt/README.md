# Hybrid SDT

Extensión de Spec Kit para el bucle externo de aceptación.

## Comandos

- `speckit.hybrid-sdt.setup`: copia el subagente `sdt-tester` a `.opencode/agents/`.
- `speckit.hybrid-sdt.sdt-test`: genera la suite de aceptación/E2E/carga en contexto aislado.

## Instalación

```bash
specify extension add hybrid-sdt --dev ./extension/hybrid-sdt
```

Después de instalar, ejecuta una vez:

```text
/speckit.hybrid-sdt.setup
```

El setup es explícito: no hay hook que lo ejecute en cada `/speckit.tasks`.

## Notas

- El subagente es específico de OpenCode; Spec Kit no instala `.opencode/agents` de forma nativa.
- La extensión instala comandos y scripts; el setup copia el agente.
- Las reglas de testing viven en la constitución y `AGENTS.md`; el comando y el agente son agnósticos a la tecnología.
