import pytest

from app import create_app
from app.db import init_db
from app.seed import seed
from ayudas import T0, Reloj, construir_usuarios


@pytest.fixture
def reloj():
    return Reloj(T0)


@pytest.fixture
def app(tmp_path, reloj):
    """Aplicación con base SQLite temporal e independiente por prueba."""
    aplicacion = create_app({
        "DATABASE": str(tmp_path / "prueba.db"), "TESTING": True,
        "CSRF_ENABLED": False, "CLOCK": reloj,
    })
    with aplicacion.app_context():
        init_db()
        seed()
    return aplicacion


@pytest.fixture
def u(app):
    return construir_usuarios(app)
