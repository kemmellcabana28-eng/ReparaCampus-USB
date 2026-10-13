**Comando:** `python -m pytest -v --junitxml=reporte-pytest.xml`  
**Fecha de ejecución:** 2026-10-12 03:38 UTC  
**SHA:** [COMPLETAR: SHA del commit]  
**Resultado:** 97 casos ejecutados en 52 escenarios; 97 casos aprobados.

| ID | SPEC / AC | Escenario y resultado esperado | Casos | Observado |
|:----|:----------|:----------------------------------------------|:---:|:-----------|
| T01 | AC-S01-01 | entrada válida crea INC-0001 REGISTRADA con evento CREACION. | 1 | Cumple |
| T02 | AC-S01-02 | coordinador y técnico reciben 403 y no se crea nada. | 2 | Cumple |
| T03 | AC-S01-03 | 19/20/500/501 caracteres, contando después de retirar espacios externos. | 6 | Cumple |
| T04 | AC-S01-04 | impacto o riesgo fuera de los valores permitidos se rechazan. | 5 | Cumple |
| T05 | AC-S01-05 | ubicación/categoría fuera de lista se rechazan. | 3 | Cumple |
| T05B | AC-S01-05 | un campo omitido se rechaza. | 1 | Cumple |
| T06 | AC-S01-06 | el texto parecido a HTML se muestra escapado. | 1 | Cumple |
| T07 | AC-S01-07 | si falla el evento, no queda incidencia sin evento (rollback). | 1 | Cumple |
| T08 | AC-S01-01 | autor, estado y código enviados por el cliente se ignoran. | 1 | Cumple |
| T09 | AC-S02-05 | prioridad calculada por el servidor según riesgo e impacto. | 4 | Cumple |
| T10 | AC-S02-06 | una prioridad enviada en el formulario no se usa. | 1 | Cumple |
| T11 | AC-S02-01 | coordinador asigna una REGISTRADA a técnico activo. | 1 | Cumple |
| T12 | AC-S02-02 | solicitante o técnico no pueden asignar. | 2 | Cumple |
| T13 | AC-S02-03 | no se reasigna una ASIGNADA; se conserva el técnico original. | 1 | Cumple |
| T14 | AC-S02-04 | técnico inactivo, de otro rol, inexistente o ilegible se rechaza. | 4 | Cumple |
| T15 | AC-S02-07 | no se asigna una incidencia que ya está EN_ATENCION. | 1 | Cumple |
| T16 | AC-S03-01 | el técnico asignado pasa ASIGNADA a EN_ATENCION con evento. | 1 | Cumple |
| T17 | AC-S03-02 | otro técnico no puede iniciar ni registrar solución. | 1 | Cumple |
| T18 | AC-S03-03 | con la incidencia ASIGNADA no se acepta solución. | 1 | Cumple |
| T19 | AC-S03-04 | la solución admite de 20 a 800 caracteres. | 4 | Cumple |
| T20 | AC-S03-05 | solución válida deja PENDIENTE_VALIDACION con solución y evento. | 1 | Cumple |
| T21 | AC-S03-06 | coordinador y solicitante no inician ni dan solución. | 2 | Cumple |
| T22 | AC-S03-07 | no se inicia una incidencia que ya está EN_ATENCION. | 1 | Cumple |
| T23 | AC-S04-01 | el dueño confirma y queda CERRADA con cierre y evento. | 1 | Cumple |
| T24 | AC-S04-02 | otro solicitante, coordinador o técnico no validan. | 6 | Cumple |
| T25 | AC-S04-02 | nadie más puede reabrir una incidencia CERRADA. | 3 | Cumple |
| T26 | AC-S04-03 | rechazo vuelve a EN_ATENCION, conserva técnico y solución, registra motivo. | 1 | Cumple |
| T27 | AC-S04-04 | el motivo del rechazo admite de 10 a 300 caracteres. | 4 | Cumple |
| T28 | AC-S04-04 | el motivo de la reapertura admite de 10 a 300 caracteres. | 4 | Cumple |
| T29 | AC-S04-05 | con exactamente 48 h desde el cierre, la reapertura se acepta. | 1 | Cumple |
| T30 | AC-S04-06 | 48 h y 1 s después del cierre se rechaza sin cambios. | 1 | Cumple |
| T31 | AC-S04-07 | el plazo se mide desde el último cierre y se conserva todo lo anterior. | 1 | Cumple |
| T32 | AC-S04-08 | validar o reabrir fuera del estado permitido se rechaza. | 3 | Cumple |
| T33 | AC-S05-01 | el coordinador ve todo y los filtros se combinan. | 1 | Cumple |
| T34 | AC-S05-02 | el solicitante solo ve las propias; una ajena responde 404. | 1 | Cumple |
| T35 | AC-S05-03 | el técnico solo ve las asignadas a él. | 1 | Cumple |
| T36 | AC-S05-04 | el historial lista cada acción en orden con autor, estados y detalle. | 1 | Cumple |
| T37 | AC-S05-05 | ni UPDATE ni DELETE sobre eventos, ni con SQL directo. | 1 | Cumple |
| T38 | AC-S05-06 | sin incidencias el porcentaje es 0,0 %. | 1 | Cumple |
| T39 | AC-S05-07 | 1 de 4 cerrada = 25,0 %; reabrirla baja a 0,0 % y conserva el cierre. | 1 | Cumple |
| T40 | AC-S05-08 | solicitante y técnico reciben 403 en el tablero. | 2 | Cumple |
| T41 | AC-S05-09 | un filtro con valor inválido se rechaza. | 2 | Cumple |
| T42 | AC-S05-06/07 | formato con coma, un decimal y redondeo half-up. | 6 | Cumple |
| T43 | S00 (transversal) | Acceso con cuentas de prueba: contraseña errónea y usuario falso devuelven 401. | 1 | Cumple |
| T44 | S00 (transversal) | Un campo 'rol' enviado por el cliente no da identidad ni permisos. | 1 | Cumple |
| T45 | S00 (transversal) | Sin sesión no se opera; tras cerrar sesión se pierde el acceso. | 1 | Cumple |
| T46 | S00 (transversal) | Las cinco cuentas existen y la contraseña no se guarda en claro. | 1 | Cumple |
| T47 | S00 (transversal) | Un 'reinicio' (nueva instancia de la app sobre el mismo archivo) conserva todo. | 1 | Cumple |
| T48 | S00 (transversal) | Con CSRF activo, un POST sin token válido se rechaza y no cambia nada. | 1 | Cumple |
| T49 (integración) | S00 (transversal) | Registrar → asignar → iniciar → proponer → confirmar. | 1 | Cumple |
| T50 (integración) | S00 (transversal) | ... proponer → rechazar → nueva solución → confirmar (conserva ambas soluciones). | 1 | Cumple |
| T51 (integración) | S00 (transversal) | Cierre → reapertura → nueva solución → nuevo cierre (todo se conserva). | 1 | Cumple |
