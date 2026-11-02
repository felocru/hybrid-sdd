# CU Piloto — Checklist

Este documento define el caso de uso real que se usará para validar la Fase 0. No es un ejemplo ficticio: debe ser una HU/CU del proyecto.

## Datos del CU

- **Nombre del CU:** CU-01 — Agendar cita médica.
- **Actor(es):** Recepcionista (principal); Especialista (consulta su agenda).
- **Objetivo del negocio:** Reservar un horario para un paciente con un especialista, dejando la cita confirmada o pendiente de documentación según corresponda.
- **Flujo principal:** La recepcionista captura paciente, especialista, fecha, hora, duración y motivo; el sistema valida datos, traslape y aviso de privacidad; guarda la cita y registra auditoría.
- **Flujos alternos / excepciones:** Datos inválidos, fecha pasada, paciente o especialista inexistente, traslape de horario, paciente de primera vez sin aviso de privacidad.
- **Entidades con estados:** Cita (CONFIRMADA, PENDIENTE_DOCUMENTACION, ATENDIDA, CANCELADA).
- **Criterios de aceptación (CA):** CA-1 cita confirmada y auditada; CA-2 cita pendiente de documentación con alerta; CA-3 traslape rechazado sin registrar la cita.
- **NFR del CU:** p95 menor a 300 ms para agendar; 20 recepcionistas concurrentes sin duplicar citas.
- **Contratos/interfaces:** Contrato de UI de la vista `/citas`.
- **UI afectada (si aplica):** `CitasView` en Vaadin Flow.

## Checklist de la especificación

- [ ] `spec.md` conserva la estructura oficial de Spec Kit.
- [ ] Tiene un diagrama de casos de uso (`usecase-beta`).
- [ ] Cada historia tiene un diagrama de actividad/flujo.
- [ ] Las entidades con ciclo de vida tienen diagrama de estados.
- [ ] Los CA están en Given/When/Then y son verificables.
- [ ] Los CA tienen ids `CA-n` estables y globales.
- [ ] El texto no repite los pasos de los diagramas.
- [ ] Las reglas que no caben en diagramas están en Requirements/Edge Cases.
- [ ] Los NFR del CU están en `spec.md`; los globales en `constitution.md`.

## Checklist del plan

- [ ] `plan.md` tiene C4 L3 (`C4Component`).
- [ ] `plan.md` tiene diagrama de secuencia.
- [ ] `plan.md` tiene class diagram de dominio.
- [ ] `data-model.md` tiene ER (`erDiagram`) y constraints.
- [ ] Class diagram y ER coexisten y no se contradicen.
- [ ] Los contratos están en `contracts/` y enlazados desde el plan.
- [ ] El `Summary` no repite el C4.

## Checklist de tareas y aceptación

- [ ] `tasks.md` no contiene tareas de aceptación.
- [ ] Build tiene tareas de unitarias, integración, ArchUnit y contrato.
- [ ] La suite de aceptación existe en `tests/acceptance/`.
- [ ] La suite está congelada en un commit dedicado.
- [ ] Cada CA tiene al menos un test de aceptación.
- [ ] `/speckit.implement` no ejecuta ni modifica la aceptación.
- [ ] No se fuerza test-first para las pruebas de caja blanca.

## Checklist de Mermaid

- [ ] `mmdc` local está instalado (12+).
- [ ] `python3 scripts/validate_mermaid.py specs/ --mmdc mmdc` pasa.
- [ ] `usecase-beta` renderiza.
- [ ] C4 renderiza.
- [ ] `flowchart`, `stateDiagram-v2`, `sequenceDiagram`, `classDiagram` y `erDiagram` renderizan.

## Checklist de validación del preset

- [ ] El flujo se ejecutó en un proyecto limpio con el preset, no sobre artefactos manuales.
- [ ] `python3 spec-kit-hybrid/scripts/validate_overrides.py --project . --stage all --mmdc mmdc` pasa sin FAIL.
- [ ] Los WARN se revisaron y se justificaron.
- [ ] Los artefactos generados no se editaron a mano después de la generación.
- [ ] El flujo se repitió desde un proyecto limpio tras cualquier corrección.

## Observaciones del piloto

- ¿La IA duplicó texto y diagrama?
- ¿Qué sección fue la más difícil de mantener sin duplicar?
- ¿El diagrama de casos de uso aportó claridad?
- ¿El C4 L3 fue útil o redundante?
- ¿El class diagram y el ER se solaparon?
- ¿La aceptación antes de implementar funcionó?
- ¿Build intentó tocar la aceptación?
- ¿Qué ajuste hay que hacer en plantillas/comandos?
