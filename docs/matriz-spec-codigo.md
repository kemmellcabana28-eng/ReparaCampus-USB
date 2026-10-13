Comparación de cada criterio con el código y con la prueba que lo comprueba. El resultado esperado se definió en la SPEC antes de ejecutar; el observado viene del reporte de ejecución (sección 7.3).

| Criterio | Comportamiento esperado | Módulo / función | Prueba | Estado |
|:------|:--------------------------------------|:-------------------|:-----|:------|
| AC-S01-01 | Registro válido: INC-0001, REGISTRADA, autor, fecha UTC, evento CREACION | services.crear_incidencia | T01, T08 | Cumple |
| AC-S01-02 | Coordinador y técnico: 403, sin cambios | services._exigir_rol | T02 | Cumple |
| AC-S01-03 | Descripción 19 y 501 rechazadas; 20 y 500 aceptadas; trim | services._texto | T03 | Cumple |
| AC-S01-04 | Impacto y riesgo inválidos rechazados | services._opcion, _booleano | T04 | Cumple |
| AC-S01-05 | Campos faltantes o fuera de lista rechazados | services._opcion | T05, T05B | Cumple |
| AC-S01-06 | HTML escapado | plantillas Jinja (autoescape) | T06 | Cumple |
| AC-S01-07 | Fallo al guardar el evento: sin incidencia | services.transaccion | T07 | Cumple |
| AC-S02-01 | Asignación válida a ASIGNADA con evento | services.asignar | T11 | Cumple |
| AC-S02-02 | Solo coordinador asigna | services._exigir_rol | T12 | Cumple |
| AC-S02-03 | Asignación repetida rechazada; técnico se conserva | services.asignar | T13 | Cumple |
| AC-S02-04 | Técnico inactivo, de otro rol o inexistente rechazado | services.asignar | T14 | Cumple |
| AC-S02-05 | CRITICA / ALTA / NORMAL según riesgo e impacto | services.calcular_prioridad | T09 | Cumple |
| AC-S02-06 | Prioridad del cliente ignorada | services.crear_incidencia | T10 | Cumple |
| AC-S02-07 | Solo se asigna REGISTRADA | services.asignar | T15 | Cumple |
| AC-S03-01 | Técnico asignado inicia: EN_ATENCION | services.iniciar_atencion | T16 | Cumple |
| AC-S03-02 | Técnico no asignado: 403 | services._cargar_para_tecnico | T17 | Cumple |
| AC-S03-03 | Sin solución antes de iniciar | services.registrar_solucion | T18 | Cumple |
| AC-S03-04 | Solución 19/801 rechazada; 20/800 aceptada | services._texto | T19 | Cumple |
| AC-S03-05 | PENDIENTE_VALIDACION con solución y evento | services.registrar_solucion | T20 | Cumple |
| AC-S03-06 | Coordinador y solicitante: 403 | services._exigir_rol | T21 | Cumple |
| AC-S03-07 | Solo se inicia desde ASIGNADA | services.iniciar_atencion | T22 | Cumple |
| AC-S04-01 | Dueño confirma: CERRADA, cierre y evento | services.confirmar | T23, T49 | Cumple |
| AC-S04-02 | No dueño y otros roles: 403 | services._cargar_para_dueno | T24, T25 | Cumple |
| AC-S04-03 | Rechazo: EN_ATENCION, mismo técnico, solución conservada | services.rechazar | T26, T50 | Cumple |
| AC-S04-04 | Motivo 9/301 rechazado; 10/300 aceptado | services._texto | T27, T28 | Cumple |
| AC-S04-05 | Reapertura a exactamente 48 h aceptada | services.reabrir | T29 | Cumple |
| AC-S04-06 | Reapertura a 48 h y 1 s rechazada sin cambios | services.reabrir | T30 | Cumple |
| AC-S04-07 | Plazo desde el último cierre; todo se conserva | services.reabrir | T31, T51 | Cumple |
| AC-S04-08 | Estados incompatibles rechazados | services.confirmar, rechazar, reabrir | T32 | Cumple |
| AC-S05-01 | Coordinador ve todo; filtros combinados | services.listar | T33 | Cumple |
| AC-S05-02 | Solicitante solo lo propio; ajena 404 | services._alcance, detalle | T34 | Cumple |
| AC-S05-03 | Técnico solo lo asignado | services._alcance | T35 | Cumple |
| AC-S05-04 | Historial completo y ordenado | services.detalle; eventos | T36 | Cumple |
| AC-S05-05 | Eventos inmutables | triggers en db/schema.sql | T37 | Cumple |
| AC-S05-06 | Tablero vacío: 0,0 % | services.tablero, formatear_porcentaje | T38, T42 | Cumple |
| AC-S05-07 | 1 de 4 = 25,0 %; reabrir lo reduce y conserva el cierre | services.tablero | T39, T42 | Cumple |
| AC-S05-08 | Tablero solo para coordinador | services.tablero | T40 | Cumple |
| AC-S05-09 | Filtro inválido: 400 | services.listar | T41 | Cumple |
