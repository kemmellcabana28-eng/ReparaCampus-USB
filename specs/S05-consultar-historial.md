# SPEC S05 · Consultar e historizar

**Versión / autor / revisor / fecha:** v1.0 /   johan viviescas/ Arnold cantillo/8-10-2026

**Requisito asociado:** RF05

**Historia.** Como usuario del sistema, quiero consultar las incidencias que me corresponden y ver su historial, y como coordinador un tablero, para dar seguimiento al trabajo.

**Alcance y exclusiones.** Listado con filtros, detalle con historial y tablero. Excluye edición o borrado de eventos.

**Entradas.** Filtros opcionales de estado y de prioridad (valores permitidos).

**Precondiciones y permisos.** SOLICITANTE: solo las propias. TECNICO: solo las asignadas a él. COORDINADOR: todas, más el tablero.

**Reglas y proceso.** El listado aplica los filtros dentro del alcance del rol. El detalle muestra el historial completo (creación, asignación, inicio, soluciones, motivos, cierres y reaperturas) con autor, fecha, estados y acción. Acceder a una incidencia ajena responde 404 (supuesto A1). El historial es solo de adición, también a nivel de base de datos (triggers). Tablero: cantidades por estado y por prioridad, incidencias CRITICA no cerradas y porcentaje de cierre = CERRADAS / total × 100 con un decimal; con cero registros muestra 0,0 %.

**Salidas y cambios persistidos.** Solo lectura; no modifica datos.

**Errores y efectos que deben evitarse.** Los filtros inválidos se rechazan. Una operación rechazada no agrega eventos.

**Criterios de aceptación**

- **AC-S05-01:** Dado un coordinador, cuando lista, entonces ve todas; con estado=ASIGNADA y prioridad=CRITICA ve solo las que cumplen ambos filtros.
- **AC-S05-02:** Dado un solicitante, cuando lista o abre un detalle, entonces solo accede a las propias; una ajena responde 404.
- **AC-S05-03:** Dado un técnico, cuando lista, entonces solo ve las asignadas a él.
- **AC-S05-04:** Dado una incidencia con un flujo completo, cuando se consulta su historial, entonces muestra todos los eventos en orden con autor, fecha, estados y acción.
- **AC-S05-05:** Dado un evento existente, cuando se intenta actualizar o borrar (desde la aplicación o con SQL directo), entonces la operación falla y el historial no cambia.
- **AC-S05-06:** Dado cero incidencias, cuando el coordinador abre el tablero, entonces el porcentaje de cierre es 0,0 %.
- **AC-S05-07:** Dado cuatro incidencias y una CERRADA, cuando se abre el tablero, entonces muestra 25,0 %; si se reabre, baja a 0,0 % y el cierre anterior sigue en el historial.
- **AC-S05-08:** Dado un solicitante o un técnico, cuando intenta abrir el tablero, entonces recibe 403.
- **AC-S05-09:** Dado un filtro con un valor inválido, cuando se consulta, entonces se rechaza con 400 y no se devuelven resultados engañosos.

**Diseño y tareas vinculadas.** Consultas con alcance por rol; triggers BEFORE UPDATE y BEFORE DELETE sobre eventos; redondeo con Decimal ROUND_HALF_UP; T-S05-1 listado y filtros, T-S05-2 detalle e historial, T-S05-3 triggers, T-S05-4 tablero, T-S05-5 pruebas.

**Pruebas y resultados esperados.** tests/test_s05_consultar_historial.py (t33–t42).

**Decisión de revisión / versión aprobada:** aprobada / jaider Lozano/8-10-2026
