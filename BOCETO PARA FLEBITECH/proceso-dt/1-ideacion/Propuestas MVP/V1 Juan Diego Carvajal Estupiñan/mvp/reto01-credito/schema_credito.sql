-- Reto 01 — Esquema de datos mínimo (Crédito Hiperpersonalizado)
-- Hackathon Colsubsidio 2026 · Scala Labs
-- SQLite/Postgres compatible. Es el mínimo para el MVP: perfil -> oferta -> evento de canal.

CREATE TABLE afiliado (
    id                TEXT PRIMARY KEY,
    nombre            TEXT NOT NULL,
    categoria         TEXT CHECK (categoria IN ('A','B','C')) NOT NULL,
    ingreso_mensual   INTEGER NOT NULL,
    edad              INTEGER,
    antiguedad_meses  INTEGER DEFAULT 0,
    productos_activos INTEGER DEFAULT 0,
    mora_ultimos_12m  INTEGER DEFAULT 0,
    canal_preferido   TEXT,           -- WhatsApp | App Colsubsidio | Email | Oficina
    interes_declarado TEXT,           -- vivienda | educacion | vehiculo | libre
    consentimiento_datos BOOLEAN DEFAULT 0,  -- Habeas Data: sin esto no se personaliza
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE oferta (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    afiliado_id       TEXT REFERENCES afiliado(id),
    segmento          TEXT,           -- Consolidado | Crecimiento | Nuevo por activar | Reconstrucción
    score             INTEGER,        -- 0-100
    producto          TEXT,
    monto             INTEGER,
    tasa_mensual      REAL,
    plazo_meses       INTEGER,
    cuota_estimada    INTEGER,
    canal_recomendado TEXT,
    justificacion     TEXT,           -- JSON con las razones (transparencia)
    mensaje_generado  TEXT,           -- copy del agente Gemini por canal
    estado            TEXT DEFAULT 'generada', -- generada | enviada | vista | aceptada | rechazada
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evento_interaccion (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    oferta_id    INTEGER REFERENCES oferta(id),
    canal        TEXT,
    tipo         TEXT,               -- enviado | abierto | click | acepta | rechaza
    ocurrido_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_oferta_afiliado ON oferta(afiliado_id);
CREATE INDEX idx_evento_oferta   ON evento_interaccion(oferta_id);
