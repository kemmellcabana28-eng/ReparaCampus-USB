import sqlite3

import pytest

from app.services import formatear_porcentaje
from ayudas import (MOTIVO_OK, accion, crear, en_estado, estado_de, filas, n_eventos, una)


def preparar_tres(app, u):
    """INC-0001 CRITICA/ASIGNADA (sol1, tec1); INC-0002 ALTA/REGISTRADA (sol1); INC-0003 NORMAL/REGISTRADA (sol2)."""
    a = crear(u.sol1, riesgo_personas="true", impacto="ALTO")
    b = crear(u.sol1, riesgo_personas="false", impacto="ALTO")
    c = crear(u.sol2, riesgo_personas="false", impacto="BAJO")
    accion(u.coord, a, "asignar", tecnico_id=u.ids["tecnico1"])
    return a, b, c


def test_t33_s05_ac01_coordinador_lista_y_filtra(app, u):
    """AC-S05-01: el coordinador ve todo y los filtros se combinan."""
    a, b, c = preparar_tres(app, u)
    todo = u.coord.get("/incidencias").get_data(as_text=True)
    assert all(codigo in todo for codigo in ("INC-0001", "INC-0002", "INC-0003"))
    solo_a = u.coord.get("/incidencias?estado=ASIGNADA&prioridad=CRITICA").get_data(as_text=True)
    assert "INC-0001" in solo_a and "INC-0002" not in solo_a and "INC-0003" not in solo_a
    registradas = u.coord.get("/incidencias?estado=REGISTRADA").get_data(as_text=True)
    assert "INC-0001" not in registradas and "INC-0002" in registradas and "INC-0003" in registradas
    altas = u.coord.get("/incidencias?prioridad=ALTA").get_data(as_text=True)
    assert "INC-0002" in altas and "INC-0001" not in altas and "INC-0003" not in altas


def test_t34_s05_ac02_solicitante_solo_las_suyas(app, u):
    """AC-S05-02: el solicitante solo ve las propias; una ajena responde 404."""
    preparar_tres(app, u)
    html = u.sol1.get("/incidencias").get_data(as_text=True)
    assert "INC-0001" in html and "INC-0002" in html and "INC-0003" not in html
    assert u.sol1.get("/incidencias/INC-0003").status_code == 404
    assert u.sol2.get("/incidencias/INC-0001").status_code == 404
    assert u.sol1.get("/incidencias/INC-0001").status_code == 200


def test_t35_s05_ac03_tecnico_solo_asignadas(app, u):
    """AC-S05-03: el técnico solo ve las asignadas a él."""
    preparar_tres(app, u)
    html = u.tec1.get("/incidencias").get_data(as_text=True)
    assert "INC-0001" in html and "INC-0002" not in html and "INC-0003" not in html
    assert "INC-0001" not in u.tec2.get("/incidencias").get_data(as_text=True)
    assert u.tec2.get("/incidencias/INC-0001").status_code == 404


def test_t36_s05_ac04_historial_completo(app, u):
    """AC-S05-04: el historial lista cada acción en orden con autor, estados y detalle."""
    codigo = en_estado(u, "PENDIENTE_VALIDACION")
    accion(u.sol1, codigo, "rechazar", motivo=MOTIVO_OK)
    ev = filas(app, "SELECT accion, estado_anterior, estado_nuevo, autor_id FROM eventos ORDER BY id")
    esperado = [
        ("CREACION", None, "REGISTRADA", u.ids["solicitante1"]),
        ("ASIGNACION", "REGISTRADA", "ASIGNADA", u.ids["coordinador1"]),
        ("INICIO_ATENCION", "ASIGNADA", "EN_ATENCION", u.ids["tecnico1"]),
        ("SOLUCION", "EN_ATENCION", "PENDIENTE_VALIDACION", u.ids["tecnico1"]),
        ("RECHAZO", "PENDIENTE_VALIDACION", "EN_ATENCION", u.ids["solicitante1"]),
    ]
    assert [tuple(e) for e in ev] == esperado
    html = u.coord.get(f"/incidencias/{codigo}").get_data(as_text=True)
    for texto in ("CREACION", "ASIGNACION", "INICIO_ATENCION", "SOLUCION", "RECHAZO", MOTIVO_OK):
        assert texto in html


def test_t37_s05_ac05_historial_inmutable(app, u):
    """AC-S05-05: ni UPDATE ni DELETE sobre eventos, ni con SQL directo."""
    crear(u.sol1)
    con = sqlite3.connect(app.config["DATABASE"])
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("UPDATE eventos SET accion='CIERRE'")
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("DELETE FROM eventos")
    con.close()
    assert una(app, "SELECT accion FROM eventos") == "CREACION"
    assert n_eventos(app) == 1


def test_t38_s05_ac06_tablero_vacio(app, u):
    """AC-S05-06: sin incidencias el porcentaje es 0,0 %."""
    html = u.coord.get("/tablero").get_data(as_text=True)
    assert "0,0 %" in html and "de 0)" in html


def test_t39_s05_ac07_tablero_25_y_reapertura(app, u, reloj):
    """AC-S05-07: 1 de 4 cerrada = 25,0 %; reabrirla baja a 0,0 % y conserva el cierre."""
    cerrada = en_estado(u, "CERRADA")
    crear(u.sol1)
    crear(u.sol1, riesgo_personas="true")
    crear(u.sol2)
    html = u.coord.get("/tablero").get_data(as_text=True)
    assert "25,0 %" in html and "1 cerradas de 4" in html
    assert "INC-0003" in html  # CRITICA sin cerrar
    reloj.avanzar(hours=1)
    assert accion(u.sol1, cerrada, "reabrir", motivo=MOTIVO_OK).status_code == 302
    assert "0,0 %" in u.coord.get("/tablero").get_data(as_text=True)
    assert una(app, "SELECT COUNT(*) FROM cierres") == 1


@pytest.mark.parametrize("quien", ["sol1", "tec1"])
def test_t40_s05_ac08_tablero_solo_coordinador(app, u, quien):
    """AC-S05-08: solicitante y técnico reciben 403 en el tablero."""
    assert getattr(u, quien).get("/tablero").status_code == 403


@pytest.mark.parametrize("consulta", ["estado=INVENTADO", "prioridad=URGENTE"])
def test_t41_s05_ac09_filtro_invalido(app, u, consulta):
    """AC-S05-09: un filtro con valor inválido se rechaza."""
    assert u.coord.get(f"/incidencias?{consulta}").status_code == 400


@pytest.mark.parametrize("cerradas,total,esperado", [
    (0, 0, "0,0 %"), (1, 4, "25,0 %"), (1, 3, "33,3 %"), (2, 3, "66,7 %"),
    (1, 16, "6,3 %"), (4, 4, "100,0 %"),
])
def test_t42_s05_porcentaje_con_un_decimal(cerradas, total, esperado):
    """AC-S05-06/07: formato con coma, un decimal y redondeo half-up."""
    assert formatear_porcentaje(cerradas, total) == esperado
