import pytest
from ayudas import SOLUCION_OK, accion, crear, en_estado, estado_de, filas, n_eventos, una

def test_t16_s03_ac01_tecnico_inicia(app, u):
    """AC-S03-01: el técnico asignado pasa ASIGNADA a EN_ATENCION con evento."""
    codigo = en_estado(u, "ASIGNADA")
    resp = accion(u.tec1, codigo, "iniciar")
    assert resp.status_code == 302
    assert estado_de(app, codigo) == "EN_ATENCION"
    ultimo = filas(app, "SELECT * FROM eventos ORDER BY id DESC LIMIT 1")[0]
    assert (ultimo["accion"], ultimo["estado_anterior"], ultimo["estado_nuevo"]) == \
        ("INICIO_ATENCION", "ASIGNADA", "EN_ATENCION")
    
def test_t17_s03_ac02_tecnico_no_asignado(app, u):
    """AC-S03-02: otro técnico no puede iniciar ni registrar solución."""
    codigo = en_estado(u, "ASIGNADA")
    antes = n_eventos(app)
    assert accion(u.tec2, codigo, "iniciar").status_code == 403
    assert estado_de(app, codigo) == "ASIGNADA"
    accion(u.tec1, codigo, "iniciar")
    antes = n_eventos(app)
    assert accion(u.tec2, codigo, "solucion", solucion=SOLUCION_OK).status_code == 403
    assert estado_de(app, codigo) == "EN_ATENCION"
    assert una(app, "SELECT COUNT(*) FROM soluciones") == 0
    assert n_eventos(app) == antes
    
def test_t18_s03_ac03_solucion_antes_de_iniciar(app, u):
    """AC-S03-03: con la incidencia ASIGNADA no se acepta solución."""
    codigo = en_estado(u, "ASIGNADA")
    antes = n_eventos(app)
    assert accion(u.tec1, codigo, "solucion", solucion=SOLUCION_OK).status_code == 409
    assert estado_de(app, codigo) == "ASIGNADA"
    assert una(app, "SELECT COUNT(*) FROM soluciones") == 0
    assert n_eventos(app) == antes
@pytest.mark.parametrize("largo,esperado", [(19, 400), (20, 302), (800, 302), (801, 400)])

def test_t19_s03_ac04_limites_solucion(app, u, largo, esperado):
    """AC-S03-04: la solución admite de 20 a 800 caracteres."""
    codigo = en_estado(u, "EN_ATENCION")
    resp = accion(u.tec1, codigo, "solucion", solucion="s" * largo)
    assert resp.status_code == esperado
    assert estado_de(app, codigo) == ("PENDIENTE_VALIDACION" if esperado == 302 else "EN_ATENCION")

def test_t20_s03_ac05_solucion_valida(app, u):
    """AC-S03-05: solución válida deja PENDIENTE_VALIDACION con solución y evento."""
    codigo = en_estado(u, "EN_ATENCION")
    assert accion(u.tec1, codigo, "solucion", solucion="  " + SOLUCION_OK + "  ").status_code == 302
    assert estado_de(app, codigo) == "PENDIENTE_VALIDACION"
    sol = filas(app, "SELECT * FROM soluciones")
    assert len(sol) == 1 and sol[0]["texto"] == SOLUCION_OK
    ultimo = filas(app, "SELECT * FROM eventos ORDER BY id DESC LIMIT 1")[0]
    assert (ultimo["accion"], ultimo["detalle"]) == ("SOLUCION", SOLUCION_OK)

@pytest.mark.parametrize("quien", ["coord", "sol1"])
def test_t21_s03_ac06_otros_roles_no_atienden(app, u, quien):
    """AC-S03-06: coordinador y solicitante no inician ni dan solución."""
    codigo = en_estado(u, "ASIGNADA")
    assert accion(getattr(u, quien), codigo, "iniciar").status_code == 403
    assert estado_de(app, codigo) == "ASIGNADA"
    accion(u.tec1, codigo, "iniciar")
    assert accion(getattr(u, quien), codigo, "solucion", solucion=SOLUCION_OK).status_code == 403
    assert estado_de(app, codigo) == "EN_ATENCION"

def test_t22_s03_ac07_iniciar_en_estado_incorrecto(app, u):
    """AC-S03-07: no se inicia una incidencia que ya está EN_ATENCION."""
    codigo = en_estado(u, "EN_ATENCION")
    antes = n_eventos(app)
    assert accion(u.tec1, codigo, "iniciar").status_code == 409
    assert n_eventos(app) == antes
