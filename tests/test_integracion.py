"""Integración: recorridos completos por HTTP contra un archivo SQLite real."""
import pytest

from ayudas import (MOTIVO_OK, SOLUCION_OK, accion, crear, filas, una)

pytestmark = pytest.mark.integracion


def acciones(app):
    return [(e["accion"], e["estado_anterior"], e["estado_nuevo"])
            for e in filas(app, "SELECT * FROM eventos ORDER BY id")]


def test_t49_integracion_flujo_de_cierre(app, u):
    """AC-S04-01: Registrar → asignar → iniciar → proponer → confirmar."""
    codigo = crear(u.sol1, riesgo_personas="true")
    assert accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"]).status_code == 302
    assert accion(u.tec1, codigo, "iniciar").status_code == 302
    assert accion(u.tec1, codigo, "solucion", solucion=SOLUCION_OK).status_code == 302
    assert accion(u.sol1, codigo, "confirmar").status_code == 302
    inc = filas(app, "SELECT * FROM incidencias")[0]
    assert (inc["estado"], inc["prioridad"], inc["tecnico_id"]) == \
        ("CERRADA", "CRITICA", u.ids["tecnico1"])
    assert acciones(app) == [
        ("CREACION", None, "REGISTRADA"),
        ("ASIGNACION", "REGISTRADA", "ASIGNADA"),
        ("INICIO_ATENCION", "ASIGNADA", "EN_ATENCION"),
        ("SOLUCION", "EN_ATENCION", "PENDIENTE_VALIDACION"),
        ("CIERRE", "PENDIENTE_VALIDACION", "CERRADA"),
    ]
    assert una(app, "SELECT COUNT(*) FROM cierres") == 1


def test_t50_integracion_flujo_con_rechazo(app, u):
    """AC-S04-03: proponer → rechazar → nueva solución → confirmar (conserva ambas soluciones)."""
    codigo = crear(u.sol1)
    accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico2"])
    accion(u.tec2, codigo, "iniciar")
    accion(u.tec2, codigo, "solucion", solucion=SOLUCION_OK)
    assert accion(u.sol1, codigo, "rechazar", motivo=MOTIVO_OK).status_code == 302
    segunda = "Segunda solución: se cambió el cable y se midió la tensión."
    assert accion(u.tec2, codigo, "solucion", solucion=segunda).status_code == 302
    assert accion(u.sol1, codigo, "confirmar").status_code == 302
    assert [s["texto"] for s in filas(app, "SELECT texto FROM soluciones ORDER BY id")] == \
        [SOLUCION_OK, segunda]
    assert una(app, "SELECT tecnico_id FROM incidencias") == u.ids["tecnico2"]
    assert [a[0] for a in acciones(app)] == [
        "CREACION", "ASIGNACION", "INICIO_ATENCION", "SOLUCION", "RECHAZO", "SOLUCION", "CIERRE"]
    assert una(app, "SELECT estado FROM incidencias") == "CERRADA"


def test_t51_integracion_cierre_reapertura_nuevo_cierre(app, u, reloj):
    """AC-S04-07: Cierre → reapertura → nueva solución → nuevo cierre (todo se conserva)."""
    codigo = crear(u.sol1)
    accion(u.coord, codigo, "asignar", tecnico_id=u.ids["tecnico1"])
    accion(u.tec1, codigo, "iniciar")
    accion(u.tec1, codigo, "solucion", solucion=SOLUCION_OK)
    accion(u.sol1, codigo, "confirmar")
    reloj.avanzar(hours=24)
    assert accion(u.sol1, codigo, "reabrir", motivo="Volvió a fallar el tomacorriente").status_code == 302
    nueva = "Se instaló un interruptor diferencial nuevo y se probó."
    assert accion(u.tec1, codigo, "solucion", solucion=nueva).status_code == 302
    reloj.avanzar(hours=2)
    assert accion(u.sol1, codigo, "confirmar").status_code == 302
    assert una(app, "SELECT COUNT(*) FROM cierres") == 2
    assert una(app, "SELECT COUNT(*) FROM soluciones") == 2
    assert una(app, "SELECT tecnico_id FROM incidencias") == u.ids["tecnico1"]
    assert [a[0] for a in acciones(app)] == [
        "CREACION", "ASIGNACION", "INICIO_ATENCION", "SOLUCION", "CIERRE",
        "REAPERTURA", "SOLUCION", "CIERRE"]
    assert una(app, "SELECT estado FROM incidencias") == "CERRADA"
