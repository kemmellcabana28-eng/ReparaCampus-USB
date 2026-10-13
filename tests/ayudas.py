"""Ayudas de prueba. Los valores esperados se escriben a mano en cada prueba."""
import sqlite3
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.seed import CLAVE_DEMO

T0 = datetime(2026, 3, 2, 10, 0, 0, tzinfo=timezone.utc)  # fecha ficticia fija

VALIDO = {
    "ubicacion": "LAB-01", "categoria": "ELECTRICIDAD",
    "descripcion": "El tomacorriente del fondo suelta chispas al conectar equipos.",
    "impacto": "ALTO", "riesgo_personas": "false",
}
SOLUCION_OK = "Se reemplazó el tomacorriente y se verificó el circuito con carga."
MOTIVO_OK = "El daño sigue presente"


class Reloj:
    """Reloj controlado: el servidor lo usa en lugar de la hora real."""
    def __init__(self, inicio):
        self.ahora = inicio

    def __call__(self):
        return self.ahora

    def avanzar(self, **kwargs):
        self.ahora += timedelta(**kwargs)


def entrar(app, username):
    cliente = app.test_client()
    resp = cliente.post("/login", data={"username": username, "password": CLAVE_DEMO})
    assert resp.status_code == 302
    return cliente


def filas(app, sql, params=()):
    con = sqlite3.connect(app.config["DATABASE"])
    con.row_factory = sqlite3.Row
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def una(app, sql, params=()):
    return filas(app, sql, params)[0][0]


def ejecutar_sql(app, sql, params=()):
    con = sqlite3.connect(app.config["DATABASE"])
    try:
        con.execute(sql, params)
        con.commit()
    finally:
        con.close()


def construir_usuarios(app):
    nombres = ["solicitante1", "solicitante2", "coordinador1", "tecnico1", "tecnico2"]
    ids = {n: una(app, "SELECT id FROM usuarios WHERE username=?", (n,)) for n in nombres}
    return SimpleNamespace(
        sol1=entrar(app, "solicitante1"), sol2=entrar(app, "solicitante2"),
        coord=entrar(app, "coordinador1"), tec1=entrar(app, "tecnico1"),
        tec2=entrar(app, "tecnico2"), ids=ids)


def registrar(cliente, **cambios):
    datos = dict(VALIDO)
    datos.update(cambios)
    return cliente.post("/incidencias/nueva", data=datos)


def crear(cliente, **cambios):
    resp = registrar(cliente, **cambios)
    assert resp.status_code == 302
    return resp.headers["Location"].rsplit("/", 1)[1]


def accion(cliente, codigo, nombre, **datos):
    return cliente.post(f"/incidencias/{codigo}/{nombre}", data=datos)


ORDEN = ["REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA"]


def en_estado(u, estado, **cambios):
    """Lleva una incidencia nueva hasta `estado` por el camino legal (técnico1)."""
    codigo = crear(u.sol1, **cambios)
    pasos = ORDEN.index(estado)
    if pasos >= 1:
        assert accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"]).status_code == 302
    if pasos >= 2:
        assert accion(u.tec1, codigo, "iniciar").status_code == 302
    if pasos >= 3:
        assert accion(u.tec1, codigo, "solucion", solucion=SOLUCION_OK).status_code == 302
    if pasos >= 4:
        assert accion(u.sol1, codigo, "confirmar").status_code == 302
    return codigo


def estado_de(app, codigo):
    return una(app, "SELECT estado FROM incidencias WHERE codigo=?", (codigo,))


def n_eventos(app):
    return una(app, "SELECT COUNT(*) FROM eventos")
