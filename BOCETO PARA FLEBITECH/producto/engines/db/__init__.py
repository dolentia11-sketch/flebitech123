"""Puerta única de acceso a la DB de negocio · Reto 02 (Seguros).

Este módulo es el **único** punto del proyecto donde se hace INSERT/UPDATE/DELETE
sobre `negocio.db`. Todo lo demás (chat, motor, n8n) habla con la DB a
través de estas funciones — nunca directo con `sqlite3`. Esa restricción existe
para que las reglas del proyecto se cumplan por diseño, no por disciplina:

Renombrado 25-jul (colisión con PR #9): antes `trazabilidad.db`. Ahora la
trazabilidad de interacciones/aprendizaje vive en `interactions.db` (PR #9,
paquete `producto/db/`). Este archivo guarda la cadena regulatoria de
negocio: cotización → póliza. Las dos DBs coexisten con puente en
`producto/db/puente_negocio.py`.

Invariantes que este módulo garantiza
-------------------------------------
* **Constitución II · venta adecuada**
    - `cotizacion.prima` solo se escribe desde `cotizar()` (nadie más puede).
    - `veredicto_idoneidad` debe ser uno de `VEREDICTOS_VALIDOS`.
    - `poliza` solo se crea vía `emitir_poliza()`, que exige
      `consentimiento_texto` no vacío y una `cotizacion` existente.
* **Constitución III · datos sintéticos**
    - No se valida contra PII real; el módulo no distingue afiliados reales.
* **FR-008 · trazabilidad total**
    - `emitir_poliza()` inserta automáticamente los eventos `consentimiento`
      y `cierre` en `evento_trazabilidad`. Emitir una póliza SIEMPRE deja rastro.

Ubicación de archivos
---------------------
* `schema_seguros.sql`  — DDL de las 5 tablas (colocado junto a este módulo).
* `seeds_demo.sql`      — 5 historias sintéticas para el pitch.
* `negocio.db`          — archivo SQLite (gitignored; se regenera).

Ejemplo de uso desde el chat
----------------------------
    from producto.engines.db import session, traza, cotizar, emitir_poliza

    with session() as con:
        traza(con, "paso0", serie, {"afiliada": True})
        # ... más eventos ...
        cot_id = cotizar(con, serie, "vida", prima=28_400,
                         veredicto="apto", score_id=score_id)
        traza(con, "precio", serie, {"prima_ofrecida": 28_400})
        numero = emitir_poliza(con, cot_id, "Acepto contratar el seguro...")
        # commit implícito al salir del `with`

CLI
---
    python -m producto.engines.db init                # crea la DB desde el schema
    python -m producto.engines.db init --seed          # + carga seeds_demo.sql
    python -m producto.engines.db cadena SER-000001    # tira de eventos
    python -m producto.engines.db explicar COL-2026-00001
    python -m producto.engines.db stats                # conversión + fugas

Nota sobre la ubicación
-----------------------
La spec (T007) pide literalmente `producto/engines/db.py`. Se implementó como
`producto/engines/db/__init__.py` (paquete) para evitar la colisión con el
directorio homónimo que aloja los archivos SQL. El *import path* es idéntico
(`producto.engines.db`), así que ningún consumidor cambia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


# ─────────────────────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR: Path = Path(__file__).parent
SCHEMA_PATH: Path = BASE_DIR / "schema_seguros.sql"
SEEDS_PATH: Path = BASE_DIR / "seeds_demo.sql"
DEFAULT_DB_PATH: Path = BASE_DIR / "negocio.db"

POLIZA_PREFIX: str = "COL-2026-"

VEREDICTOS_VALIDOS: frozenset[str] = frozenset({
    "apto", "alternativa_asequible", "asistida",
})

PASOS_VALIDOS: frozenset[str] = frozenset({
    "paso0", "intencion",
    "p1", "p2", "p3", "p4", "p5",
    "precio", "consentimiento", "cierre",
    "abandono", "derivacion", "lead_afiliacion", "paquete",
})


# ─────────────────────────────────────────────────────────────────────────────
# Excepciones
# ─────────────────────────────────────────────────────────────────────────────

class DBError(Exception):
    """Base para errores del módulo de negocio."""


class ValidacionError(DBError):
    """Se intentó violar una regla constitucional (venta adecuada, consentimiento, paso inválido)."""


class NotFoundError(DBError):
    """El recurso pedido (cotización, póliza, etc.) no existe."""


# ─────────────────────────────────────────────────────────────────────────────
# Conexión
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def session(path: Path | str = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    """Abre una conexión SQLite lista para uso transaccional.

    Configura `row_factory = sqlite3.Row` (acceso por nombre) y activa
    `PRAGMA foreign_keys` (SQLite las trae apagadas por default). Hace commit
    al salir sin error; rollback si algo lanza.

    Args:
        path: Ruta al archivo `.db`. Default: `negocio.db` junto a este módulo.

    Yields:
        Una conexión abierta y configurada.

    Ejemplo:
        >>> with session() as con:
        ...     traza(con, "paso0", "SER-000001", {"afiliada": True})
    """
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db(path: Path | str = DEFAULT_DB_PATH, *, with_seeds: bool = False) -> None:
    """Crea (o recrea) la DB ejecutando `schema_seguros.sql`.

    El schema usa `CREATE TABLE IF NOT EXISTS`, así que llamar dos veces es
    idempotente. Si `with_seeds=True`, también corre `seeds_demo.sql` — útil
    para preparar el archivo del pitch.

    Args:
        path: Ruta destino del `.db`. La carpeta padre se crea si no existe.
        with_seeds: Si True, carga las 5 historias demo después del schema.

    Raises:
        FileNotFoundError: Si `schema_seguros.sql` no se encuentra junto al módulo.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with session(path) as con:
        con.executescript(schema_sql)
        if with_seeds:
            if not SEEDS_PATH.exists():
                raise FileNotFoundError(f"No existe {SEEDS_PATH}")
            con.executescript(SEEDS_PATH.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# Escritura (los ÚNICOS INSERT permitidos en el proyecto)
# ─────────────────────────────────────────────────────────────────────────────

def crear_usuario_demo(
    con: sqlite3.Connection,
    serie: str,
    *,
    es_afiliado: bool,
    segmento: str | None = None,
    categoria: str | None = None,
    rango_salarial: str | None = None,
    rango_edad: str | None = None,
    genero: str | None = None,
    situacion_laboral: str | None = None,
    composicion_familiar: str | None = None,
) -> None:
    """Registra un prospecto sintético.

    Para afiliados el `serie` viene de la base v2 (`SER-XXXXXX`); para leads
    no afiliados, el chat genera `LEAD-XXXX`.

    Args:
        con: Conexión activa (usar `session()`).
        serie: Identificador único. PK de `usuario_demo`.
        es_afiliado: True si viene con SERIE de la base v2.
        segmento, categoria, rango_*, genero, situacion_laboral, composicion_familiar:
            Campos opcionales del perfil. Vienen enmascarados de la base v2 o
            declarados por el usuario en el chat si es lead.

    Raises:
        sqlite3.IntegrityError: Si la serie ya existe.
    """
    con.execute(
        """
        INSERT INTO usuario_demo (
            serie, es_afiliado, segmento, categoria, rango_salarial,
            rango_edad, genero, situacion_laboral, composicion_familiar
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (serie, es_afiliado, segmento, categoria, rango_salarial,
         rango_edad, genero, situacion_laboral, composicion_familiar),
    )


def guardar_score(
    con: sqlite3.Connection,
    serie: str,
    variables: dict[str, Any],
    ranking: list[dict[str, Any]],
) -> int:
    """Persiste la salida del `scoring_engine`.

    Args:
        con: Conexión activa.
        serie: FK a `usuario_demo.serie`.
        variables: Claves V1..V7/V11 que efectivamente entraron al cálculo.
            Se serializa como JSON (traza de explicabilidad · SC-003).
        ranking: Lista ordenada desc, forma `[{"producto_id": "vida", "puntaje": 0.87}, ...]`.

    Returns:
        El `id` autoincremental de la fila insertada (usar como `score_id` en
        la cotización que se derive).
    """
    cur = con.execute(
        """
        INSERT INTO score_resultado (serie, variables_json, ranking_json)
        VALUES (?, ?, ?)
        """,
        (
            serie,
            json.dumps(variables, ensure_ascii=False),
            json.dumps(ranking, ensure_ascii=False),
        ),
    )
    return int(cur.lastrowid)


def cotizar(
    con: sqlite3.Connection,
    serie: str,
    producto_id: str,
    prima: int,
    veredicto: str,
    *,
    variables: dict[str, Any] | None = None,
    score_id: int | None = None,
) -> int:
    """Registra una cotización calculada por el motor.

    Esta es la **única** puerta por la que puede escribirse una prima en la DB
    (constitución II · venta adecuada). La UI y el chat NO pueden.

    Args:
        con: Conexión activa.
        serie: FK a `usuario_demo.serie`.
        producto_id: Referencia al catálogo JSON (`productos.csv/json`).
        prima: COP/mes. Debe ser > 0.
        veredicto: Uno de `VEREDICTOS_VALIDOS`
            (`apto` | `alternativa_asequible` | `asistida`).
        variables: Insumos del cálculo (opcional pero muy recomendable).
        score_id: FK a `score_resultado.id`. Encadena la traza de explicabilidad.

    Returns:
        El `id` de la cotización (usar en `emitir_poliza`).

    Raises:
        ValidacionError: Si `prima <= 0` o `veredicto` no está en la whitelist.
    """
    if prima <= 0:
        raise ValidacionError(f"prima debe ser > 0, recibido: {prima}")
    if veredicto not in VEREDICTOS_VALIDOS:
        raise ValidacionError(
            f"veredicto '{veredicto}' inválido. "
            f"Debe ser uno de: {sorted(VEREDICTOS_VALIDOS)}"
        )
    cur = con.execute(
        """
        INSERT INTO cotizacion (
            serie, producto_id, prima, veredicto_idoneidad, variables_json, score_id
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            serie, producto_id, prima, veredicto,
            json.dumps(variables or {}, ensure_ascii=False),
            score_id,
        ),
    )
    return int(cur.lastrowid)


def emitir_poliza(
    con: sqlite3.Connection,
    cotizacion_id: int,
    consentimiento_texto: str,
) -> str:
    """Emite una póliza a partir de una cotización previamente registrada.

    Es la operación más blindada del módulo — bloquea todos los escenarios en
    que una póliza podría salir sin cumplir constitución II:

    * exige una cotización real (`NotFoundError` si no existe);
    * exige `consentimiento_texto` no vacío;
    * sella `consentimiento_ts` con la hora actual (UTC);
    * calcula `hash = sha256(numero|serie|producto_id|prima|ts)` como prueba
      criptográfica de emisión;
    * inserta automáticamente los eventos `consentimiento` y `cierre` en
      `evento_trazabilidad` (FR-008).

    Todo esto ocurre dentro de la misma transacción; si algo falla, no se
    emite media póliza.

    Args:
        con: Conexión activa.
        cotizacion_id: `id` devuelto por `cotizar()`.
        consentimiento_texto: Frase que el usuario aceptó inline en el chat.

    Returns:
        El número de póliza asignado (formato `COL-2026-XXXXX`).

    Raises:
        ValidacionError: Si el texto de consentimiento está vacío.
        NotFoundError: Si la cotización no existe.
    """
    if not consentimiento_texto or not consentimiento_texto.strip():
        raise ValidacionError(
            "consentimiento_texto no puede estar vacío (constitución II · sin "
            "consentimiento no hay emisión)"
        )

    row = con.execute(
        "SELECT serie, producto_id, prima FROM cotizacion WHERE id = ?",
        (cotizacion_id,),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"cotizacion #{cotizacion_id} no existe")

    numero = _siguiente_numero_poliza(con)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    hsh = _hash_poliza(numero, row["serie"], row["producto_id"], row["prima"], ts)

    con.execute(
        """
        INSERT INTO poliza (
            numero, serie, producto_id, prima, consentimiento_texto,
            consentimiento_ts, hash, cotizacion_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (numero, row["serie"], row["producto_id"], row["prima"],
         consentimiento_texto, ts, hsh, cotizacion_id),
    )

    traza(con, "consentimiento", row["serie"], {"aceptado": True, "hash_prefix": hsh[:16]})
    traza(con, "cierre",         row["serie"], {"poliza": numero, "prima": row["prima"]})

    return numero


def traza(
    con: sqlite3.Connection,
    paso: str,
    serie: str,
    dato: dict[str, Any] | None = None,
) -> None:
    """Registra una transición de estado del chat.

    Debe llamarse en CADA cambio de paso (FR-008). Es la función más usada del
    módulo — el chat la invoca decenas de veces por conversación.

    Args:
        con: Conexión activa.
        paso: Uno de `PASOS_VALIDOS`. Si no está, se rechaza (evita paso"typos"
            silenciosos que arruinan los reportes de fuga).
        serie: `SER-XXXXXX` (afiliado) o `LEAD-XXXX` (no afiliado).
        dato: Payload libre — la respuesta del usuario, el score, el motivo de
            abandono, etc. Se serializa como JSON.

    Raises:
        ValidacionError: Si `paso` no está en la whitelist.
    """
    if paso not in PASOS_VALIDOS:
        raise ValidacionError(
            f"paso '{paso}' inválido. Debe ser uno de: {sorted(PASOS_VALIDOS)}"
        )
    con.execute(
        "INSERT INTO evento_trazabilidad (serie, paso, dato_json) VALUES (?, ?, ?)",
        (serie, paso, json.dumps(dato or {}, ensure_ascii=False)),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Lectura (para el pitch y el flywheel)
# ─────────────────────────────────────────────────────────────────────────────

def consultar_cadena(con: sqlite3.Connection, serie: str) -> list[dict[str, Any]]:
    """Devuelve la tira ordenada de eventos de una conversación.

    Insumo directo del pitch — permite mostrar en vivo cómo fue la
    conversación de un prospecto. `dato_json` se deserializa a dict.

    Args:
        con: Conexión activa.
        serie: `SER-XXXXXX` o `LEAD-XXXX`.

    Returns:
        Lista de `{"paso": str, "dato": dict, "ts": str}` orden cronológico.
        Vacía si la serie no tiene eventos.
    """
    rows = con.execute(
        """
        SELECT paso, dato_json, timestamp
        FROM evento_trazabilidad
        WHERE serie = ?
        ORDER BY timestamp, id
        """,
        (serie,),
    ).fetchall()
    return [
        {"paso": r["paso"], "dato": json.loads(r["dato_json"] or "{}"), "ts": r["timestamp"]}
        for r in rows
    ]


def explicabilidad(con: sqlite3.Connection, numero_poliza: str) -> dict[str, Any]:
    """Devuelve qué variables activaron una póliza (SC-003).

    Encadena `poliza → cotizacion → score_resultado` para responder
    "¿por qué se emitió este seguro?" con evidencia auditable.

    Args:
        con: Conexión activa.
        numero_poliza: Formato `COL-2026-XXXXX`.

    Returns:
        Dict con `numero`, `prima`, `consentimiento_ts`, `variables_usadas` y `ranking`.

    Raises:
        NotFoundError: Si la póliza no existe.
    """
    row = con.execute(
        """
        SELECT p.numero, p.prima, p.consentimiento_ts,
               s.variables_json, s.ranking_json
        FROM   poliza p
        JOIN   cotizacion c      ON c.id = p.cotizacion_id
        JOIN   score_resultado s ON s.id = c.score_id
        WHERE  p.numero = ?
        """,
        (numero_poliza,),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"póliza {numero_poliza} no existe")
    return {
        "numero": row["numero"],
        "prima": row["prima"],
        "consentimiento_ts": row["consentimiento_ts"],
        "variables_usadas": json.loads(row["variables_json"]),
        "ranking": json.loads(row["ranking_json"]),
    }


def puntos_fuga(con: sqlite3.Connection) -> dict[str, int]:
    """Cuenta eventos terminales por tipo (insumo del flywheel).

    Devuelve un dict con las claves `abandono`, `derivacion`, `lead_afiliacion`
    y `cierre` (con 0 si no hay). Sirve para saber dónde se caen los
    prospectos y ajustar el flujo.

    Args:
        con: Conexión activa.

    Returns:
        `{"abandono": N, "derivacion": N, "lead_afiliacion": N, "cierre": N}`.
    """
    terminales = ("abandono", "derivacion", "lead_afiliacion", "cierre")
    rows = con.execute(
        f"""
        SELECT paso, COUNT(*) AS n
        FROM   evento_trazabilidad
        WHERE  paso IN ({",".join("?" * len(terminales))})
        GROUP  BY paso
        """,
        terminales,
    ).fetchall()
    resultado = {p: 0 for p in terminales}
    for r in rows:
        resultado[r["paso"]] = r["n"]
    return resultado


def conversion(con: sqlite3.Connection) -> dict[str, int]:
    """Métricas brutas del embudo.

    Returns:
        `{"prospectos": N, "cotizados": N, "emitidos": N}`.
    """
    return {
        "prospectos": con.execute("SELECT COUNT(*) FROM usuario_demo").fetchone()[0],
        "cotizados":  con.execute("SELECT COUNT(*) FROM cotizacion").fetchone()[0],
        "emitidos":   con.execute("SELECT COUNT(*) FROM poliza").fetchone()[0],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internos (no exportados)
# ─────────────────────────────────────────────────────────────────────────────

def _siguiente_numero_poliza(con: sqlite3.Connection) -> str:
    """Genera el siguiente número secuencial `COL-2026-XXXXX`.

    Lee el último número existente y suma 1. Se llama dentro de la misma
    transacción que hace el INSERT en `poliza`, así que no hay condiciones de
    carrera dentro de una sesión.
    """
    row = con.execute(
        "SELECT numero FROM poliza WHERE numero LIKE ? ORDER BY numero DESC LIMIT 1",
        (f"{POLIZA_PREFIX}%",),
    ).fetchone()
    if row is None:
        siguiente = 1
    else:
        siguiente = int(row["numero"].removeprefix(POLIZA_PREFIX)) + 1
    return f"{POLIZA_PREFIX}{siguiente:05d}"


def _hash_poliza(numero: str, serie: str, producto_id: str, prima: int, ts: str) -> str:
    """Calcula el hash sha256 que sella la emisión.

    Formato de la cadena a hashear: `numero|serie|producto_id|prima|ts`
    (idéntico al usado en `seeds_demo.sql` para consistencia).
    """
    raw = f"{numero}|{serie}|{producto_id}|{prima}|{ts}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# CLI — `python -m producto.engines.db <subcomando>`
# ─────────────────────────────────────────────────────────────────────────────

def _cmd_init(args: argparse.Namespace) -> None:
    init_db(args.path, with_seeds=args.seed)
    extra = " (con seeds)" if args.seed else ""
    print(f"OK · DB inicializada en {args.path}{extra}")


def _cmd_cadena(args: argparse.Namespace) -> None:
    with session(args.path) as con:
        eventos = consultar_cadena(con, args.serie)
    if not eventos:
        print(f"Sin eventos para {args.serie}")
        return
    for e in eventos:
        print(f"[{e['ts']}] {e['paso']:16} {json.dumps(e['dato'], ensure_ascii=False)}")


def _cmd_explicar(args: argparse.Namespace) -> None:
    with session(args.path) as con:
        info = explicabilidad(con, args.numero)
    print(json.dumps(info, ensure_ascii=False, indent=2))


def _cmd_stats(args: argparse.Namespace) -> None:
    with session(args.path) as con:
        conv = conversion(con)
        fugas = puntos_fuga(con)
    print("Conversión:", json.dumps(conv, ensure_ascii=False))
    print("Terminales:", json.dumps(fugas, ensure_ascii=False))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="producto.engines.db",
        description="DB de negocio · Reto 02 · Colsubsidio 2026",
    )
    parser.add_argument(
        "--path", type=Path, default=DEFAULT_DB_PATH,
        help=f"Ruta al archivo .db (default: {DEFAULT_DB_PATH})",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Crea la DB desde schema_seguros.sql")
    p_init.add_argument("--seed", action="store_true",
                        help="Además carga seeds_demo.sql (5 historias del pitch)")
    p_init.set_defaults(func=_cmd_init)

    p_cad = sub.add_parser("cadena", help="Muestra la tira cronológica de eventos de una serie")
    p_cad.add_argument("serie", help="Ej: SER-000001 o LEAD-0001")
    p_cad.set_defaults(func=_cmd_cadena)

    p_exp = sub.add_parser("explicar", help="Muestra variables + ranking que activaron una póliza")
    p_exp.add_argument("numero", help="Ej: COL-2026-00001")
    p_exp.set_defaults(func=_cmd_explicar)

    p_st = sub.add_parser("stats", help="Conversión (prospectos/cotizados/emitidos) y terminales")
    p_st.set_defaults(func=_cmd_stats)

    return parser


def _main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (ValidacionError, NotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
