"""DB de trazabilidad — kit de arranque.

Uso rápido:
    python3 trazabilidad.py            # crea interactions.db, inserta la sesión
                                       # dorada y exporta interactions.json
Desde el motor (Sebas) o Make (vía script):
    from trazabilidad import log_interaction, registrar_feature, registrar_output
"""

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "interactions.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db():
    """Crea la DB desde schema.sql. Idempotente: si la DB ya existe, migra
    columnas nuevas sin tocar filas existentes (evita romper DBs previas)."""
    with _conn() as con:
        con.executescript(SCHEMA_PATH.read_text())
        # Migraciones idempotentes para DBs creadas antes del cambio.
        cols_sessions = {r[1] for r in con.execute("PRAGMA table_info(sessions)")}
        if "aseguradora_id" not in cols_sessions:
            con.execute("ALTER TABLE sessions ADD COLUMN aseguradora_id TEXT")


def hash_id(cedula: str) -> str:
    """La cédula JAMÁS se guarda en claro (Ley 1581)."""
    return hashlib.sha256(cedula.encode()).hexdigest()


def crear_sesion(canal="web", origen="directo", afiliado=0, session_id=None):
    sid = session_id or str(uuid.uuid4())
    with _conn() as con:
        con.execute(
            "INSERT INTO sessions (session_id, started_at, canal, origen, afiliado) VALUES (?,?,?,?,?)",
            (sid, _now(), canal, origen, afiliado),
        )
    return sid


def log_interaction(session_id, tipo, actor, contenido_raw=None, contenido_estructurado=None, ts=None):
    """Un evento por interacción. Raw y estructurado SIEMPRE separados."""
    with _conn() as con:
        con.execute(
            "INSERT INTO events (session_id, ts, tipo, actor, contenido_raw, contenido_estructurado) VALUES (?,?,?,?,?,?)",
            (session_id, ts or _now(), tipo, actor, contenido_raw,
             json.dumps(contenido_estructurado, ensure_ascii=False) if isinstance(contenido_estructurado, dict) else contenido_estructurado),
        )


def registrar_feature(session_id, variable, valor, fuente, ts=None):
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO features (session_id, variable, valor, fuente, ts) VALUES (?,?,?,?,?)",
            (session_id, variable, valor, fuente, ts or _now()),
        )


def registrar_output(session_id, motor_version, producto_id, score, pct_afinidad, rank, modo_cierre, porque, ts=None):
    with _conn() as con:
        con.execute(
            "INSERT INTO outputs (session_id, ts, motor_version, producto_id, score, pct_afinidad, rank, modo_cierre, porque) VALUES (?,?,?,?,?,?,?,?,?)",
            (session_id, ts or _now(), motor_version, producto_id, score, pct_afinidad, rank, modo_cierre, porque),
        )


def registrar_label(session_id, label, producto_id=None, ts=None):
    with _conn() as con:
        con.execute(
            "INSERT INTO labels (session_id, label, producto_id, ts) VALUES (?,?,?,?)",
            (session_id, label, producto_id, ts or _now()),
        )


def cerrar_sesion(session_id, estado_final, producto_cerrado=None, paso_abandono=None,
                  consent_datos=None, consent_compra=None, id_hash=None, aseguradora_id=None):
    sets, vals = ["ended_at=?", "estado_final=?"], [_now(), estado_final]
    for col, v in (("producto_cerrado", producto_cerrado), ("paso_abandono", paso_abandono),
                   ("consent_datos", consent_datos), ("consent_compra", consent_compra),
                   ("id_hash", id_hash), ("aseguradora_id", aseguradora_id)):
        if v is not None:
            sets.append(f"{col}=?")
            vals.append(v)
    with _conn() as con:
        con.execute(f"UPDATE sessions SET {', '.join(sets)} WHERE session_id=?", (*vals, session_id))


def exportar_interactions_json(destino=None):
    """Exporta la DB al formato que consume la pantalla del PR #10."""
    destino = Path(destino or Path(__file__).parent / "interactions.json")
    with _conn() as con:
        data = {
            "version": "1.0",
            "exportado": _now(),
            "sessions": [dict(r) for r in con.execute("SELECT * FROM sessions ORDER BY started_at")],
            "events": [dict(r) for r in con.execute("SELECT * FROM events ORDER BY session_id, ts")],
            "features": [dict(r) for r in con.execute("SELECT * FROM features ORDER BY session_id, variable")],
            "outputs": [dict(r) for r in con.execute("SELECT * FROM outputs ORDER BY session_id, rank")],
            "labels": [dict(r) for r in con.execute("SELECT * FROM labels ORDER BY session_id, ts")],
        }
    destino.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return destino


def sesion_dorada():
    """Inserta la sesión de prueba del esquema. Si se escribe y se lee completa,
    la integración de las 5pm está asegurada."""
    sid = crear_sesion(canal="web", origen="campaña", afiliado=1, session_id="dorada-0001")
    log_interaction(sid, "pregunta", "llm", "¡Hola! ¿Qué te gustaría proteger hoy?")
    log_interaction(sid, "respuesta", "usuario", "Quiero un seguro de vida",
                    {"intencion": "vida", "match": "directo"})
    log_interaction(sid, "consulta_crm", "make", None,
                    {"resultado": "afiliado_encontrado", "campos": ["nombre", "edad", "genero", "ocupacion", "ciudad"]})
    # 11 variables: mezcla de fuentes (3 preguntas + 5 precarga + 3 inferencia)
    fuentes = {
        "V1": ("34", "precarga_crm"), "V2": ("F", "precarga_crm"),
        "V3": ("empleada", "precarga_crm"), "V4": ("1-1.5 SMLV", "pregunta"),
        "V5": ("monoparental 2 hijos", "pregunta"), "V6": ("arriendo", "pregunta"),
        "V7": ("no", "inferencia"), "V8": ("no", "inferencia"),
        "V9": ("no", "inferencia"), "V10": ("no", "precarga_crm"),
        "V11": ("si", "precarga_crm"),
    }
    for var, (valor, fuente) in fuentes.items():
        registrar_feature(sid, var, valor, fuente)
    log_interaction(sid, "recomendacion", "motor", None, {"top": 3})
    registrar_output(sid, "v1.0", "seguro-vida", 41.2, 87.2, 1, "asesor", "V5: personas a cargo")
    registrar_output(sid, "v1.0", "plan-exequial", 33.0, 69.8, 2, "auto", "V5 + V4")
    registrar_output(sid, "v1.0", "ap-digital", 28.5, 60.3, 3, "auto", "V3: actividad laboral")
    log_interaction(sid, "consentimiento", "usuario", "Acepto",
                    {"tipo": "habeas_data", "aceptado": True})
    log_interaction(sid, "cierre", "make", None, {"paso": "pago_simulado"})
    registrar_label(sid, "compro", "seguro-vida")
    cerrar_sesion(sid, "cerrada", producto_cerrado="seguro-vida",
                  consent_datos=1, consent_compra=1, id_hash=hash_id("demo-0000"))
    return sid


if __name__ == "__main__":
    init_db()
    sid = sesion_dorada()
    out = exportar_interactions_json()
    with _conn() as con:
        n = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("sessions", "events", "features", "outputs", "labels")}
    print(f"Sesión dorada '{sid}' escrita y leída ✓ → {n}")
    print(f"Export para la pantalla (PR #10): {out}")
