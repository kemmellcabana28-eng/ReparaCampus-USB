import pytest

from ayudas import (MOTIVO_OK, SOLUCION_OK, accion, en_estado, estado_de, filas, n_eventos, una)


def test_t23_s04_ac01_confirmar(app, u):
    """AC-S04-01: el dueño confirma y queda CERRADA con cierre y evento."""
    codigo = en_estado(u, "PENDIENTE_VALIDACION")
    assert accion(u.sol1, codigo, "confirmar").status_code == 302
    assert estado_de(app, codigo) == "CERRADA"
    assert una(app, "SELECT COUNT(*) FROM cierres") == 1
    ultimo = filas(app, "SELECT * FROM eventos ORDER BY id DESC LIMIT 1")[0]
    assert (ultimo["accion"], ultimo["estado_nuevo"]) == ("CIERRE", "CERRADA")


@pytest.mark.parametrize("quien", ["sol2", "coord", "tec1"])
@pytest.mark.parametrize("nombre", ["confirmar", "rechazar"])
def test_t24_s04_ac02_solo_el_dueno_valida(app, u, quien, nombre):
    """AC-S04-02: otro solicitante, coordinador o técnico no validan."""
    codigo = en_estado(u, "PENDIENTE_VALIDACION")
    antes = n_eventos(app)
    resp = accion(getattr(u, quien), codigo, nombre, motivo=MOTIVO_OK)
    assert resp.status_code == 403
    assert estado_de(app, codigo) == "PENDIENTE_VALIDACION"
    assert n_eventos(app) == antes
    assert una(app, "SELECT COUNT(*) FROM cierres") == 0


@pytest.mark.parametrize("quien", ["sol2", "coord", "tec1"])
def test_t25_s04_ac02_solo_el_dueno_reabre(app, u, quien):
    """AC-S04-02: nadie más puede reabrir una incidencia CERRADA."""
    codigo = en_estado(u, "CERRADA")
    antes = n_eventos(app)
    assert accion(getattr(u, quien), codigo, "reabrir", motivo=MOTIVO_OK).status_code == 403
    assert estado_de(app, codigo) == "CERRADA"
    assert n_eventos(app) == antes


def test_t26_s04_ac03_rechazo_valido(app, u):
    """AC-S04-03: rechazo vuelve a EN_ATENCION, conserva técnico y solución, registra motivo."""
    codigo = en_estado(u, "PENDIENTE_VALIDACION")
    assert accion(u.sol1, codigo, "rechazar", motivo=MOTIVO_OK).status_code == 302
    inc = filas(app, "SELECT estado, tecnico_id FROM incidencias")[0]
    assert (inc["estado"], inc["tecnico_id"]) == ("EN_ATENCION", u.ids["tecnico1"])
    assert una(app, "SELECT texto FROM soluciones") == SOLUCION_OK
    ultimo = filas(app, "SELECT * FROM eventos ORDER BY id DESC LIMIT 1")[0]
    assert (ultimo["accion"], ultimo["detalle"], ultimo["autor_id"], ultimo["fecha"]) == \
        ("RECHAZO", "El daño sigue presente", u.ids["solicitante1"], "2026-03-02T10:00:00+00:00")


@pytest.mark.parametrize("largo,esperado", [(9, 400), (10, 302), (300, 302), (301, 400)])
def test_t27_s04_ac04_limites_motivo_rechazo(app, u, largo, esperado):
    """AC-S04-04: el motivo del rechazo admite de 10 a 300 caracteres."""
    codigo = en_estado(u, "PENDIENTE_VALIDACION")
    resp = accion(u.sol1, codigo, "rechazar", motivo="m" * largo)
    assert resp.status_code == esperado
    assert estado_de(app, codigo) == ("EN_ATENCION" if esperado == 302 else "PENDIENTE_VALIDACION")


@pytest.mark.parametrize("largo,esperado", [(9, 400), (10, 302), (300, 302), (301, 400)])
def test_t28_s04_ac04_limites_motivo_reapertura(app, u, largo, esperado):
    """AC-S04-04: el motivo de la reapertura admite de 10 a 300 caracteres."""
    codigo = en_estado(u, "CERRADA")
    resp = accion(u.sol1, codigo, "reabrir", motivo="m" * largo)
    assert resp.status_code == esperado
    assert estado_de(app, codigo) == ("EN_ATENCION" if esperado == 302 else "CERRADA")


def test_t29_s04_ac05_reapertura_exactamente_48h(app, u, reloj):
    """AC-S04-05: con exactamente 48 h desde el cierre, la reapertura se acepta."""
    codigo = en_estado(u, "CERRADA")
    reloj.avanzar(hours=48)
    assert accion(u.sol1, codigo, "reabrir", motivo=MOTIVO_OK).status_code == 302
    inc = filas(app, "SELECT estado, tecnico_id FROM incidencias")[0]
    assert (inc["estado"], inc["tecnico_id"]) == ("EN_ATENCION", u.ids["tecnico1"])


def test_t30_s04_ac06_reapertura_pasadas_48h(app, u, reloj):
    """AC-S04-06: 48 h y 1 s después del cierre se rechaza sin cambios."""
    codigo = en_estado(u, "CERRADA")
    antes = n_eventos(app)
    reloj.avanzar(hours=48, seconds=1)
    assert accion(u.sol1, codigo, "reabrir", motivo=MOTIVO_OK).status_code == 409
    assert estado_de(app, codigo) == "CERRADA"
    assert n_eventos(app) == antes
    assert una(app, "SELECT COUNT(*) FROM cierres") == 1


def test_t31_s04_ac07_plazo_desde_el_ultimo_cierre(app, u, reloj):
    """AC-S04-07: el plazo se mide desde el último cierre y se conserva todo lo anterior."""
    codigo = en_estado(u, "CERRADA")          # cierre 1 en T0
    reloj.avanzar(hours=40)
    assert accion(u.sol1, codigo, "reabrir", motivo=MOTIVO_OK).status_code == 302
    assert accion(u.tec1, codigo, "solucion", solucion="Segunda solución: se cambió el cableado.").status_code == 302
    reloj.avanzar(hours=60)                   # T0 + 100 h
    assert accion(u.sol1, codigo, "confirmar").status_code == 302   # cierre 2
    reloj.avanzar(hours=47)                   # 147 h tras el cierre 1, 47 h tras el cierre 2
    assert accion(u.sol1, codigo, "reabrir", motivo=MOTIVO_OK).status_code == 302
    assert una(app, "SELECT COUNT(*) FROM cierres") == 2
    assert una(app, "SELECT COUNT(*) FROM soluciones") == 2
    assert una(app, "SELECT tecnico_id FROM incidencias") == u.ids["tecnico1"]


@pytest.mark.parametrize("nombre,estado_inicial", [
    ("confirmar", "REGISTRADA"), ("rechazar", "EN_ATENCION"), ("reabrir", "PENDIENTE_VALIDACION"),
])
def test_t32_s04_ac08_estados_incompatibles(app, u, nombre, estado_inicial):
    """AC-S04-08: validar o reabrir fuera del estado permitido se rechaza."""
    codigo = en_estado(u, estado_inicial)
    antes = n_eventos(app)
    assert accion(u.sol1, codigo, nombre, motivo=MOTIVO_OK).status_code == 409
    assert estado_de(app, codigo) == estado_inicial
    assert n_eventos(app) == antes
