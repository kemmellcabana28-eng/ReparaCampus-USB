# ReparaCampus (prototipo)

Prototipo web para registrar, priorizar, asignar, atender y validar incidencias de infraestructura
de la Universidad Simón Bolívar. Examen ISI SDD, Ingeniería de Software I. Todos los datos son ficticios.

**integrantes: kemmell cabana ,jaider lozano, arnold cantillo ,johan viviescas , sebastian murcia.

## Versiones usadas

| Componente | Versión |
|---|---|
| Python | 3.12.3 |
| Flask | 3.1.3 |
| Werkzeug (hash de contraseñas) | 3.1.7 |
| SQLite (incluido en Python) | 3.45.1 |
| pytest | 9.1.1 |

Las dependencias exactas están en `requirements.txt`.

### Cómo ejecutar el prototipo (guía para quien revisa)

Requisitos: Python 3.12 o superior y Git. No se necesita instalar nada más ni crear cuentas:
la base de datos es un archivo SQLite que se genera localmente y todos los datos son ficticios.

**1. Obtener la versión entregada**

```bash
git clone https://github.com/USUARIO/reparacampus.git
cd reparacampus
git checkout release-examen
```

**2. Crear y activar un entorno virtual**

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Si PowerShell indica que la ejecución de scripts está deshabilitada, ejecute primero
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y repita la activación.
En CMD use `.venv\Scripts\activate.bat`.

Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Crear la base de datos con las cuentas ficticias**

```bash
flask --app app init-db
```

**5. Arrancar la aplicación**

```bash
flask --app app run
```

Abra http://127.0.0.1:5000 en el navegador (la terminal debe seguir abierta; `Ctrl+C` detiene el servidor).

**6. Iniciar sesión** con cualquiera de las cinco cuentas ficticias. Contraseña de todas: `Reparacampus#2026`

| Usuario | Rol | Qué puede hacer |
|---|---|---|
| solicitante1, solicitante2 | SOLICITANTE | Reportar, ver las propias, confirmar / rechazar / reabrir |
| coordinador1 | COORDINADOR | Ver todas, asignar técnico, ver el tablero |
| tecnico1, tecnico2 | TECNICO | Ver sus asignadas, iniciar atención, registrar solución |

Recorrido sugerido: `solicitante1` reporta un daño → `coordinador1` lo asigna a un técnico →
ese técnico inicia la atención y registra la solución → `solicitante1` la confirma o la rechaza →
`coordinador1` revisa el «Tablero». Use una ventana de incógnito para tener dos cuentas a la vez.

**7. Ejecutar las pruebas automatizadas**

```bash
python -m pytest -v
```
Son 97 casos (52 escenarios, 3 de integración con SQLite real); tardan cerca de un minuto.
Solo las de integración: `python -m pytest -m integracion`.

**Empezar de cero:** detenga el servidor, borre `instance/reparacampus.db` y repita el paso 4.

**Versiones con las que se probó:** Python [COMPLETAR versión real], Flask 3.1.3, Werkzeug 3.1.7,
pytest 9.1.1 (detalle en `requirements.txt`).
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
