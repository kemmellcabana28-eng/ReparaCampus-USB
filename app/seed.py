"""Seed ficticio: dos solicitantes, un coordinador y dos técnicos activos."""
from werkzeug.security import generate_password_hash

from .db import get_db

CLAVE_DEMO = "Reparacampus#2026"  # contraseña ficticia solo para el prototipo

CUENTAS = [
    ("solicitante1", "Sara Solicitante", "SOLICITANTE"),
    ("solicitante2", "Samuel Solicitante", "SOLICITANTE"),
    ("coordinador1", "Carla Coordinadora", "COORDINADOR"),
    ("tecnico1", "Tomás Técnico", "TECNICO"),
    ("tecnico2", "Teresa Técnica", "TECNICO"),
]


def seed():
    db = get_db()
    for username, nombre, rol in CUENTAS:
        existe = db.execute("SELECT 1 FROM usuarios WHERE username=?", (username,)).fetchone()
        if not existe:
            db.execute(
                "INSERT INTO usuarios (username, nombre, rol, password_hash, activo) "
                "VALUES (?,?,?,?,1)",
                (username, nombre, rol, generate_password_hash(CLAVE_DEMO)),
            )
