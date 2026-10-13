"""Lógica de negocio. TODAS las reglas, permisos y validaciones viven aquí (servidor)."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

UBICACIONES = ("LAB-01", "AULA-201", "BIB-01")
CATEGORIAS = ("ELECTRICIDAD", "HIDRAULICA", "MOBILIARIO", "TIC")
IMPACTOS = ("BAJO", "ALTO")
ESTADOS = ("REGISTRADA", "ASIGNADA", "EN_ATENCION", "PENDIENTE_VALIDACION", "CERRADA")
PRIORIDADES = ("CRITICA", "ALTA", "NORMAL")
PLAZO_REAPERTURA = timedelta(hours=48)


class ServicioError(Exception):
    status = 400

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje


class ValidacionError(ServicioError):
    status = 400


class PermisoError(ServicioError):
    status = 403


class NoEncontradoError(ServicioError):
    status = 404


class EstadoError(ServicioError):
    status = 409


@contextmanager
def transaccion(db):
    """Todo o nada: estado, solución, cierre y evento se guardan juntos."""
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
    except BaseException:
        db.execute("ROLLBACK")
        raise
    else:
        db.execute("COMMIT")


# ---------- utilidades ----------
def _iso(momento):
    return momento.astimezone(timezone.utc).isoformat()


def _exigir_rol(usuario, rol):
    if usuario is None or usuario["rol"] != rol:
        raise PermisoError(f"Solo el rol {rol} puede realizar esta operación")


def _texto(valor, minimo, maximo, campo):
    if not isinstance(valor, str):
        raise ValidacionError(f"{campo} es obligatorio")
    limpio = valor.strip()
    if not minimo <= len(limpio) <= maximo:
        raise ValidacionError(f"{campo} debe tener entre {minimo} y {maximo} caracteres")
    return limpio


def _opcion(valor, permitidos, campo):
    if not isinstance(valor, str) or valor.strip() not in permitidos:
        raise ValidacionError(f"{campo} inválido. Valores permitidos: {', '.join(permitidos)}")
    return valor.strip()


def _booleano(valor, campo):
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str) and valor.strip().lower() in ("true", "false"):
        return valor.strip().lower() == "true"
    raise ValidacionError(f"{campo} debe ser true o false")


def calcular_prioridad(riesgo, impacto):
    if riesgo:
        return "CRITICA"
    return "ALTA" if impacto == "ALTO" else "NORMAL"


def _evento(db, incidencia_id, autor_id, ahora, anterior, nuevo, accion, detalle=None):
    db.execute(
        "INSERT INTO eventos (incidencia_id, autor_id, fecha, estado_anterior, estado_nuevo, "
        "accion, detalle) VALUES (?,?,?,?,?,?,?)",
        (incidencia_id, autor_id, _iso(ahora), anterior, nuevo, accion, detalle),
    )


def _cargar(db, codigo):
    inc = db.execute("SELECT * FROM incidencias WHERE codigo=?", (codigo,)).fetchone()
    if inc is None:
        raise NoEncontradoError("La incidencia no existe")
    return inc


def _cambiar_estado(db, inc, esperado, nuevo):
    """UPDATE condicionado al estado esperado: evita transiciones concurrentes."""
    cur = db.execute(
        "UPDATE incidencias SET estado=? WHERE id=? AND estado=?", (nuevo, inc["id"], esperado)
    )
    if cur.rowcount != 1:
        raise EstadoError("El estado de la incidencia cambió; operación rechazada")


# ---------- S01 / S02: registrar, priorizar, asignar ----------
def crear_incidencia(db, usuario, datos, ahora):
    _exigir_rol(usuario, "SOLICITANTE")
    ubicacion = _opcion(datos.get("ubicacion"), UBICACIONES, "La ubicación")
    categoria = _opcion(datos.get("categoria"), CATEGORIAS, "La categoría")
    descripcion = _texto(datos.get("descripcion"), 20, 500, "La descripción")
    impacto = _opcion(datos.get("impacto"), IMPACTOS, "El impacto")
    riesgo = _booleano(datos.get("riesgo_personas"), "El riesgo para personas")
    prioridad = calcular_prioridad(riesgo, impacto)  # nunca se toma del cliente
    with transaccion(db):
        siguiente = db.execute("SELECT COALESCE(MAX(id),0)+1 FROM incidencias").fetchone()[0]
        codigo = f"INC-{siguiente:04d}"
        cur = db.execute(
            "INSERT INTO incidencias (codigo, ubicacion, categoria, descripcion, impacto, "
            "riesgo_personas, prioridad, estado, solicitante_id, creada_en) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (codigo, ubicacion, categoria, descripcion, impacto, int(riesgo), prioridad,
             "REGISTRADA", usuario["id"], _iso(ahora)),
        )
        _evento(db, cur.lastrowid, usuario["id"], ahora, None, "REGISTRADA", "CREACION")
    return codigo


def asignar(db, usuario, codigo, tecnico_id, ahora):
    _exigir_rol(usuario, "COORDINADOR")
    with transaccion(db):
        inc = _cargar(db, codigo)
        if inc["estado"] != "REGISTRADA":
            raise EstadoError("Solo se puede asignar una incidencia REGISTRADA")
        try:
            tecnico_id = int(tecnico_id)
        except (TypeError, ValueError):
            raise ValidacionError("Técnico inválido")
        tecnico = db.execute(
            "SELECT id FROM usuarios WHERE id=? AND rol='TECNICO' AND activo=1", (tecnico_id,)
        ).fetchone()
        if tecnico is None:
            raise ValidacionError("El técnico no existe, no es técnico o no está activo")
        _cambiar_estado(db, inc, "REGISTRADA", "ASIGNADA")
        db.execute("UPDATE incidencias SET tecnico_id=? WHERE id=?", (tecnico_id, inc["id"]))
        db.execute(
            "INSERT INTO asignaciones (incidencia_id, coordinador_id, tecnico_id, fecha) "
            "VALUES (?,?,?,?)", (inc["id"], usuario["id"], tecnico_id, _iso(ahora)))
        _evento(db, inc["id"], usuario["id"], ahora, "REGISTRADA", "ASIGNADA", "ASIGNACION",
                f"técnico id={tecnico_id}")


# ---------- S03: atender ----------
def _cargar_para_tecnico(db, usuario, codigo):
    _exigir_rol(usuario, "TECNICO")
    inc = _cargar(db, codigo)
    if inc["tecnico_id"] != usuario["id"]:
        raise PermisoError("La incidencia no está asignada a este técnico")
    return inc


def iniciar_atencion(db, usuario, codigo, ahora):
    _exigir_rol(usuario, "TECNICO")
    with transaccion(db):
        inc = _cargar_para_tecnico(db, usuario, codigo)
        if inc["estado"] != "ASIGNADA":
            raise EstadoError("Solo se inicia la atención de una incidencia ASIGNADA")
        _cambiar_estado(db, inc, "ASIGNADA", "EN_ATENCION")
        _evento(db, inc["id"], usuario["id"], ahora, "ASIGNADA", "EN_ATENCION", "INICIO_ATENCION")


def registrar_solucion(db, usuario, codigo, texto, ahora):
    _exigir_rol(usuario, "TECNICO")
    with transaccion(db):
        inc = _cargar_para_tecnico(db, usuario, codigo)
        if inc["estado"] != "EN_ATENCION":
            raise EstadoError("La solución solo se registra con la incidencia EN_ATENCION")
        solucion = _texto(texto, 20, 800, "La solución")
        _cambiar_estado(db, inc, "EN_ATENCION", "PENDIENTE_VALIDACION")
        db.execute(
            "INSERT INTO soluciones (incidencia_id, tecnico_id, texto, fecha) VALUES (?,?,?,?)",
            (inc["id"], usuario["id"], solucion, _iso(ahora)))
        _evento(db, inc["id"], usuario["id"], ahora, "EN_ATENCION", "PENDIENTE_VALIDACION",
                "SOLUCION", solucion)


# ---------- S04: validar ----------
def _cargar_para_dueno(db, usuario, codigo):
    _exigir_rol(usuario, "SOLICITANTE")
    inc = _cargar(db, codigo)
    if inc["solicitante_id"] != usuario["id"]:
        raise PermisoError("Solo el solicitante dueño puede validar esta incidencia")
    return inc


def confirmar(db, usuario, codigo, ahora):
    _exigir_rol(usuario, "SOLICITANTE")
    with transaccion(db):
        inc = _cargar_para_dueno(db, usuario, codigo)
        if inc["estado"] != "PENDIENTE_VALIDACION":
            raise EstadoError("Solo se confirma una solución PENDIENTE_VALIDACION")
        _cambiar_estado(db, inc, "PENDIENTE_VALIDACION", "CERRADA")
        db.execute("INSERT INTO cierres (incidencia_id, solicitante_id, fecha) VALUES (?,?,?)",
                   (inc["id"], usuario["id"], _iso(ahora)))
        _evento(db, inc["id"], usuario["id"], ahora, "PENDIENTE_VALIDACION", "CERRADA", "CIERRE")


def rechazar(db, usuario, codigo, motivo, ahora):
    _exigir_rol(usuario, "SOLICITANTE")
    with transaccion(db):
        inc = _cargar_para_dueno(db, usuario, codigo)
        if inc["estado"] != "PENDIENTE_VALIDACION":
            raise EstadoError("Solo se rechaza una solución PENDIENTE_VALIDACION")
        motivo = _texto(motivo, 10, 300, "El motivo")
        _cambiar_estado(db, inc, "PENDIENTE_VALIDACION", "EN_ATENCION")
        _evento(db, inc["id"], usuario["id"], ahora, "PENDIENTE_VALIDACION", "EN_ATENCION",
                "RECHAZO", motivo)


def reabrir(db, usuario, codigo, motivo, ahora):
    _exigir_rol(usuario, "SOLICITANTE")
    with transaccion(db):
        inc = _cargar_para_dueno(db, usuario, codigo)
        if inc["estado"] != "CERRADA":
            raise EstadoError("Solo se reabre una incidencia CERRADA")
        motivo = _texto(motivo, 10, 300, "El motivo")
        ultimo = db.execute(
            "SELECT fecha FROM cierres WHERE incidencia_id=? ORDER BY id DESC LIMIT 1",
            (inc["id"],)).fetchone()
        transcurrido = ahora - datetime.fromisoformat(ultimo["fecha"])
        if transcurrido > PLAZO_REAPERTURA:  # <= 48 h se acepta
            raise EstadoError("Fuera del plazo de 48 horas desde el último cierre")
        _cambiar_estado(db, inc, "CERRADA", "EN_ATENCION")
        _evento(db, inc["id"], usuario["id"], ahora, "CERRADA", "EN_ATENCION", "REAPERTURA", motivo)


# ---------- S05: consultar, historizar, tablero ----------
def _alcance(usuario):
    if usuario["rol"] == "SOLICITANTE":
        return " AND i.solicitante_id = ?", [usuario["id"]]
    if usuario["rol"] == "TECNICO":
        return " AND i.tecnico_id = ?", [usuario["id"]]
    return "", []


def listar(db, usuario, estado=None, prioridad=None):
    estado = (estado or "").strip() or None
    prioridad = (prioridad or "").strip() or None
    if estado is not None and estado not in ESTADOS:
        raise ValidacionError("Filtro de estado inválido")
    if prioridad is not None and prioridad not in PRIORIDADES:
        raise ValidacionError("Filtro de prioridad inválido")
    sql = ("SELECT i.*, u.nombre AS solicitante FROM incidencias i "
           "JOIN usuarios u ON u.id = i.solicitante_id WHERE 1=1")
    extra, params = _alcance(usuario)
    sql += extra
    if estado:
        sql += " AND i.estado = ?"
        params.append(estado)
    if prioridad:
        sql += " AND i.prioridad = ?"
        params.append(prioridad)
    return db.execute(sql + " ORDER BY i.id DESC", params).fetchall()


def detalle(db, usuario, codigo):
    extra, params = _alcance(usuario)
    inc = db.execute(
        "SELECT i.*, u.nombre AS solicitante, t.nombre AS tecnico FROM incidencias i "
        "JOIN usuarios u ON u.id = i.solicitante_id "
        "LEFT JOIN usuarios t ON t.id = i.tecnico_id WHERE i.codigo = ?" + extra,
        [codigo] + params).fetchone()
    if inc is None:  # inexistente o ajena: misma respuesta (404)
        raise NoEncontradoError("La incidencia no existe")
    eventos = db.execute(
        "SELECT e.*, u.nombre AS autor FROM eventos e JOIN usuarios u ON u.id = e.autor_id "
        "WHERE e.incidencia_id=? ORDER BY e.id", (inc["id"],)).fetchall()
    soluciones = db.execute(
        "SELECT * FROM soluciones WHERE incidencia_id=? ORDER BY id", (inc["id"],)).fetchall()
    cierres = db.execute(
        "SELECT * FROM cierres WHERE incidencia_id=? ORDER BY id", (inc["id"],)).fetchall()
    tecnicos = []
    if usuario["rol"] == "COORDINADOR" and inc["estado"] == "REGISTRADA":
        tecnicos = db.execute(
            "SELECT id, nombre FROM usuarios WHERE rol='TECNICO' AND activo=1 ORDER BY nombre"
        ).fetchall()
    return {"incidencia": inc, "eventos": eventos, "soluciones": soluciones,
            "cierres": cierres, "tecnicos": tecnicos}


def formatear_porcentaje(cerradas, total):
    if total == 0:
        return "0,0 %"
    valor = (Decimal(cerradas) * 100 / Decimal(total)).quantize(Decimal("0.1"), ROUND_HALF_UP)
    return f"{valor}".replace(".", ",") + " %"


def tablero(db, usuario):
    _exigir_rol(usuario, "COORDINADOR")
    por_estado = {e: 0 for e in ESTADOS}
    por_prioridad = {p: 0 for p in PRIORIDADES}
    for fila in db.execute("SELECT estado, COUNT(*) n FROM incidencias GROUP BY estado"):
        por_estado[fila["estado"]] = fila["n"]
    for fila in db.execute("SELECT prioridad, COUNT(*) n FROM incidencias GROUP BY prioridad"):
        por_prioridad[fila["prioridad"]] = fila["n"]
    total = sum(por_estado.values())
    criticas = db.execute(
        "SELECT codigo, estado, ubicacion FROM incidencias "
        "WHERE prioridad='CRITICA' AND estado <> 'CERRADA' ORDER BY id").fetchall()
    return {"por_estado": por_estado, "por_prioridad": por_prioridad, "total": total,
            "criticas_abiertas": criticas,
            "porcentaje_cierre": formatear_porcentaje(por_estado["CERRADA"], total)}
