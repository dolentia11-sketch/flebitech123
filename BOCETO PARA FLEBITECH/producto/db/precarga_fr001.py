"""Gap #2 (precarga desde CRM) y Gap #4 (contador FR-001).

Se apoya en la API pública de `trazabilidad.py` sin modificarla. El motor
de Sebas debe usar `registrar_feature_pregunta()` cuando la variable venga
de una pregunta al usuario — el wrapper corta a la 6ta y evita romper FR-001.

Uso rápido:
    python3 precarga_fr001.py
"""

import sqlite3
from trazabilidad import (
    DB_PATH,
    _conn,
    crear_sesion,
    hash_id,
    registrar_feature,
)

# Mapa CRM → V-code del motor. Confirmar V10/V11 con Sebas.
CRM_A_VARIABLE = {
    "edad":                "V1",
    "genero":              "V2",
    "ocupacion":           "V3",
}

MAX_PREGUNTAS_EFECTIVAS = 5  # FR-001


class FR001Excedido(Exception):
    """Se intentó registrar una 6ta pregunta efectiva en la misma sesión."""


# --- Gap #2 ------------------------------------------------------------------

def precargar_features_desde_crm(session_id: str, cedula: str) -> list[str]:
    """Consulta el CRM simulado, escribe `sessions.id_hash` (SHA-256) y llena
    features con `fuente='precarga_crm'`. Devuelve las variables cargadas.

    Contrato: llamarla ANTES de arrancar el diálogo. Lo que precarga NO cuenta
    contra el tope FR-001 — de eso trata la precarga.
    """
    from crm_simulado import consultar

    registro = consultar(cedula)
    if registro is None:
        return []

    with _conn() as con:
        con.execute(
            "UPDATE sessions SET id_hash=? WHERE session_id=?",
            (hash_id(cedula), session_id),
        )

    cargadas = []
    for campo, variable in CRM_A_VARIABLE.items():
        if campo not in registro:
            continue
        valor = registro[campo]
        if isinstance(valor, bool):
            valor = "si" if valor else "no"
        registrar_feature(session_id, variable, str(valor), "precarga_crm")
        cargadas.append(variable)
    return cargadas


# --- Gap #4 ------------------------------------------------------------------

def preguntas_efectivas(session_id: str) -> int:
    """Cuenta features con fuente='pregunta' — la métrica auditable de FR-001."""
    with _conn() as con:
        return con.execute(
            "SELECT COUNT(*) FROM features WHERE session_id=? AND fuente='pregunta'",
            (session_id,),
        ).fetchone()[0]


def puede_hacer_pregunta(session_id: str) -> bool:
    return preguntas_efectivas(session_id) < MAX_PREGUNTAS_EFECTIVAS


def registrar_feature_pregunta(session_id: str, variable: str, valor: str, ts=None) -> None:
    """Wrapper con gate FR-001. Usar cuando la fuente es una pregunta al usuario.
    Para `precarga_crm` o `inferencia`, usar `registrar_feature` directo."""
    if not puede_hacer_pregunta(session_id):
        raise FR001Excedido(
            f"Sesión {session_id} ya alcanzó {MAX_PREGUNTAS_EFECTIVAS} preguntas "
            f"efectivas (FR-001). Usar inferencia o handoff a asesor."
        )
    registrar_feature(session_id, variable, valor, "pregunta", ts=ts)


def auditar_sesion(session_id: str) -> dict:
    """Reporte para el jurado (H0.4): ¿cumplió FR-001 y de dónde salió cada variable?"""
    with _conn() as con:
        por_fuente = dict(con.execute(
            "SELECT fuente, COUNT(*) FROM features WHERE session_id=? GROUP BY fuente",
            (session_id,),
        ).fetchall())
    preguntas = por_fuente.get("pregunta", 0)
    return {
        "session_id": session_id,
        "preguntas_efectivas": preguntas,
        "tope_fr001": MAX_PREGUNTAS_EFECTIVAS,
        "cumple_fr001": preguntas <= MAX_PREGUNTAS_EFECTIVAS,
        "features_por_fuente": por_fuente,
    }


# --- Smoke test (demo) -------------------------------------------------------

def _demo():
    DEMO_SID = "demo-fr001"

    # Reset por si se re-corre
    with sqlite3.connect(DB_PATH) as con:
        for tbl in ("labels", "outputs", "features", "events", "sessions"):
            con.execute(f"DELETE FROM {tbl} WHERE session_id=?", (DEMO_SID,))

    sid = crear_sesion(canal="web", origen="qr", afiliado=1, session_id=DEMO_SID)

    # Gap #2: precarga → 5 vars sin gastar preguntas efectivas
    cargadas = precargar_features_desde_crm(sid, "1010101010")
    print(f"[gap#2] CRM precargó {len(cargadas)} vars {cargadas} — preguntas gastadas: {preguntas_efectivas(sid)}")

    # Gap #4: 5 preguntas OK, la 6ta debe cortar
    for var, val in [("V4", "1-1.5 SMLV"), ("V5", "monoparental"),
                     ("V6", "arriendo"),   ("V7", "no"), ("V8", "no")]:
        registrar_feature_pregunta(sid, var, val)
    print(f"[gap#4] 5 preguntas hechas — puede_hacer_pregunta: {puede_hacer_pregunta(sid)}")

    try:
        registrar_feature_pregunta(sid, "V9", "no")
        print("[gap#4] BUG: la 6ta pregunta pasó — FR-001 NO se aplica")
    except FR001Excedido as e:
        print(f"[gap#4] 6ta pregunta bloqueada ✓ → {e}")

    print(f"[audit ] {auditar_sesion(sid)}")


if __name__ == "__main__":
    _demo()
