# Bundle Hybrid SDD

Compone el preset `hybrid-methodology` y la extensión `hybrid-sdt`.

## Composición

- `hybrid-methodology` v0.1.0: plantillas y addendas de especificación, plan y tareas.
- `hybrid-sdt` v0.1.0: comandos de aceptación y setup del subagente.

## Instalación

Con los componentes publicados en catálogos:

```bash
specify bundle install hybrid-sdd
```

Con los componentes ya instalados o accesibles localmente:

```bash
specify bundle install ./bundle.yml
```

Después del bundle, instala el agente una vez:

```text
/speckit.hybrid-sdt.setup
```

El bundle no instala `.opencode/agents/sdt-tester.md`; el comando de setup lo copia desde la extensión.

## Construcción del artefacto

```bash
specify bundle build --path ./bundle --output ./dist
```

El `.zip` resultante contiene el manifiesto del bundle; los componentes se resuelven por catálogo o por instalación previa.
