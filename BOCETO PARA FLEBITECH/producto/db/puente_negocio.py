"""Gap #5 — puente entre `interactions.db` (trazabilidad, PR #9) y
`negocio.db` (paquete producto/engines/db, T007).

Arquitectura acordada 25-jul (post-rename):
- `interactions.db` = trazabilidad de interacciones + flywheel de aprendizaje.
- `negocio.db`      = cadena regulatoria (cotización → póliza).

Este módulo NO abre negocio.db — solo mantiene el link lógico (`sessions.serie`)
y las etiquetas del flywheel (`labels`). El paquete de T007 sigue siendo la
puerta única sobre negocio.db. La integración recomendada es que, dentro de
`emitir_poliza()` de T007, se llame a `cerrar_por_venta()` de este módulo
para dejar la señal en trazabilidad.

Uso rápido:
    python3 puente_negocio.py
"""

import sqlite3
from pathlib import Path

from trazabilidad import (
    DB_PATH,
    _conn,
    _now,
    cerrar_sesion,
    crear_sesion,
    log_interaction,
    registrar_label,
)

EXTENSION_PATH = Path(__file__).parent / "schema_extension.sql"


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def aplicar_extension() -> bool:
    """Aplica schema_extension.sql. Idempotente: si `serie` ya existe, no toca.
    Devuelve True si aplicó cambios, False si ya estaba."""
    with _conn() as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(sessions)")}
        if "serie" in cols:
            return False
        con.executescript(EXTENSION_PATH.read_text())
        return True


# ---------------------------------------------------------------------------
# Puente
# ---------------------------------------------------------------------------

def vincular_sesion_a_serie(session_id: str, serie: str) -> None:
    """Asocia la sesión de chat con un `usuario_demo.serie` de negocio.db.
    Llamar apenas se resuelva quién es el usuario (paso0 del flujo)."""
    with _conn() as con:
        con.execute("UPDATE sessions SET serie=? WHERE session_id=?", (serie, session_id))


def cerrar_por_venta(session_id: str, producto_id: str) -> None:
    """Registrar cierre exitoso en trazabilidad. Idealmente llamada desde
    `emitir_poliza()` de T007, justo después del INSERT en negocio.poliza."""
    log_interaction(session_id, "cierre", "motor", None, {"producto_id": producto_id, "resultado": "venta"})
    registrar_label(session_id, "compro", producto_id)
    cerrar_sesion(session_id, "cerrada", producto_cerrado=producto_id)


def cerrar_por_abandono(session_id: str, paso_abandono: str) -> None:
    """Registrar abandono en trazabilidad (H8.2: los que se van también son señal)."""
    log_interaction(session_id, "abandono", "motor", None, {"paso": paso_abandono})
    registrar_label(session_id, "abandono")
    cerrar_sesion(session_id, "abandonada", paso_abandono=paso_abandono)


def cerrar_por_handoff(session_id: str, motivo: str) -> None:
    """Derivación a asesor humano (constitución II · producto asistida)."""
    log_interaction(session_id, "handoff", "motor", None, {"motivo": motivo})
    registrar_label(session_id, "handoff")
    cerrar_sesion(session_id, "handoff_asesor")


# ---------------------------------------------------------------------------
# Lecturas para reporte
# ---------------------------------------------------------------------------

def sesiones_por_serie(serie: str) -> list[dict]:
    """Todas las sesiones de un usuario del negocio, ordenadas por fecha."""
    with _conn() as con:
        return [dict(r) for r in con.execute(
            "SELECT session_id, started_at, ended_at, estado_final, producto_cerrado "
            "FROM sessions WHERE serie=? ORDER BY started_at",
            (serie,),
        )]


def resumen_flywheel() -> dict:
    """Distribución de labels — insumo del flywheel (H8.2 + P3)."""
    with _conn() as con:
        return dict(con.execute(
            "SELECT label, COUNT(*) FROM labels GROUP BY label"
        ).fetchall())


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def _demo():
    print(f"[extension] aplicada ahora: {aplicar_extension()}")

    SID = "demo-puente"
    SERIE = "SER-000042"

    # Reset por si se re-corre
    with sqlite3.connect(DB_PATH) as con:
        for tbl in ("labels", "outputs", "features", "events", "sessions"):
            con.execute(f"DELETE FROM {tbl} WHERE session_id=?", (SID,))

    sid = crear_sesion(canal="web", origen="qr", afiliado=1, session_id=SID)
    vincular_sesion_a_serie(sid, SERIE)
    print(f"[vincular] sesión {sid} ↔ serie {SERIE}")

    cerrar_por_venta(sid, "seguro-vida")
    print(f"[venta   ] label 'compro' + cierre registrados")

    print(f"[reporte ] sesiones de {SERIE}: {sesiones_por_serie(SERIE)}")
    print(f"[flywheel] distribución de labels: {resumen_flywheel()}")

    # Ejemplo de integración con T007 (comentado — necesita PYTHONPATH):
    # from producto.engines.db import session, emitir_poliza
    # with session() as con:
    #     numero = emitir_poliza(con, cot_id, "Acepto...")
    # cerrar_por_venta(sid, producto_id)   # ← lo que T007 debería llamar


if __name__ == "__main__":
    _demo()
