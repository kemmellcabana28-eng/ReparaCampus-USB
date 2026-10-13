import pytest

from ayudas import accion, crear, ejecutar_sql, estado_de, filas, n_eventos, una


@pytest.mark.parametrize("riesgo,impacto,esperada", [
    ("true", "ALTO", "CRITICA"), ("true", "BAJO", "CRITICA"),
    ("false", "ALTO", "ALTA"), ("false", "BAJO", "NORMAL"),
])
def test_t09_s02_ac05_regla_de_prioridad(app, u, riesgo, impacto, esperada):
    """AC-S02-05: prioridad calculada por el servidor según riesgo e impacto."""
    codigo = crear(u.sol1, riesgo_personas=riesgo, impacto=impacto)
    assert una(app, "SELECT prioridad FROM incidencias WHERE codigo=?", (codigo,)) == esperada


def test_t10_s02_ac06_prioridad_del_cliente_se_ignora(app, u):
    """AC-S02-06: una prioridad enviada en el formulario no se usa."""
    codigo = crear(u.sol1, riesgo_personas="false", impacto="BAJO", prioridad="CRITICA")
    assert una(app, "SELECT prioridad FROM incidencias WHERE codigo=?", (codigo,)) == "NORMAL"


def test_t11_s02_ac01_coordinador_asigna(app, u):
    """AC-S02-01: coordinador asigna una REGISTRADA a técnico activo."""
    codigo = crear(u.sol1)
    resp = accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"])
    assert resp.status_code == 302
    inc = filas(app, "SELECT estado, tecnico_id FROM incidencias")[0]
    assert (inc["estado"], inc["tecnico_id"]) == ("ASIGNADA", u.ids["tecnico1"])
    assert una(app, "SELECT COUNT(*) FROM asignaciones") == 1
    ev = filas(app, "SELECT accion, estado_anterior, estado_nuevo, autor_id FROM eventos "
                    "ORDER BY id")
    assert [e["accion"] for e in ev] == ["CREACION", "ASIGNACION"]
    assert (ev[1]["estado_anterior"], ev[1]["estado_nuevo"], ev[1]["autor_id"]) == \
        ("REGISTRADA", "ASIGNADA", u.ids["coordinador1"])


@pytest.mark.parametrize("quien", ["sol1", "tec1"])
def test_t12_s02_ac02_solo_coordinador_asigna(app, u, quien):
    """AC-S02-02: solicitante o técnico no pueden asignar."""
    codigo = crear(u.sol1)
    eventos_antes = n_eventos(app)
    resp = accion(getattr(u, quien), codigo, "asignar", tecnico_id=u.ids["tecnico1"])
    assert resp.status_code == 403
    assert estado_de(app, codigo) == "REGISTRADA"
    assert n_eventos(app) == eventos_antes


def test_t13_s02_ac03_asignacion_repetida(app, u):
    """AC-S02-03: no se reasigna una ASIGNADA; se conserva el técnico original."""
    codigo = crear(u.sol1)
    accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"])
    eventos_antes = n_eventos(app)
    resp = accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico2"])
    assert resp.status_code == 409
    assert una(app, "SELECT tecnico_id FROM incidencias") == u.ids["tecnico1"]
    assert una(app, "SELECT COUNT(*) FROM asignaciones") == 1
    assert n_eventos(app) == eventos_antes


@pytest.mark.parametrize("tecnico", ["inactivo", "solicitante", "inexistente", "texto"])
def test_t14_s02_ac04_tecnico_invalido(app, u, tecnico):
    """AC-S02-04: técnico inactivo, de otro rol, inexistente o ilegible se rechaza."""
    ejecutar_sql(app, "UPDATE usuarios SET activo=0 WHERE username='tecnico2'")
    valor = {"inactivo": u.ids["tecnico2"], "solicitante": u.ids["solicitante1"],
             "inexistente": 9999, "texto": "abc"}[tecnico]
    codigo = crear(u.sol1)
    resp = accion(u.coord, codigo, "asignar", tecnico_id=str(valor))
    assert resp.status_code == 400
    assert estado_de(app, codigo) == "REGISTRADA"
    assert una(app, "SELECT COUNT(*) FROM asignaciones") == 0


def test_t15_s02_ac07_estado_incompatible(app, u):
    """AC-S02-07: no se asigna una incidencia que ya está EN_ATENCION."""
    from ayudas import en_estado
    codigo = en_estado(u, "EN_ATENCION")
    resp = accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico2"])
    assert resp.status_code == 409
    assert una(app, "SELECT tecnico_id FROM incidencias") == u.ids["tecnico1"]
