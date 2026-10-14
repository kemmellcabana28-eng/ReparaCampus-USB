# SPEC S04 · Validar

**Versión / autor / revisor / fecha:** v1.0 / Kemmell Cabana / Jaider Lozano / 8/10/2026

**Requisito asociado:** RF04

**Historia.** Como solicitante, quiero confirmar, rechazar o reabrir la solución de mi incidencia, para asegurar que el problema quedó resuelto.

**Alcance y exclusiones.** Confirmar, rechazar y reabrir. Excluye cierre automático y acciones del coordinador en nombre del solicitante.

**Entradas.** Código; motivo de 10 a 300 caracteres tras el trim, para rechazar o reabrir.

**Precondiciones y permisos.** Solo el solicitante dueño. El coordinador no confirma ni reabre en su nombre.

**Reglas y proceso.** Confirmar: PENDIENTE_VALIDACION → CERRADA, con un cierre registrado. Rechazar: PENDIENTE_VALIDACION → EN_ATENCION con el mismo técnico, conservando la solución anterior. Reabrir: CERRADA → EN_ATENCION con el mismo técnico, solo si el tiempo desde el último cierre es menor o igual a 48 horas (UTC, calculado por el servidor). Se conservan todos los cierres y soluciones anteriores. El navegador no elige la hora; en pruebas el reloj es inyectable.

**Salidas y cambios persistidos.** Nuevo estado, cierre (si aplica) y evento CIERRE, RECHAZO o REAPERTURA con el motivo.

**Errores y efectos que deben evitarse.** Un usuario que no es el dueño, un estado incorrecto, un motivo inválido o una reapertura fuera de plazo se rechazan sin cambios.

**Criterios de aceptación**

- **AC-S04-01:** Dado el dueño y una incidencia PENDIENTE_VALIDACION, cuando confirma, entonces queda CERRADA con un cierre registrado y su evento.
- **AC-S04-02:** Dado otro solicitante, un coordinador o un técnico, cuando intenta confirmar, rechazar o reabrir, entonces recibe 403 y no hay cambios.
- **AC-S04-03:** Dado el dueño y un reporte PENDIENTE_VALIDACION con técnico T01 y solución registrada, cuando lo rechaza con «El daño sigue presente», entonces queda EN_ATENCION, conserva T01 y la solución anterior, y registra quién rechazó, cuándo y por qué.
- **AC-S04-04:** Dado un motivo de 9 caracteres, cuando rechaza o reabre, entonces se rechaza sin cambios; con 10 o 300 se acepta; con 301 se rechaza.
- **AC-S04-05:** Dado una incidencia CERRADA hace exactamente 48 horas, cuando el dueño la reabre, entonces vuelve a EN_ATENCION con el mismo técnico.
- **AC-S04-06:** Dado una incidencia CERRADA hace 48 horas y 1 segundo, cuando el dueño intenta reabrirla, entonces se rechaza sin cambios.
- **AC-S04-07:** Dado una incidencia reabierta, resuelta y cerrada de nuevo, cuando se reabre otra vez, entonces el plazo se mide desde el último cierre y los cierres y soluciones anteriores siguen en el historial.
- **AC-S04-08:** Dado una incidencia fuera del estado requerido, cuando se intenta confirmar, rechazar o reabrir, entonces se rechaza sin cambios.

**Diseño y tareas vinculadas.** Tabla cierres; reloj inyectable (CLOCK); servicios confirmar(), rechazar() y reabrir(); T-S04-1 confirmar, T-S04-2 rechazar, T-S04-3 reapertura y reloj, T-S04-4 permisos, T-S04-5 pruebas.

**Pruebas y resultados esperados.** tests/test_s04_validar.py (t23–t32), con fechas ficticias fijas y avance controlado del reloj.

**Decisión de revisión / versión aprobada:** aprobada / Jaider Lozano / 8/10/2026
