Cada requisito se conecta con su historia, su SPEC, los criterios de aceptación, el código y las pruebas (Requisito → Historia → SPEC → Código → Prueba).

| RF | Historia | SPEC | Criterios | Código (módulo / función) | Pruebas |
|:---:|:--------------------------|:----:|:--------|:-----------------------------------|:----------------|
| RF01 | Como solicitante, quiero registrar una incidencia | S01 | AC-S01-01 a 07 | services.crear_incidencia; routes.nueva; db/schema.sql | T01–T08 |
| RF02 | Como coordinador, quiero priorizar y asignar | S02 | AC-S02-01 a 07 | services.calcular_prioridad, services.asignar; routes.asignar | T09–T15 |
| RF03 | Como técnico, quiero atender y registrar la solución | S03 | AC-S03-01 a 07 | services.iniciar_atencion, services.registrar_solucion | T16–T22 |
| RF04 | Como solicitante, quiero confirmar, rechazar o reabrir | S04 | AC-S04-01 a 08 | services.confirmar, rechazar, reabrir; reloj CLOCK | T23–T32, T49–T51 |
| RF05 | Como usuario, quiero consultar e historizar; como coordinador, un tablero | S05 | AC-S05-01 a 09 | services.listar, detalle, tablero, formatear_porcentaje; triggers de eventos | T33–T42 |
| Transversal | Acceso, sesión, hash, CSRF, persistencia | S00 | Reglas comunes | routes.login, cargar_usuario, verificar_csrf; seed.py | T43–T48 |
