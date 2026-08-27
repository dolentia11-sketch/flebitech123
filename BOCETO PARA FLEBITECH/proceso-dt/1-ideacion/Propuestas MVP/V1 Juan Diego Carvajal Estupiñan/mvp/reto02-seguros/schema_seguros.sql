-- Reto 02 — Esquema de datos mínimo (Venta Automatizada de Seguros)
-- Hackathon Colsubsidio 2026 · Scala Labs
-- SQLite/Postgres compatible. Catálogo -> conversación -> cotización -> póliza.

CREATE TABLE producto_seguro (
    key            TEXT PRIMARY KEY,     -- vida | accidentes | exequial | hogar | desempleo
    nombre         TEXT NOT NULL,
    ramo           TEXT,
    prima_base     INTEGER NOT NULL,     -- mensual
    cobertura_base INTEGER NOT NULL,
    atiende        TEXT                  -- necesidad que resuelve, en lenguaje simple
);

CREATE TABLE conversacion (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    afiliado_id   TEXT,
    canal         TEXT,                  -- web | WhatsApp | app
    respuestas    TEXT,                  -- JSON con edad, dependientes, vivienda, ingreso, preocupacion
    necesidad_detectada TEXT,
    iniciada_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cotizacion (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    conversacion_id INTEGER REFERENCES conversacion(id),
    producto_key  TEXT REFERENCES producto_seguro(key),
    cobertura     INTEGER,
    prima_mensual INTEGER,
    idoneidad     TEXT,                  -- por qué este producto encaja (venta adecuada)
    estado        TEXT DEFAULT 'cotizada', -- cotizada | aceptada | emitida | descartada
    creado_en     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE poliza (
    numero        TEXT PRIMARY KEY,      -- POL-XXXXXX
    cotizacion_id INTEGER REFERENCES cotizacion(id),
    afiliado_id   TEXT,
    consentimiento BOOLEAN DEFAULT 0,    -- sin esto no se emite
    emitida_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vigencia      TEXT DEFAULT '12 meses renovable'
);

CREATE INDEX idx_cotizacion_conv ON cotizacion(conversacion_id);
CREATE INDEX idx_poliza_afiliado  ON poliza(afiliado_id);
