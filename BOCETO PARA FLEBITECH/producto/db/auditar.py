"""Gap #9 — comando de auditoría en vivo (H0.4: cero infra, la consulta ES un comando).

Uso ante el jurado:
    python3 producto/db/auditar.py dorada-0001       # cadena completa de una sesión
    python3 producto/db/auditar.py --resumen         # embudo del flywheel
    python3 producto/db/auditar.py --listar          # todas las sesiones

Sin dependencias externas (solo stdlib) — corre desde cualquier terminal con
Python 3 sobre `producto/db/interactions.db`.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "interactions.db"

# Import perezoso — permite mostrar ayuda sin exigir que la DB exista.
def _conn():
    import sqlite3
    if not DB_PATH.exists():
        sys.exit(f"✗ No existe {DB_PATH}. Corre primero: python3 {Path(__file__).parent / 'trazabilidad.py'}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _ts(iso: str) -> str:
    """Reformatea ISO a HH:MM:SS para reporte compacto."""
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M:%S")
    except Exception:
        return iso or ""


def _fmt_json(s):
    if not s:
        return ""
    try:
        d = json.loads(s)
        return " · ".join(f"{k}={v}" for k, v in d.items() if not isinstance(v, (dict, list)))[:70]
    except Exception:
        return str(s)[:70]


def auditar(session_id: str):
    con = _conn()
    s = con.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if not s:
        sys.exit(f"✗ sesión '{session_id}' no existe")

    print(f"\n═══ Sesión {session_id} ═══")
    print(f"  canal={s['canal']}  origen={s['origen']}  afiliado={s['afiliado']}"
          f"  serie={s['serie'] or '—'}")
    print(f"  inicio={_ts(s['started_at'])}  fin={_ts(s['ended_at']) or 'en curso'}"
          f"  estado={s['estado_final']}")
    if s['producto_cerrado']:
        print(f"  producto vendido: {s['producto_cerrado']}")
    if s['paso_abandono']:
        print(f"  se fue en paso: {s['paso_abandono']}")
    hash_ok = "sí (SHA-256, Ley 1581)" if s['id_hash'] else "sin identificar"
    print(f"  cédula hasheada: {hash_ok}")

    # Features + FR-001 audit
    feats = list(con.execute(
        "SELECT variable, valor, fuente FROM features WHERE session_id=? ORDER BY variable",
        (session_id,),
    ))
    por_fuente = {}
    for f in feats:
        por_fuente[f["fuente"]] = por_fuente.get(f["fuente"], 0) + 1
    preguntas = por_fuente.get("pregunta", 0)
    cumple = "✓ CUMPLE" if preguntas <= 5 else "✗ VIOLA"
    print(f"\n─── FR-001 (máx 5 preguntas efectivas) ───")
    print(f"  preguntas efectivas: {preguntas}/5  →  {cumple}")
    print(f"  desglose: {dict(por_fuente)}")

    # Cronología
    events = list(con.execute(
        "SELECT ts, tipo, actor, contenido_raw, contenido_estructurado "
        "FROM events WHERE session_id=? ORDER BY event_id",
        (session_id,),
    ))
    if events:
        print(f"\n─── Cronología ({len(events)} eventos) ───")
        for e in events:
            texto = e["contenido_raw"] or _fmt_json(e["contenido_estructurado"])
            print(f"  {_ts(e['ts'])}  [{e['actor']:7} · {e['tipo']:14}] {texto[:70]}")

    # Features detalle
    if feats:
        print(f"\n─── Features (V1..V11) ───")
        for f in feats:
            marca = "?" if f["fuente"] == "pregunta" else " "
            print(f"  {marca} {f['variable']:4} = {(f['valor'] or ''):20} ← {f['fuente']}")

    # Outputs del motor
    outs = list(con.execute(
        "SELECT rank, producto_id, score, pct_afinidad, modo_cierre, porque "
        "FROM outputs WHERE session_id=? ORDER BY rank",
        (session_id,),
    ))
    if outs:
        print(f"\n─── Recomendación del motor ───")
        for o in outs:
            print(f"  #{o['rank']} {o['producto_id']:18} score={o['score']:5.1f}"
                  f"  afinidad={o['pct_afinidad']:5.1f}%  cierre={o['modo_cierre']:6}  ← {o['porque']}")

    # Label
    lbls = list(con.execute(
        "SELECT label, producto_id, ts FROM labels WHERE session_id=? ORDER BY ts",
        (session_id,),
    ))
    if lbls:
        print(f"\n─── Etiqueta (flywheel) ───")
        for l in lbls:
            prod = f" · {l['producto_id']}" if l['producto_id'] else ""
            print(f"  {_ts(l['ts'])}  {l['label']}{prod}")

    print()


def resumen():
    con = _conn()
    total_s = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    por_estado = dict(con.execute("SELECT estado_final, COUNT(*) FROM sessions GROUP BY estado_final"))
    por_label = dict(con.execute("SELECT label, COUNT(*) FROM labels GROUP BY label"))
    fr001 = con.execute(
        "SELECT COUNT(DISTINCT session_id) FROM features "
        "WHERE fuente='pregunta' GROUP BY session_id HAVING COUNT(*) > 5"
    ).fetchall()
    infractoras = len(fr001)

    print(f"\n═══ Resumen del flywheel ({DB_PATH.name}) ═══")
    print(f"  sesiones totales: {total_s}")
    print(f"  por estado:       {por_estado}")
    print(f"  labels (target):  {por_label}")
    print(f"  FR-001:           {infractoras} sesión(es) violaron el tope de 5 preguntas")
    print()


def listar():
    con = _conn()
    rows = list(con.execute(
        "SELECT session_id, canal, serie, estado_final, started_at "
        "FROM sessions ORDER BY started_at DESC"
    ))
    print(f"\n═══ Sesiones ({len(rows)}) ═══")
    for r in rows:
        print(f"  {r['session_id']:25} {r['canal']:9} serie={r['serie'] or '—':12}"
              f" {r['estado_final']:15} {_ts(r['started_at'])}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("session_id", nargs="?", help="Auditar una sesión específica")
    g.add_argument("--resumen", action="store_true", help="Embudo del flywheel")
    g.add_argument("--listar", action="store_true", help="Todas las sesiones")
    args = ap.parse_args()

    if args.resumen:
        resumen()
    elif args.listar:
        listar()
    else:
        auditar(args.session_id)


if __name__ == "__main__":
    main()
