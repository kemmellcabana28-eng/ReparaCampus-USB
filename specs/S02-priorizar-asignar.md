# SPEC S02 · Priorizar y asignar

**Versión / autor / revisor / fecha:** v1.0 / [COMPLETAR autor] / [COMPLETAR revisor] / [COMPLETAR fecha]

**Requisito asociado:** RF02

**Historia.** Como coordinador, quiero que cada incidencia tenga una prioridad calculada y poder asignarla a un técnico activo, para que se atienda según su urgencia.

**Alcance y exclusiones.** Cálculo de prioridad y asignación. Excluye reasignación y restricción por especialidad.

**Entradas.** Código de la incidencia e identificador del técnico.

**Precondiciones y permisos.** Rol COORDINADOR; incidencia REGISTRADA; técnico existente, con rol TECNICO y activo.

**Reglas y proceso.** Prioridad calculada en el servidor: con riesgo, CRITICA; sin riesgo e impacto ALTO, ALTA; sin riesgo e impacto BAJO, NORMAL. Asignar: validar rol → estado REGISTRADA → técnico activo → en una transacción pasar a ASIGNADA, guardar la asignación y el evento ASIGNACION.

**Salidas y cambios persistidos.** Estado ASIGNADA, técnico asignado, fila en asignaciones y evento.

**Errores y efectos que deben evitarse.** No se reasigna una incidencia ya ASIGNADA. Los rechazos no cambian estado ni historial. La prioridad nunca viene del cliente.

**Criterios de aceptación**

- **AC-S02-01:** Dado un coordinador y una incidencia REGISTRADA, cuando la asigna a un técnico activo, entonces pasa a ASIGNADA con ese técnico y se registra el evento.
- **AC-S02-02:** Dado un solicitante o un técnico, cuando intenta asignar, entonces recibe 403 y no hay cambios.
- **AC-S02-03:** Dado una incidencia ya ASIGNADA, cuando el coordinador intenta asignarla de nuevo, entonces se rechaza y se conserva el técnico original.
- **AC-S02-04:** Dado un técnico inexistente, inactivo o que no tiene rol TECNICO, cuando se intenta asignar, entonces se rechaza sin cambios.
- **AC-S02-05:** Dado riesgo=true, o riesgo=false con impacto ALTO, o riesgo=false con impacto BAJO, cuando se registra, entonces la prioridad es CRITICA, ALTA o NORMAL respectivamente.
- **AC-S02-06:** Dado un formulario con un campo «prioridad» manipulado, cuando se registra, entonces el servidor lo ignora y calcula la prioridad.
- **AC-S02-07:** Dado una incidencia que no está REGISTRADA, cuando se intenta asignar, entonces se rechaza.

**Diseño y tareas vinculadas.** Función calcular_prioridad(); servicio asignar(); T-S02-1 prioridad (AC-05/06), T-S02-2 asignación (AC-01/03/04/07), T-S02-3 permisos (AC-02), T-S02-4 pruebas.

**Pruebas y resultados esperados.** tests/test_s02_priorizar_asignar.py (t09–t15). Los esperados se escriben a mano, sin usar la función de producción.

**Decisión de revisión / versión aprobada:** [COMPLETAR: aprobada / ajustar, revisor, fecha]
