# Checklist de entrega (completar antes del cierre)

## Lo que ya viene hecho en este paquete
- [x] Código Flask + SQLite, esquema, seed, plantillas (`app/`, `db/`)
- [x] 97 casos de prueba (52 escenarios), 3 de integración con SQLite real (`tests/`)
- [x] SPECS S00–S05 con 38 criterios Dado/Cuando/Entonces (`specs/`)
- [x] Diagramas PlantUML + PNG (`docs/diagramas/`)
- [x] Informe con las 11 secciones (`docs/informe/`, .docx editable y .pdf)

## Lo que SOLO ustedes pueden hacer (no se puede inventar)
1. Crear el repo en GitHub, tablero (Por hacer / En progreso / En revisión / Terminado) e issues; dar acceso al docente.
2. Subir el código por ramas y pull requests: cada integrante con una contribución propia y al menos una revisión de un cambio ajeno (reparto circular propuesto en la sección 10).
3. Que otra persona revise cada SPEC ANTES del código y dejar fecha, versión y decisión en cada archivo de `specs/`.
4. Ejecutar `python -m pytest -v --junitxml=reporte-pytest.xml` y `python docs/generar_reporte.py` en su repo; anotar fecha y SHA.
5. Crear el tag `release-examen`, anotar el SHA completo y la URL en la sección 9.
6. Completar en el .docx todo lo marcado en amarillo: [COMPLETAR ...] (códigos, grupo, docente, fecha, equipo, commits/PR, aceptación).
7. Confirmar o corregir las "decisiones humanas" de la bitácora de IA y poner su nombre como autor de cada intervención.
8. Regenerar el PDF (Word/Writer → Exportar a PDF), actualizar el índice, abrirlo y verificar enlaces.
9. Nombrar el archivo `Examen_ISI_SDD_ReparaCampus_Equipo_<nombre>.pdf` y que TODOS lo adjunten en el aula.

Si algo no se ejecutó o quedó incompleto, declárenlo como pendiente: no lo registren como aprobado.
