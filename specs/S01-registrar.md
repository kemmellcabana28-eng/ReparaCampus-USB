# SPEC S01 · Registrar incidencia

**Versión / autor / revisor / fecha:** v1.0 / [COMPLETAR autor] / [COMPLETAR revisor] / [COMPLETAR fecha]

**Requisito asociado:** RF01

**Historia.** Como solicitante, quiero registrar una incidencia con ubicación, categoría, descripción, impacto y riesgo, para que mantenimiento pueda priorizarla y atenderla.

**Alcance y exclusiones.** Crear una incidencia. Excluye edición posterior y adjuntos.

**Entradas (todas obligatorias).** ubicación ∈ {LAB-01, AULA-201, BIB-01}; categoría ∈ {ELECTRICIDAD, HIDRAULICA, MOBILIARIO, TIC}; descripción de 20 a 500 caracteres tras retirar espacios externos; impacto ∈ {BAJO, ALTO}; riesgo para personas booleano. El servidor genera código (INC-0001…), autor (sesión), fecha UTC, estado REGISTRADA y prioridad (S02).

**Precondiciones y permisos.** Sesión activa con rol SOLICITANTE.

**Reglas y proceso.** Validar rol → normalizar con trim → validar entradas → calcular prioridad → en una transacción insertar la incidencia y el evento CREACION.

**Salidas y cambios persistidos.** Incidencia REGISTRADA y su evento CREACION; mensaje con el código.

**Errores y efectos que deben evitarse.** Un rol incorrecto o una entrada inválida se rechaza sin crear incidencia ni evento. No se aceptan estado, autor, fecha, código o prioridad enviados por el cliente.

**Criterios de aceptación**

- **AC-S01-01:** Dado un solicitante autenticado, cuando registra datos válidos, entonces se crea con código, autor, fecha UTC y estado REGISTRADA, y existe un evento CREACION.
- **AC-S01-02:** Dado un coordinador o un técnico autenticado, cuando intenta registrar, entonces recibe 403 y no se crea incidencia ni evento.
- **AC-S01-03:** Dado un solicitante, cuando la descripción tiene 19 caracteres tras el trim, entonces se rechaza; con 20 o 500 se acepta; con 501 se rechaza.
- **AC-S01-04:** Dado un solicitante, cuando envía un impacto fuera de {BAJO, ALTO} o un riesgo que no es booleano, entonces se rechaza sin cambios.
- **AC-S01-05:** Dado un solicitante, cuando omite un campo o envía ubicación o categoría fuera de la lista, entonces se rechaza sin cambios.
- **AC-S01-06:** Dado un solicitante, cuando la descripción contiene `<script>alert(1)</script>`, entonces se guarda como texto y se muestra escapada.
- **AC-S01-07:** Dado un fallo al guardar el evento, cuando se registra, entonces no queda una incidencia sin evento.

**Diseño y tareas vinculadas.** Tablas incidencias y eventos; servicio crear_incidencia(); T-S01-1 validación (AC-03/04/05), T-S01-2 servicio transaccional (AC-01/07), T-S01-3 ruta y formulario (AC-01/02/06), T-S01-4 pruebas.

**Pruebas y resultados esperados.** tests/test_s01_registrar.py (t01–t08), con valores límite 19, 20, 500 y 501.

**Decisión de revisión / versión aprobada:** [COMPLETAR: aprobada / ajustar, revisor, fecha]
