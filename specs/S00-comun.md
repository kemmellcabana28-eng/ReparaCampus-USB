# S00 · Problema, alcance y reglas comunes

**Versión / autor / revisor / fecha: v1.0 / Kemmell cabana /   Arnold cantillo/ 8-10-2026

**Necesidad.** La Universidad Simón Bolívar recibe reportes de daños de infraestructura por canales dispersos y a veces los cierra sin saber si quedaron resueltos. Se requiere un prototipo para registrar, priorizar, asignar, atender y validar incidencias.

**Actores y permisos**

| Actor | Puede |
|:----------|:-----------------------------------------------------------|
| SOLICITANTE | Registrar; consultar solo las propias; confirmar, rechazar o reabrir las propias |
| COORDINADOR | Consultar todas; asignar un técnico a incidencias REGISTRADA; ver el tablero. No confirma ni reabre |
| TECNICO | Consultar sus asignadas; iniciar la atención; registrar la solución |

**Estados y transiciones permitidas (únicas)**

- REGISTRADA → ASIGNADA (coordinador)
- ASIGNADA → EN_ATENCION (técnico asignado)
- EN_ATENCION → PENDIENTE_VALIDACION (técnico asignado, con solución)
- PENDIENTE_VALIDACION → CERRADA (solicitante dueño confirma)
- PENDIENTE_VALIDACION → EN_ATENCION (solicitante dueño rechaza con motivo)
- CERRADA → EN_ATENCION (solicitante dueño reabre, ≤ 48 h desde el último cierre)

**Valores permitidos.** Ubicación: LAB-01, AULA-201, BIB-01. Categoría: ELECTRICIDAD, HIDRAULICA, MOBILIARIO, TIC. Impacto: BAJO, ALTO. Riesgo para personas: booleano. Prioridad: CRITICA, ALTA, NORMAL.

**Reglas transversales**

- Identidad y rol se obtienen de la sesión en el servidor; la pertenencia se comprueba en cada operación.
- Los límites de texto se aplican después de retirar espacios externos.
- Las fechas son UTC y las genera el servidor; el cliente no envía la hora efectiva.
- Una operación rechazada no cambia estado ni historial.
- Estado y evento se guardan en una sola transacción (todo o nada).
- El historial es solo de adición: no se edita ni se borra.
- Los textos de usuario se muestran escapados (no se ejecutan como HTML ni scripts).
- No hay cierre automático, edición de reportes ni reasignación.

**Cuentas ficticias (seed).** solicitante1, solicitante2, coordinador1, tecnico1 y tecnico2, con contraseñas ficticias guardadas con hash.

**Preguntas útiles al cliente**

1. ¿Qué debe ver un solicitante cuando abre una incidencia ajena: «no existe» o «sin permiso»?
2. ¿Una incidencia reabierta (EN_ATENCION) cuenta como no cerrada en el porcentaje del tablero?
3. ¿El técnico debe recibir un aviso cuando una incidencia suya se reabre o su solución se rechaza, o basta con que la vea en su lista?

**Supuestos pendientes de confirmar (una respuesta de IA no es una decisión del cliente)**

| ID | Supuesto | Estado |
|:----|:--------------------------------------------------------|:--------------|
| A1 | Leer una incidencia ajena responde 404 para no revelar su existencia | sin confirmar |
| A2 | El porcentaje usa el estado actual: una incidencia reabierta no cuenta como cerrada | sin confirmar |
| A3 | El código tiene el formato INC-0001, secuencial | Sin confirmar |
| A4 | El porcentaje se redondea mitad hacia arriba, con un decimal y coma decimal | Sin confirmar |
| A5 | Sin notificaciones: el técnico se entera consultando su lista | Sin confirmar |
