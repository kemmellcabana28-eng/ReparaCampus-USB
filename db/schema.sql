-- Esquema ReparaCampus (SQLite). Estado e historial se guardan en la misma transacción.
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    nombre        TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('SOLICITANTE','COORDINADOR','TECNICO')),
    password_hash TEXT NOT NULL,
    activo        INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS incidencias (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT NOT NULL UNIQUE,
    ubicacion       TEXT NOT NULL CHECK (ubicacion IN ('LAB-01','AULA-201','BIB-01')),
    categoria       TEXT NOT NULL CHECK (categoria IN ('ELECTRICIDAD','HIDRAULICA','MOBILIARIO','TIC')),
    descripcion     TEXT NOT NULL,
    impacto         TEXT NOT NULL CHECK (impacto IN ('BAJO','ALTO')),
    riesgo_personas INTEGER NOT NULL CHECK (riesgo_personas IN (0,1)),
    prioridad       TEXT NOT NULL CHECK (prioridad IN ('CRITICA','ALTA','NORMAL')),
    estado          TEXT NOT NULL CHECK (estado IN
        ('REGISTRADA','ASIGNADA','EN_ATENCION','PENDIENTE_VALIDACION','CERRADA')),
    solicitante_id  INTEGER NOT NULL REFERENCES usuarios(id),
    tecnico_id      INTEGER REFERENCES usuarios(id),
    creada_en       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS asignaciones (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id  INTEGER NOT NULL REFERENCES incidencias(id),
    coordinador_id INTEGER NOT NULL REFERENCES usuarios(id),
    tecnico_id     INTEGER NOT NULL REFERENCES usuarios(id),
    fecha          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS soluciones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id INTEGER NOT NULL REFERENCES incidencias(id),
    tecnico_id    INTEGER NOT NULL REFERENCES usuarios(id),
    texto         TEXT NOT NULL,
    fecha         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cierres (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id  INTEGER NOT NULL REFERENCES incidencias(id),
    solicitante_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incidencia_id   INTEGER NOT NULL REFERENCES incidencias(id),
    autor_id        INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TEXT NOT NULL,
    estado_anterior TEXT,
    estado_nuevo    TEXT NOT NULL,
    accion          TEXT NOT NULL CHECK (accion IN
        ('CREACION','ASIGNACION','INICIO_ATENCION','SOLUCION','CIERRE','RECHAZO','REAPERTURA')),
    detalle         TEXT
);

-- El historial no se edita ni se borra (ni siquiera con SQL directo).
CREATE TRIGGER IF NOT EXISTS eventos_no_update BEFORE UPDATE ON eventos
BEGIN SELECT RAISE(ABORT, 'El historial no se puede editar'); END;
CREATE TRIGGER IF NOT EXISTS eventos_no_delete BEFORE DELETE ON eventos
BEGIN SELECT RAISE(ABORT, 'El historial no se puede borrar'); END;

CREATE INDEX IF NOT EXISTS idx_inc_estado ON incidencias(estado);
CREATE INDEX IF NOT EXISTS idx_inc_prioridad ON incidencias(prioridad);
CREATE INDEX IF NOT EXISTS idx_eventos_inc ON eventos(incidencia_id);
