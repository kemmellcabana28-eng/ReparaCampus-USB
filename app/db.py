"""Acceso a SQLite. Las transacciones se manejan manualmente (isolation_level=None)."""
import os
import sqlite3

from flask import current_app, g

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], isolation_level=None)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    with open(SCHEMA, encoding="utf-8") as archivo:
        get_db().executescript(archivo.read())


def init_app(app):
    app.teardown_appcontext(close_db)
