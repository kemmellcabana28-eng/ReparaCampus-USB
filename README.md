# ReparaCampus (prototipo)

Prototipo web para registrar, priorizar, asignar, atender y validar incidencias de infraestructura
de la Universidad Simón Bolívar. Examen ISI SDD, Ingeniería de Software I. Todos los datos son ficticios.

## Versiones usadas

| Componente | Versión |
|---|---|
| Python | 3.12.3 |
| Flask | 3.1.3 |
| Werkzeug (hash de contraseñas) | 3.1.7 |
| SQLite (incluido en Python) | 3.45.1 |
| pytest | 9.1.1 |

Las dependencias exactas están en `requirements.txt`.

## Instalación y arranque (desde una copia limpia)

```bash
git clone <URL-DEL-REPOSITORIO> && cd reparacampus
git checkout release-examen
python -m venv .venv
# Windows: .venv\Scripts\activate      Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db      # crea el esquema (db/schema.sql) y las cinco cuentas ficticias
flask --app app run          # http://127.0.0.1:5000
```

La base queda en `instance/reparacampus.db` y persiste al reiniciar. Para empezar de cero, borre ese archivo y repita `init-db`.
En un entorno real, defina la variable `SECRET_KEY` antes de arrancar.

## Cuentas ficticias (contraseña de todas: `Reparacampus#2026`)

| Usuario | Rol |
|---|---|
| solicitante1, solicitante2 | SOLICITANTE |
| coordinador1 | COORDINADOR |
| tecnico1, tecnico2 | TECNICO (activos) |

## Pruebas

```bash
python -m pytest -v --junitxml=reporte-pytest.xml     # 97 casos (52 escenarios), 3 de integración
python -m pytest -m integracion                       # solo las 3 de integración (SQLite real)
python docs/generar_reporte.py                        # tabla de resultados -> docs/reporte-pruebas.md
```

Cada prueba usa una base SQLite temporal propia y un reloj controlado (no se cambia el reloj del sistema).
Los resultados esperados están escritos a mano en cada prueba, sin calcularlos con la función de producción.

## Estructura

```
app/        routes.py (web), services.py (reglas y permisos), db.py, seed.py, templates/, static/
db/         schema.sql (esquema, restricciones y triggers del historial)
specs/      S00 a S05 (especificación, diseño, tareas y criterios de aceptación)
tests/      pytest (conftest.py, ayudas.py y un archivo por funcionalidad)
docs/       diagramas (.puml y .png), bitácora de IA, riesgos, trazabilidad, reporte de pruebas
```

## Limitaciones conocidas

- Sin límite de intentos de inicio de sesión ni bloqueo de cuentas.
- Sin notificaciones, adjuntos ni hosting (fuera de alcance del examen).
- Leer una incidencia ajena responde 404, pero operar sobre una ajena responde 403 (supuesto A1 de S00, sin confirmar con el cliente).
- Las pruebas usan el cliente de pruebas de Flask; no hay pruebas automáticas de navegador.
