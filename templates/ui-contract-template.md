# UI Contract: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

Este contrato es la **única fuente de identidad de la UI** (Principio VI de la constitución): nombres de elementos, etiquetas accesibles, roles, mensajes y estados. El diseño y el código se alinean a este contrato; nunca al revés. El tester aislado deriva sus selectores exclusivamente de la tabla de identificadores canónicos y de las etiquetas aquí definidas.

<!--
  Este archivo lo genera el comando /speckit.plan (Fase 1) para toda feature con UI,
  siguiendo esta plantilla híbrida. Reglas para el agente:
  - Si ya existe un diseño (p. ej. Penpot vía su MCP de plugin), importa los nombres de
    capa y reconcilíalos en la tabla ANTES de congelar el contrato: el contrato canoniza,
    el diseño adopta. Renombra las capas divergentes al nombre canónico.
  - Exporta la referencia visual congelada a specs/[###-feature]/design/ (una imagen por
    pantalla). Ese snapshot es la única referencia visual para el Build.
  - Elimina estos comentarios y reemplaza todo placeholder antes de entregar.
-->

## 1. Identificadores canónicos

Una fila por elemento interactivo o hito de accesibilidad. Nadie fuera de este contrato inventa identificadores: ni el diseño, ni el tester, ni el Build.

| Ruta/Pantalla | Elemento | Nombre (`name`/`id`) | Etiqueta accesible | Rol ARIA | `data-testid` | Capa en el diseño |
| --- | --- | --- | --- | --- | --- | --- |
| `/[ruta]` | [campo de entrada] | `[nombre-canonico]` | [etiqueta visible exacta] | textbox | — | `[nombre-de-capa]` |
| `/[ruta]` | [botón] | `[nombre-canonico]` | [texto exacto del botón] | button | — | `[nombre-de-capa]` |
| `/[ruta]` | [encabezado] | `[nombre-canonico]` | [título exacto] | heading | — | `[nombre-de-capa]` |

Reglas de la tabla:

- Nombres únicos por pantalla y sin colisiones entre rutas.
- La etiqueta accesible es el texto visible exacto; el tester selecciona por rol + etiqueta.
- `data-testid` es opcional y solo se declara cuando rol + etiqueta no bastan para identificar de forma única.
- El nombre de capa del diseño debe coincidir con el nombre canónico; si difiere, se renombra la capa o se canoniza aquí antes de congelar el contrato.
- Un cambio de identificador se hace primero en esta tabla; diseño y código se actualizan después.

## 2. Rutas y pantallas

| Ruta | Propósito | Hito (`h1`) |
| --- | --- | --- |
| `/[ruta]` | [propósito de la pantalla] | [título del `h1`] |

## 3. Flujo de pasos

[Orden de pantallas, foco al cambiar de paso y reglas del stepper si aplica.]

## 4. Contratos por pantalla

### [N]. `/[ruta]` — [título]

**Elementos**

- [Elemento con etiqueta, ayuda, atributos (`inputmode`, `autocomplete`, `maxlength`) y nombre canónico tomado de la tabla. No se repiten los textos exactos que ya están en la tabla.]

**Estados**

- [Inicial / enviando / error / éxito, con reglas `aria-*` y de foco.]

**Validación**

- [Reglas de formato, habilitación y bloqueo semántico.]

**Reglas**

- [Reglas de negocio y privacidad que la pantalla exige.]

<!-- Repite esta subsección por pantalla. -->

## 5. Mensajes del canal

[Mensajes de aviso, `aria-live`, contadores y textos de espera.]

## 6. Contrato de mensajes de error

[Causa + acción correctiva por mensaje; vocabulario prohibido.]

## 7. Accesibilidad (WCAG 2.1 AA)

[Roles, foco, anuncios, reflow a 320 px, `lang`, contraste; solo los hitos verificables por la suite a11y.]

## 8. Responsivo y visual

[Breakpoints, tokens del sistema de diseño y reglas de modo oscuro.]

## 9. Modo aceptación

[Controles de simulación que la suite necesita y cómo se activan sin tocar código de producción. Omitir si no aplica.]
