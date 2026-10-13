import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, render_template

from . import db, routes
from .seed import seed as cargar_seed


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "clave-solo-para-demo-cambiar"),
        DATABASE=os.path.join(app.instance_path, "reparacampus.db"),
        CLOCK=lambda: datetime.now(timezone.utc),  # reloj inyectable (pruebas)
        CSRF_ENABLED=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(routes.bp)

    @app.errorhandler(sqlite3.Error)
    def error_bd(_e):
        return render_template("error.html", mensaje="Error interno: la operación no se aplicó."), 500

    @app.cli.command("init-db")
    def init_db_command():
        """Crea el esquema y las cuentas ficticias."""
        db.init_db()
        cargar_seed()
        print("Base de datos lista con cuentas ficticias.")

    return app
