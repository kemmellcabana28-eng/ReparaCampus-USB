"""Capa web: lee la sesión, delega en services y devuelve HTML. No contiene reglas de negocio."""
import secrets
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

from . import services
from .db import get_db

bp = Blueprint("web", __name__)


@bp.before_app_request
def cargar_usuario():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:  # identidad y rol salen de la sesión + BD, nunca del cliente
        g.user = get_db().execute(
            "SELECT id, username, nombre, rol FROM usuarios WHERE id=? AND activo=1", (user_id,)
        ).fetchone()
        if g.user is None:
            session.clear()


@bp.before_app_request
def verificar_csrf():
    if request.method == "POST" and current_app.config["CSRF_ENABLED"]:
        esperado = session.get("csrf_token")
        if not esperado or not secrets.compare_digest(esperado, request.form.get("csrf_token", "")):
            abort(400, "Token CSRF inválido")


@bp.app_context_processor
def inyectar():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return {"csrf_token": session["csrf_token"], "usuario": g.get("user"),
            "ESTADOS": services.ESTADOS, "PRIORIDADES": services.PRIORIDADES,
            "UBICACIONES": services.UBICACIONES, "CATEGORIAS": services.CATEGORIAS,
            "IMPACTOS": services.IMPACTOS}


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("web.login"))
        return vista(*args, **kwargs)
    return envoltura


def _ahora():
    return current_app.config["CLOCK"]()


@bp.errorhandler(services.ServicioError)
def servicio_error(e):
    return render_template("error.html", mensaje=e.mensaje), e.status


@bp.errorhandler(400)
def solicitud_invalida(e):
    return render_template("error.html", mensaje=getattr(e, "description", "Solicitud inválida")), 400


# ---------- sesión ----------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        fila = get_db().execute(
            "SELECT * FROM usuarios WHERE username=? AND activo=1",
            (request.form.get("username", "").strip(),)).fetchone()
        if fila and check_password_hash(fila["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = fila["id"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(url_for("web.lista"))
        return render_template("login.html", error="Usuario o contraseña incorrectos"), 401
    return render_template("login.html", error=None)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("web.login"))


@bp.route("/")
def inicio():
    return redirect(url_for("web.lista"))


# ---------- consulta ----------
@bp.route("/incidencias")
@login_requerido
def lista():
    estado = request.args.get("estado", "")
    prioridad = request.args.get("prioridad", "")
    filas = services.listar(get_db(), g.user, estado, prioridad)
    return render_template("lista.html", incidencias=filas, estado=estado, prioridad=prioridad)


@bp.route("/incidencias/<codigo>")
@login_requerido
def ver(codigo):
    datos = services.detalle(get_db(), g.user, codigo)
    return render_template("detalle.html", **datos)


@bp.route("/tablero")
@login_requerido
def tablero():
    return render_template("tablero.html", t=services.tablero(get_db(), g.user))


# ---------- registrar ----------
@bp.route("/incidencias/nueva", methods=["GET", "POST"])
@login_requerido
def nueva():
    if request.method == "POST":
        try:
            codigo = services.crear_incidencia(get_db(), g.user, request.form, _ahora())
        except services.ValidacionError as e:
            return render_template("nueva.html", error=e.mensaje, v=request.form), 400
        flash(f"Incidencia {codigo} registrada")
        return redirect(url_for("web.ver", codigo=codigo))
    if g.user["rol"] != "SOLICITANTE":
        raise services.PermisoError("Solo el solicitante registra incidencias")
    return render_template("nueva.html", error=None, v={})


# ---------- transiciones ----------
def _accion(nombre, funcion, mensaje, campo=None):
    @bp.route(f"/incidencias/<codigo>/{nombre}", methods=["POST"], endpoint=nombre)
    @login_requerido
    def vista(codigo):
        args = [get_db(), g.user, codigo]
        if campo:
            args.append(request.form.get(campo))
        funcion(*args, _ahora())
        flash(mensaje)
        return redirect(url_for("web.ver", codigo=codigo))
    return vista


_accion("asignar", services.asignar, "Incidencia asignada", "tecnico_id")
_accion("iniciar", services.iniciar_atencion, "Atención iniciada")
_accion("solucion", services.registrar_solucion, "Solución registrada", "solucion")
_accion("confirmar", services.confirmar, "Incidencia cerrada")
_accion("rechazar", services.rechazar, "Solución rechazada", "motivo")
_accion("reabrir", services.reabrir, "Incidencia reabierta", "motivo")
