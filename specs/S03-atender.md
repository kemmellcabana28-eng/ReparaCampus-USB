# SPEC S03 · Atender

**Versión / autor / revisor / fecha: v1.0 / jaider lozano/ Kemmell cabana/ 8-10-2026

**Requisito asociado:** RF03

**Historia.** Como técnico, quiero iniciar la atención de mis incidencias y registrar la solución, para que el solicitante pueda validarla.

**Alcance y exclusiones.** Iniciar atención y registrar solución. Excluye reasignar o editar soluciones.

**Entradas.** Código y texto de la solución (20 a 800 caracteres tras el trim).

**Precondiciones y permisos.** Rol TECNICO y ser el técnico asignado a esa incidencia.

**Reglas y proceso.** Iniciar: ASIGNADA → EN_ATENCION con evento INICIO_ATENCION. Registrar solución: solo desde EN_ATENCION → PENDIENTE_VALIDACION; se guarda una solución nueva sin sobrescribir las anteriores, y el evento SOLUCION.

**Salidas y cambios persistidos.** Nuevo estado, fila en soluciones y evento, todo en una transacción.

**Errores y efectos que deben evitarse.** Un técnico no asignado, otro rol o un estado incorrecto se rechazan sin cambios. No se admite solución antes de iniciar.

**Criterios de aceptación**

- **AC-S03-01:** Dado el técnico asignado y una incidencia ASIGNADA, cuando inicia la atención, entonces pasa a EN_ATENCION y se registra el evento.
- **AC-S03-02:** Dado un técnico que no es el asignado, cuando intenta iniciar o registrar una solución, entonces recibe 403 y no hay cambios.
- **AC-S03-03:** Dado una incidencia ASIGNADA que no se ha iniciado, cuando el técnico registra una solución, entonces se rechaza.
- **AC-S03-04:** Dado una incidencia EN_ATENCION, cuando la solución tiene 19 caracteres se rechaza; con 20 u 800 se acepta; con 801 se rechaza.
- **AC-S03-05:** Dado una incidencia EN_ATENCION y una solución válida, cuando el técnico la registra, entonces pasa a PENDIENTE_VALIDACION, la solución queda guardada y existe el evento SOLUCION.
- **AC-S03-06:** Dado un coordinador o un solicitante, cuando intenta iniciar o registrar una solución, entonces recibe 403 y no hay cambios.
- **AC-S03-07:** Dado una incidencia que no está ASIGNADA, cuando se intenta iniciar la atención, entonces se rechaza.

**Diseño y tareas vinculadas.** Tabla soluciones; servicios iniciar_atencion() y registrar_solucion(); T-S03-1 iniciar (AC-01/02/06/07), T-S03-2 solución (AC-03/04/05), T-S03-3 formularios, T-S03-4 pruebas.

**Pruebas y resultados esperados.** tests/test_s03_atender.py (t16–t22).

**Decisión de revisión / versión aprobada:** aprobada / Sebastian murcia/ 8-10-2026
