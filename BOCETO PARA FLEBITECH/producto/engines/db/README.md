# DB de negocio · Reto 02 (Seguros)

DB de la cadena regulatoria **señal → score → oferta → decisión → póliza** (SC-003). Todo lo que se emite (cotizaciones, pólizas) y la máquina de estados del chat se escribe aquí — para demostrarle al jurado en vivo la trazabilidad de la venta.

> **Renombrado 25-jul (colisión con PR #9):** este archivo antes se llamaba `trazabilidad.db`. La trazabilidad de interacciones/aprendizaje (sessions, events, features, outputs, labels) vive ahora en `interactions.db` (paquete `producto/db/`). Las dos DBs coexisten con puente en `producto/db/puente_negocio.py`: al emitir póliza aquí, se dispara `label='compro'` allá.

- **Motor**: SQLite (D3, cerrada 2026-07-24). Cero infra, archivo único.
- **Ubicación del archivo**: `producto/engines/db/negocio.db` (gitignored — se regenera desde `schema_seguros.sql`).
- **Constitución II**: la prima **solo la escribe el motor**; la UI nunca envía primas. No hay póliza sin `consentimiento_ts` y sin `cotizacion_id`.
- **Constitución III**: todo dato personal es **sintético**. No usamos PII real ni siquiera en demo.

---

## Diagrama de flujo del dato

```
chat (Gemini) ──┐
                ├──► usuario_demo (perfil sintético)
base v2 ────────┘        │
                         ▼
                   score_resultado (V1..V7 usadas + ranking)
                         │
                         ▼
                   cotizacion (prima, veredicto de idoneidad)
                         │
                         ▼
                    poliza (numero, consentimiento_ts, hash)

  cualquier transición ──► evento_trazabilidad (paso, dato_json, ts)
```

`producto` **no es tabla**: el catálogo de 26 productos vive en `producto/engines/data/productos-seguros.json` y se carga en memoria (ver `plan.md`). Aquí solo guardamos el `producto_id` como texto.

---

## Tablas: qué guardar y de dónde viene cada campo

### `usuario_demo` — perfil del prospecto
| Campo | Origen del dato | Notas |
|---|---|---|
| `serie` | `SER-XXXXXX` de la base v2 (afiliado) o `LEAD-XXXX` generado (no afiliado) | PK |
| `es_afiliado` | Bifurcación paso 0 del chat | bool |
| `segmento` | Base v2 enmascarada | se pasa sin interpretar |
| `categoria` | Base v2 | A / B / C |
| `rango_salarial` | Base v2 (afiliado) · chat (no afiliado) | banda SMLV |
| `rango_edad` | Base v2 · chat | V1 del scoring |
| `genero` | Base v2 · chat | V2 |
| `situacion_laboral` | Base v2 · chat | V3 |
| `composicion_familiar` | Base v2 · chat | V5 |
| `creado_en` | Auto (`CURRENT_TIMESTAMP`) | |

### `score_resultado` — salida del `scoring_engine`
| Campo | Origen | Notas |
|---|---|---|
| `serie` | FK → `usuario_demo.serie` | |
| `variables_json` | Motor de scoring | **claves V1..V7 que sí entraron al cálculo** — traza de explicabilidad |
| `ranking_json` | Motor | `[{"producto_id": "vida_metlife", "puntaje": 0.82}, ...]` desc |
| `timestamp` | Auto | |

### `cotizacion` — prima calculada por el motor
| Campo | Origen | Notas |
|---|---|---|
| `serie` | FK → `usuario_demo` | |
| `producto_id` | Catálogo JSON (`productos-seguros.json`) | texto plano, no FK |
| `prima` | `quote_engine.py` | COP/mes; **solo el motor escribe este campo** |
| `veredicto_idoneidad` | Motor | `apto` · `alternativa_asequible` · `asistida` |
| `variables_json` | Motor | qué entró al cálculo de la prima |
| `score_id` | FK → `score_resultado.id` | encadena la traza |

### `poliza` — cierre de la venta
| Campo | Origen | Notas |
|---|---|---|
| `numero` | `producto/engines/db.py` (formato `COL-2026-XXXXX`) | PK |
| `serie` | FK → `usuario_demo` | |
| `producto_id`, `prima` | Copiados de `cotizacion` | denormalizado a propósito (auditoría) |
| `consentimiento_texto` | Texto exacto que el usuario aceptó inline | NOT NULL |
| `consentimiento_ts` | Momento de la aceptación | NOT NULL — sin esto no se emite |
| `hash` | `sha256(numero + serie + producto_id + prima + consentimiento_ts)` | prueba de emisión |
| `cotizacion_id` | FK → `cotizacion.id` | NOT NULL — cierra la cadena |

### `evento_trazabilidad` — máquina de estados
| Campo | Origen | Notas |
|---|---|---|
| `serie` | El chat (puede ser LEAD-XXXX antes de afiliar) | |
| `paso` | Estado actual del flujo (ver más abajo) | |
| `dato_json` | Payload libre: la respuesta, el score, el motivo de abandono, etc. | |
| `timestamp` | Auto | |

**Pasos válidos** (máquina de estados de `data-model.md`):

```
paso0  →  intencion  ┬─ (con intención)  → oferta → precio
                     └─ (sin intención)  → p1 → p2 → p3 → p4 → p5 → precio
precio → consentimiento → cierre  [→ paquete]
precio → abandono                                             (P3 · flywheel)
cualquier → derivacion (si producto asistida)                 (P3)
cierre (no afiliado) → lead_afiliacion
```

---

## Consultas típicas del pitch

**Ver la cadena completa de una venta:**
```sql
SELECT paso, dato_json, timestamp
FROM   evento_trazabilidad
WHERE  serie = 'SER-000001'
ORDER  BY timestamp;
```

**Dónde se están cayendo los prospectos (insumo del flywheel):**
```sql
SELECT paso, COUNT(*) AS fugas
FROM   evento_trazabilidad
WHERE  paso = 'abandono'
GROUP  BY paso;
```

**Explicabilidad — qué variables activaron esta póliza:**
```sql
SELECT p.numero, s.variables_json, s.ranking_json
FROM   poliza p
JOIN   cotizacion c ON c.id = p.cotizacion_id
JOIN   score_resultado s ON s.id = c.score_id
WHERE  p.numero = 'COL-2026-00001';
```

**Conversión bruta:**
```sql
SELECT
  (SELECT COUNT(*) FROM usuario_demo) AS prospectos,
  (SELECT COUNT(*) FROM cotizacion)   AS cotizados,
  (SELECT COUNT(*) FROM poliza)       AS emitidos;
```

---

## Cómo se llena la DB

1. **`schema_seguros.sql`** — DDL puro (5 tablas + índices).
2. **`seeds_demo.sql`** — 5 historias sintéticas listas para el pitch (Laura compra vida, Diego abandona, Marta se deriva a asesor, Camilo compra + paquete, Yeni lead no-afiliada que compra hogar).
3. **`__init__.py` + `__main__.py`** (paquete `producto.engines.db`) — puerta única de acceso: `session()`, `init_db()`, `traza()`, `crear_usuario_demo()`, `guardar_score()`, `cotizar()`, `emitir_poliza()`, `consultar_cadena()`, `explicabilidad()`, `puntos_fuga()`, `conversion()`. Todas las validaciones constitucionales viven aquí.

### Uso desde código (chat / motor)

```python
from producto.engines.db import session, traza, cotizar, emitir_poliza

with session() as con:
    traza(con, "paso0", serie, {"afiliada": True})
    cot_id = cotizar(con, serie, "vida", prima=28_400,
                     veredicto="apto", score_id=score_id)
    numero = emitir_poliza(con, cot_id, "Acepto contratar el seguro...")
    # commit implícito al salir del `with`
```

### CLI (para el pitch y debugging)

```bash
# preparar la DB del pitch (schema + 5 historias)
python -m producto.engines.db init --seed

# ver el embudo
python -m producto.engines.db stats
#   Conversión: {"prospectos": 5, "cotizados": 5, "emitidos": 3}
#   Terminales: {"abandono": 1, "derivacion": 1, "lead_afiliacion": 1, "cierre": 3}

# tira de eventos de una serie
python -m producto.engines.db cadena SER-000002

# variables que activaron una póliza
python -m producto.engines.db explicar COL-2026-00001

# apuntar a otra DB
python -m producto.engines.db --path /tmp/otra.db stats
```

Regenerar la DB desde cero sin la CLI (por si no tienes el módulo instalable):
```bash
cd producto/engines/db && rm -f negocio.db
python3 -c "import sqlite3, pathlib as p; d=p.Path('.'); c=sqlite3.connect('negocio.db'); c.executescript((d/'schema_seguros.sql').read_text()); c.executescript((d/'seeds_demo.sql').read_text())"
```

---

*Alineado con `data-model.md` de la spec 001-chat-venta-seguros. Reemplaza el schema v1 (que tenía `producto_seguro` + `conversacion`, hoy desalineado con la spec).*
