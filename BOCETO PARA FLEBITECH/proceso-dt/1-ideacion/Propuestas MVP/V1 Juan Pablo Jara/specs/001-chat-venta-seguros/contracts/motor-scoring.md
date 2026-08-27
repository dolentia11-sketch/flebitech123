# Contrato — Motor de scoring y cotización

Contrato independiente del transporte (función Python, endpoint HTTP o nodo n8n —
decisión D4 abierta). La UI y el LLM consumen esto; nunca calculan.

## Operación 1 · `score(perfil) → ranking`

**Entrada** (perfil, campos del modelo de Caro/Melissa/Lizeth):
```json
{
  "serie": "DEMO-00123",
  "es_afiliado": true,
  "rango_edad": "26-35 años",
  "genero": "Femenino",
  "situacion_laboral": "Informal / cuenta propia",
  "rango_salarial": "Bajo (< $1.3M)",
  "composicion_familiar": "Con hijos menores de edad"
}
```

**Salida**:
```json
{
  "ranking": [
    {"producto_id": "vida", "familia": "Vida", "puntaje": 21, "tipo_venta": "automatica"},
    {"producto_id": "exequial", "puntaje": 17, "tipo_venta": "automatica"},
    {"producto_id": "educacion", "puntaje": 15, "tipo_venta": "asistida"}
  ],
  "variables_usadas": ["V1|26-35 años", "V2|Femenino", "V3|Informal", "V4|Bajo", "V5|Con hijos"],
  "score_id": 42
}
```

Reglas: puntajes = suma de pesos de `scoring_reglas.csv` (exportado del Excel).
Determinista: mismo perfil → mismo ranking, siempre. `variables_usadas` es la
traza de explicabilidad (SC-003).

## Operación 2 · `quote(serie, producto_id, presupuesto_mensual) → cotización`

**Salida**:
```json
{
  "producto_id": "vida",
  "prima": 18000,
  "cobertura": 50000000,
  "veredicto": "apto",
  "explicacion_variables": {"presupuesto": 50000, "umbral_responsable": 45000},
  "cotizacion_id": 77
}
```

Veredictos: `apto` | `alternativa_asequible` (devuelve además `alternativa` con el
producto sugerido — nunca fuerza el caro, spec US1-6) | `asistida` (requiere
ofrecer derivación antes de emitir).

## Operación 3 · `detectar_intencion(texto) → producto | null`

Matching contra `sinonimos_intencion` del catálogo (D7). Devuelve `null` si no hay
match con confianza → la UI enruta a descubrimiento. Nunca devuelve un producto
fuera del catálogo.

## Operación 4 · `emitir(cotizacion_id, consentimiento_texto) → póliza`

**Salida**: `{"numero": "COL-2026-00042", "hash": "sha256…", "timestamp": "…"}`.
Falla (error explícito) si la cotización tiene veredicto `asistida` sin derivación
ofrecida, o si falta consentimiento.

## Operación 5 · `traza(evento)` — fire-and-forget

Todo paso de la UI la llama: `{serie, paso, dato}`. Incluye `abandono` y
`lead_afiliacion`.

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24*
