# Etapa 3 — Proteger métricas, sesiones y CORS

## Objetivo

Evitar cruces accidentales entre sesiones, restringir qué sitios pueden llamar la API y dejar claro que `session_id` no es autenticación. Esta etapa no queda cerrada si el endpoint público puede devolver datos sensibles con un identificador ajeno.

## Archivos autorizados

- `backend/metrics.py`
- `api/index.py`
- `.env.example`
- pruebas de API/métricas

## Paso 1. Crear la rama

Después de fusionar la etapa anterior:

```bash
git switch master
git pull --ff-only
git switch -c fix/metrics-session-scope
```

## Paso 2. Filtrar interacciones por sesión

En `backend/metrics.py`, reemplaza `get_recent_interactions()` por:

```python
def get_recent_interactions(limit: int = 10, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    safe_limit = max(1, min(int(limit), 100))
    with _lock:
        cursor = conn.cursor()
        if session_id:
            cursor.execute(
                "SELECT timestamp, session_id, query, topic, had_answer, source_docs, latency_ms "
                "FROM interactions WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, safe_limit),
            )
        else:
            cursor.execute(
                "SELECT timestamp, session_id, query, topic, had_answer, source_docs, latency_ms "
                "FROM interactions ORDER BY id DESC LIMIT ?",
                (safe_limit,),
            )
        rows = [dict(r) for r in cursor.fetchall()]
    if not IS_VERCEL:
        conn.close()
    return rows
```

Reemplaza `get_knowledge_gaps()` por:

```python
def get_knowledge_gaps(limit: int = 10, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    safe_limit = max(1, min(int(limit), 100))
    with _lock:
        cursor = conn.cursor()
        if session_id:
            cursor.execute(
                "SELECT timestamp, query, topic FROM interactions "
                "WHERE had_answer = 0 AND session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, safe_limit),
            )
        else:
            cursor.execute(
                "SELECT timestamp, query, topic FROM interactions "
                "WHERE had_answer = 0 ORDER BY id DESC LIMIT ?",
                (safe_limit,),
            )
        rows = [dict(r) for r in cursor.fetchall()]
    if not IS_VERCEL:
        conn.close()
    return rows
```

La consulta sigue parametrizada; no formes SQL con f-strings.

No devuelvas `response` en métricas públicas. El texto completo de la respuesta puede contener datos clínicos escritos por el usuario o inferidos en la conversación; si se necesita para auditoría, debe quedar detrás de identidad/autorización y política de retención.

## Paso 3. Aplicar el filtro desde la API

En `/api/metrics` de `api/index.py`, cambia:

```python
recent = get_recent_interactions(limit=10)
gaps = get_knowledge_gaps(limit=10)
```

por:

```python
recent = get_recent_interactions(limit=10, session_id=session_id)
gaps = get_knowledge_gaps(limit=10, session_id=session_id)
```

Elimina el import interno duplicado de `get_knowledge_gaps`, porque ya está importado al comienzo.

## Paso 4. Validar `session_id`

En `api/index.py`, importa:

```python
from pydantic import BaseModel, Field
```

En `ChatRequest`, cambia `session_id` por:

```python
session_id: str = Field(default="web_session", min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
```

En `get_metrics`, usa validación equivalente:

```python
@app.get("/api/metrics")
def get_metrics(session_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,64}", session_id):
        raise HTTPException(status_code=400, detail="session_id inválido")
```

Añade `import re` arriba de `api/index.py`.

## Paso 5. Cerrar CORS

Antes de `app.add_middleware`, añade:

```python
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "FLEBITECH_CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]
```

Reemplaza la configuración CORS por:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

En `.env.example`, añade:

```env
FLEBITECH_CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

En Vercel debes reemplazar esos dominios por el dominio real del despliegue. No uses `*`.

## Paso 6. Añadir prueba de aislamiento

Agrega una prueba que:

1. inserte una pregunta en `session_a`;
2. inserte otra en `session_b`;
3. consulte recientes y brechas de `session_a`;
4. confirme que ningún resultado contiene información de `session_b`.

Ejemplo de aserción:

```python
recent_a = get_recent_interactions(limit=10, session_id="session_a")
assert all(row["session_id"] == "session_a" for row in recent_a)
assert not any("B_PRIVADO" in row["query"] for row in recent_a)
```

## Paso 7. Ejecutar validaciones

```bash
python -m compileall -q backend api
python test_flebitech.py
python test_conversacional.py
```

Prueba manual:

```text
GET /api/metrics?session_id=session_a
GET /api/metrics?session_id=session_b
GET /api/metrics?session_id=../../etc/passwd
```

La última debe responder 400 y las dos primeras nunca deben cruzar datos.

## Paso 8. Commit

```bash
git diff --check
git add backend/metrics.py api/index.py .env.example
git commit -m "fix: aislar metricas por sesion y restringir cors"
```

## Criterio de salida

- [ ] No hay datos cruzados entre sesiones cuando el usuario solo usa su propia sesión.
- [ ] Queda documentado que `session_id` no autoriza ni autentica.
- [ ] `/api/metrics` no devuelve `response` en el payload público.
- [ ] Si el endpoint sigue público, hay decisión explícita de aceptar el riesgo o plan para protegerlo.
- [ ] CORS no usa `*`.
- [ ] `allow_credentials` está desactivado.
- [ ] `session_id` está limitado y validado.
- [ ] El chat funciona si falla el registro de métricas.
