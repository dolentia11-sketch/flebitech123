-- Reto 02 · Esquema de negocio (Venta Automatizada de Seguros)
-- Hackathon Colsubsidio 2026 · Scala Labs
--
-- FR-008 + Constitución III: una sola DB, un solo esquema. Todo dato personal
-- es sintético. `producto` NO es tabla: el catálogo vive en JSON (data/) y se
-- carga en memoria; aquí solo guardamos el `producto_id` referenciado.
--
-- Motor: SQLite (D3, cerrada 2026-07-24). Compatible con Postgres con
-- ajustes mínimos (AUTOINCREMENT → SERIAL, TEXT JSON → JSONB si se quiere).
--
-- Historia: reemplaza el schema v1 de JD (producto_seguro + conversacion),
-- que quedó desalineado con data-model.md (5 tablas: usuario_demo,
-- score_resultado, cotizacion, poliza, evento_trazabilidad).

PRAGMA foreign_keys = ON;

-- ── usuario_demo ────────────────────────────────────────────────────────────
-- Perfil sintético del prospecto. Para no afiliados: serie = 'LEAD-XXXX'.
-- Bandas y categorías vienen enmascaradas de la base v2; no se interpretan.
CREATE TABLE IF NOT EXISTS usuario_demo (
    serie                TEXT PRIMARY KEY,
    es_afiliado          BOOLEAN NOT NULL,
    segmento             TEXT,
    categoria            TEXT,               -- A | B | C
    rango_salarial       TEXT,               -- banda SMLV
    rango_edad           TEXT,               -- V1
    genero               TEXT,               -- V2
    situacion_laboral    TEXT,               -- V3 (declarada en chat si no afiliado)
    composicion_familiar TEXT,               -- V5
    creado_en            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── score_resultado ─────────────────────────────────────────────────────────
-- Salida del scoring_engine. `variables_json` guarda las claves V1..V7/V11
-- que efectivamente entraron al cálculo (trazabilidad de explicabilidad, SC-003).
-- `ranking_json` es [{producto_id, puntaje}, ...] ordenado desc.
CREATE TABLE IF NOT EXISTS score_resultado (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    serie           TEXT NOT NULL REFERENCES usuario_demo(serie),
    variables_json  TEXT NOT NULL,
    ranking_json    TEXT NOT NULL,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── cotizacion ──────────────────────────────────────────────────────────────
-- La prima SOLO la escribe el motor (constitución II · venta adecuada).
-- La UI nunca envía primas. veredicto_idoneidad ∈ {apto | alternativa_asequible | asistida}.
CREATE TABLE IF NOT EXISTS cotizacion (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    serie               TEXT NOT NULL REFERENCES usuario_demo(serie),
    producto_id         TEXT NOT NULL,      -- referencia al catálogo JSON
    prima               INTEGER NOT NULL,   -- COP/mes
    veredicto_idoneidad TEXT NOT NULL,
    variables_json      TEXT,
    score_id            INTEGER REFERENCES score_resultado(id),
    creado_en           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── poliza ──────────────────────────────────────────────────────────────────
-- Cierre de la cadena señal → score → oferta → decisión → póliza.
-- Reglas duras (constitución II): consentimiento_ts y cotizacion_id NOT NULL.
-- hash = sha256(numero + serie + producto_id + prima + consentimiento_ts).
CREATE TABLE IF NOT EXISTS poliza (
    numero               TEXT PRIMARY KEY,   -- COL-2026-XXXXX
    serie                TEXT NOT NULL REFERENCES usuario_demo(serie),
    producto_id          TEXT NOT NULL,
    prima                INTEGER NOT NULL,
    consentimiento_texto TEXT NOT NULL,
    consentimiento_ts    TIMESTAMP NOT NULL,
    hash                 TEXT NOT NULL,
    cotizacion_id        INTEGER NOT NULL REFERENCES cotizacion(id),
    emitida_en           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── evento_trazabilidad ─────────────────────────────────────────────────────
-- Máquina de estados del chat. Se escribe en CADA transición, incluido abandono.
-- pasos válidos: paso0 | intencion | p1..p5 | precio | consentimiento | cierre
--                | abandono | derivacion | lead_afiliacion | paquete
CREATE TABLE IF NOT EXISTS evento_trazabilidad (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    serie      TEXT NOT NULL,                -- puede ser LEAD-XXXX antes de afiliar
    paso       TEXT NOT NULL,
    dato_json  TEXT,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── índices (demo en vivo: SELECT por serie/paso debe ser instantáneo) ─────
CREATE INDEX IF NOT EXISTS idx_evento_serie_ts   ON evento_trazabilidad(serie, timestamp);
CREATE INDEX IF NOT EXISTS idx_evento_paso       ON evento_trazabilidad(paso);
CREATE INDEX IF NOT EXISTS idx_cotizacion_serie  ON cotizacion(serie);
CREATE INDEX IF NOT EXISTS idx_cotizacion_score  ON cotizacion(score_id);
CREATE INDEX IF NOT EXISTS idx_score_serie       ON score_resultado(serie);
CREATE INDEX IF NOT EXISTS idx_poliza_serie      ON poliza(serie);
