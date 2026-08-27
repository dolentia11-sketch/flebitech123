-- DB de trazabilidad — DDL v1 (esquema-trazabilidad.md)
-- Uso: sqlite3 interactions.db < schema.sql

CREATE TABLE IF NOT EXISTS sessions (
  session_id       TEXT PRIMARY KEY,
  started_at       TEXT NOT NULL,
  ended_at         TEXT,
  canal            TEXT NOT NULL DEFAULT 'web',      -- web | whatsapp (visión)
  origen           TEXT DEFAULT 'directo',           -- campaña | qr | referido | directo
  afiliado         INTEGER NOT NULL DEFAULT 0,       -- 0/1
  id_hash          TEXT,                             -- SHA-256 de la cédula, NUNCA en claro
  consent_datos    INTEGER NOT NULL DEFAULT 0,
  consent_compra   INTEGER NOT NULL DEFAULT 0,
  estado_final     TEXT DEFAULT 'activa',            -- cerrada | abandonada | handoff_asesor | activa
  producto_cerrado TEXT,
  paso_abandono    TEXT,
  aseguradora_id   TEXT                              -- discovery 25-jul: en prod el cierre es remitir a la aseguradora
);

CREATE TABLE IF NOT EXISTS events (
  event_id               INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id             TEXT NOT NULL REFERENCES sessions(session_id),
  ts                     TEXT NOT NULL,
  tipo                   TEXT NOT NULL,  -- pregunta | respuesta | consulta_crm | recomendacion | consentimiento | ajuste | cierre | handoff | abandono | respaldo
  actor                  TEXT NOT NULL,  -- usuario | llm | motor | make
  contenido_raw          TEXT,           -- texto original tal cual
  contenido_estructurado TEXT            -- JSON: la lectura del sistema
);

CREATE TABLE IF NOT EXISTS features (
  session_id TEXT NOT NULL REFERENCES sessions(session_id),
  variable   TEXT NOT NULL,              -- V1..V11
  valor      TEXT,
  fuente     TEXT NOT NULL,              -- pregunta | precarga_crm | inferencia
  ts         TEXT NOT NULL,
  PRIMARY KEY (session_id, variable)
);

CREATE TABLE IF NOT EXISTS outputs (
  output_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    TEXT NOT NULL REFERENCES sessions(session_id),
  ts            TEXT NOT NULL,
  motor_version TEXT NOT NULL,
  producto_id   TEXT NOT NULL,
  score         REAL,
  pct_afinidad  REAL,
  rank          INTEGER,
  modo_cierre   TEXT,                    -- auto | asesor
  porque        TEXT                     -- la variable que justifica (H5.1)
);

CREATE TABLE IF NOT EXISTS labels (
  session_id  TEXT NOT NULL REFERENCES sessions(session_id),
  label       TEXT NOT NULL,             -- compro | abandono | handoff | no_elegible | remitido_aseguradora
  producto_id TEXT,
  ts          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_session  ON events(session_id, ts);
CREATE INDEX IF NOT EXISTS idx_outputs_session ON outputs(session_id, rank);
