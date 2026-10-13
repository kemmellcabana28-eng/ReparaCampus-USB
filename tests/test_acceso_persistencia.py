import sqlite3

from app import create_app
from app.seed import CLAVE_DEMO
from ayudas import T0, Reloj, construir_usuarios, crear, estado_de, filas, una, registrar, accion


def test_t43_acceso_login_correcto_e_incorrecto(app):
    """Acceso con cuentas de prueba: contraseña errónea y usuario falso devuelven 401."""
    c = app.test_client()
    assert c.post("/login", data={"username": "tecnico1", "password": "mala"}).status_code == 401
    assert c.post("/login", data={"username": "fantasma", "password": CLAVE_DEMO}).status_code == 401
    assert c.get("/incidencias").status_code == 302  # sigue sin sesión
    assert c.post("/login", data={"username": "tecnico1", "password": CLAVE_DEMO}).status_code == 302
    assert c.get("/incidencias").status_code == 200


def test_t44_acceso_selector_de_rol_no_autentica(app, u):
    """Un campo 'rol' enviado por el cliente no da identidad ni permisos."""
    c = app.test_client()
    resp = c.post("/login", data={"username": "solicitante1", "rol": "COORDINADOR"})
    assert resp.status_code == 401
    # un solicitante autenticado que envía rol=COORDINADOR sigue siendo solicitante
    assert u.sol1.get("/tablero?rol=COORDINADOR").status_code == 403


def test_t45_acceso_sin_sesion_y_logout(app, u):
    """Sin sesión no se opera; tras cerrar sesión se pierde el acceso."""
    codigo = crear(u.sol1)
    anonimo = app.test_client()
    resp = anonimo.post(f"/incidencias/{codigo}/asignar", data={"tecnico_id": "4"})
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
    assert estado_de(app, codigo) == "REGISTRADA"
    assert u.sol1.post("/logout").status_code == 302
    assert u.sol1.get("/incidencias").status_code == 302


def test_t46_acceso_contrasenas_con_hash(app):
    """Las cinco cuentas existen y la contraseña no se guarda en claro."""
    cuentas = filas(app, "SELECT username, rol, password_hash FROM usuarios ORDER BY id")
    assert [c["username"] for c in cuentas] == [
        "solicitante1", "solicitante2", "coordinador1", "tecnico1", "tecnico2"]
    assert [c["rol"] for c in cuentas] == [
        "SOLICITANTE", "SOLICITANTE", "COORDINADOR", "TECNICO", "TECNICO"]
    for c in cuentas:
        assert CLAVE_DEMO not in c["password_hash"]
        assert c["password_hash"].startswith(("scrypt:", "pbkdf2:"))


def test_t47_persistencia_reinicio_conserva_datos(app, u, tmp_path):
    """Un 'reinicio' (nueva instancia de la app sobre el mismo archivo) conserva todo."""
    codigo = crear(u.sol1, riesgo_personas="true")
    accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"])
    reiniciada = create_app({"DATABASE": app.config["DATABASE"], "TESTING": True,
                             "CSRF_ENABLED": False, "CLOCK": Reloj(T0)})
    nuevos = construir_usuarios(reiniciada)
    html = nuevos.sol1.get(f"/incidencias/{codigo}").get_data(as_text=True)
    assert "ASIGNADA" in html and "CRITICA" in html
    assert una(reiniciada, "SELECT COUNT(*) FROM eventos") == 2


def test_t48_seguridad_csrf_rechaza_post_sin_token(tmp_path):
    """Con CSRF activo, un POST sin token válido se rechaza y no cambia nada."""
    app = create_app({"DATABASE": str(tmp_path / "csrf.db"), "TESTING": True, "CSRF_ENABLED": True})
    with app.app_context():
        from app.db import init_db
        from app.seed import seed
        init_db(); seed()
    c = app.test_client()
    assert c.post("/login", data={"username": "solicitante1", "password": CLAVE_DEMO}).status_code == 400
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0
