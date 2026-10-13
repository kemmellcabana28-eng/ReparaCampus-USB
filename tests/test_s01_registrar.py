import pytest

from ayudas import VALIDO, crear, filas, n_eventos, registrar, una, ejecutar_sql


def test_t01_s01_ac01_registro_valido(app, u):
    """AC-S01-01: entrada válida crea INC-0001 REGISTRADA con evento CREACION."""
    resp = registrar(u.sol1)
    assert resp.status_code == 302
    inc = filas(app, "SELECT * FROM incidencias")[0]
    assert inc["codigo"] == "INC-0001"
    assert inc["estado"] == "REGISTRADA"
    assert inc["solicitante_id"] == u.ids["solicitante1"]
    assert inc["creada_en"] == "2026-03-02T10:00:00+00:00"
    ev = filas(app, "SELECT * FROM eventos")
    assert len(ev) == 1
    assert (ev[0]["accion"], ev[0]["estado_anterior"], ev[0]["estado_nuevo"]) == \
        ("CREACION", None, "REGISTRADA")
    assert ev[0]["autor_id"] == u.ids["solicitante1"]


@pytest.mark.parametrize("quien", ["coord", "tec1"])
def test_t02_s01_ac02_solo_solicitante_registra(app, u, quien):
    """AC-S01-02: coordinador y técnico reciben 403 y no se crea nada."""
    resp = registrar(getattr(u, quien))
    assert resp.status_code == 403
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0
    assert n_eventos(app) == 0


@pytest.mark.parametrize("descripcion,esperado", [
    ("x" * 19, 400), ("x" * 20, 302), ("x" * 500, 302), ("x" * 501, 400),
    ("   " + "x" * 19 + "   ", 400),  # 19 tras trim
    ("  " + "x" * 20 + "  ", 302),    # 20 tras trim
])
def test_t03_s01_ac03_limites_descripcion(app, u, descripcion, esperado):
    """AC-S01-03: 19/20/500/501 caracteres, contando después de retirar espacios externos."""
    resp = registrar(u.sol1, descripcion=descripcion)
    assert resp.status_code == esperado
    assert una(app, "SELECT COUNT(*) FROM incidencias") == (1 if esperado == 302 else 0)
    if esperado == 302:
        assert una(app, "SELECT descripcion FROM incidencias") == descripcion.strip()


@pytest.mark.parametrize("cambio", [
    {"impacto": "MEDIO"}, {"impacto": "alto"}, {"riesgo_personas": "talvez"},
    {"riesgo_personas": "1"}, {"riesgo_personas": ""},
])
def test_t04_s01_ac04_impacto_y_riesgo_invalidos(app, u, cambio):
    """AC-S01-04: impacto o riesgo fuera de los valores permitidos se rechazan."""
    assert registrar(u.sol1, **cambio).status_code == 400
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0
    assert n_eventos(app) == 0


@pytest.mark.parametrize("cambio", [
    {"ubicacion": "SALA-9"}, {"categoria": "PINTURA"}, {"ubicacion": ""},
])
def test_t05_s01_ac05_ubicacion_categoria_invalidas(app, u, cambio):
    """AC-S01-05: ubicación/categoría fuera de lista se rechazan."""
    assert registrar(u.sol1, **cambio).status_code == 400
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0


def test_t05b_s01_ac05_campo_faltante(app, u):
    """AC-S01-05: un campo omitido se rechaza."""
    datos = dict(VALIDO)
    del datos["impacto"]
    assert u.sol1.post("/incidencias/nueva", data=datos).status_code == 400
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0


def test_t06_s01_ac06_html_no_se_ejecuta(app, u):
    """AC-S01-06: el texto parecido a HTML se muestra escapado."""
    codigo = crear(u.sol1, descripcion="<script>alert(1)</script> fallo")
    html = u.sol1.get(f"/incidencias/{codigo}").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)" not in html


def test_t07_s01_ac07_sin_efectos_parciales(app, u):
    """AC-S01-07: si falla el evento, no queda incidencia sin evento (rollback)."""
    ejecutar_sql(app, "CREATE TRIGGER fallo BEFORE INSERT ON eventos "
                      "BEGIN SELECT RAISE(ABORT, 'fallo simulado'); END;")
    assert registrar(u.sol1).status_code == 500
    assert una(app, "SELECT COUNT(*) FROM incidencias") == 0
    assert n_eventos(app) == 0


def test_t08_s01_autor_y_estado_vienen_del_servidor(app, u):
    """AC-S01-01: autor, estado y código enviados por el cliente se ignoran."""
    registrar(u.sol1, solicitante_id=str(u.ids["solicitante2"]), estado="CERRADA",
              codigo="INC-9999", prioridad="NORMAL")
    inc = filas(app, "SELECT * FROM incidencias")[0]
    assert (inc["codigo"], inc["estado"], inc["solicitante_id"]) == \
        ("INC-0001", "REGISTRADA", u.ids["solicitante1"])
