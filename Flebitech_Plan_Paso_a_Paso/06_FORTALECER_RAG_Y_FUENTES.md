# Etapa 6 — Fortalecer el RAG y las fuentes clínicas

## Objetivo

Mejorar la trazabilidad y permitir que la base crezca sin sustituir `RAGEngine`.

## Regla clínica

No edites pH, osmolaridad, dilución, velocidad, vía o conducta sin una fuente institucional/científica verificable y aprobación profesional.

## Paso 1. Crear rama

```bash
git switch master
git pull --ff-only
git switch -c docs/clinical-provenance
```

## Paso 2. Definir metadatos compatibles

Añade un objeto `evidencia` a cada medicamento; no borres campos actuales:

```json
"evidencia": {
  "titulo": "",
  "organizacion_autor": "",
  "version_edicion": "",
  "fecha_publicacion": "",
  "url_doi": "",
  "fecha_revision": "",
  "responsable_revision": "",
  "estado": "pendiente_revision"
}
```

Estados permitidos:

```text
pendiente_revision
validado
retirado
```

Un registro pendiente puede recuperarse para revisión, pero no debe presentarse como recomendación clínica definitiva.

## Paso 3. Validar estructura al indexar

En `RAGEngine`, añade una función pequeña de validación; no reemplaces el indexador:

```python
REQUIRED_MEDICATION_FIELDS = {
    "nombre", "ph", "osmolaridad", "via_recomendada",
    "riesgo_flebitis", "diluyente_recomendado",
    "tiempo_infusion_minimo", "observaciones_enfermeria",
}


def _validate_medication_record(record: dict) -> list:
    return sorted(field for field in REQUIRED_MEDICATION_FIELDS if not record.get(field))
```

Durante indexación, si faltan campos, registra un aviso claro y no conviertas el registro incompleto en ficha activa. No hagas `except Exception: pass` silencioso.

## Paso 4. Añadir identificación del fragmento

Conserva el formato actual y añade a cada chunk:

```python
"evidence_status": med.get("evidencia", {}).get("estado", "pendiente_revision"),
"source_version": med.get("evidencia", {}).get("version_edicion", ""),
```

No cambies el algoritmo BM25 en este PR.

## Paso 5. Crear conjunto dorado

Crea `tests/data/golden_queries.json`:

```json
[
  {
    "id": "med_vancomycin_ph",
    "query": "pH de vancomicina",
    "expected_sources": ["medicamentos.json"],
    "required_terms": ["2.5 - 4.5"],
    "forbidden_terms": ["amiodarona"]
  },
  {
    "id": "ood_capital",
    "query": "capital de Francia",
    "expected_had_answer": false,
    "required_terms": ["no especifica"]
  }
]
```

Amplía gradualmente con preguntas reales anonimizadas y revisadas.

## Paso 6. Medir recuperación

Para cada caso registra:

- entidad esperada;
- fuente esperada;
- chunk superior;
- `had_answer` esperado;
- términos obligatorios y prohibidos.

Métricas mínimas:

- precisión de entidad;
- precisión@3 de fuente;
- falsos positivos fuera de dominio;
- mezcla de medicamentos;
- fallos de continuidad.

## Paso 7. Ajustar alias solo con prueba

Para cada alias nuevo:

1. agrega prueba positiva;
2. agrega una palabra similar que no debe coincidir;
3. ejecuta el conjunto dorado;
4. cambia `MED_ALIASES` o fuzzy matching;
5. compara métricas antes/después.

No disminuyas globalmente el umbral fuzzy para resolver un solo error.

## Paso 8. Validar

```bash
python -m json.tool knowledge_base/medicamentos.json > /dev/null
python indexer.py
pytest -q tests/test_rag.py tests/test_medications.py
python test_conversacional.py
```

En Windows sustituye `/dev/null` por `NUL`.

## Criterio de salida

- [ ] Cada dato crítico tiene metadatos de evidencia.
- [ ] Los registros incompletos se detectan automáticamente.
- [ ] Existe un conjunto dorado versionado.
- [ ] Los cambios de alias se justifican con métricas.
- [ ] El RAG actual se conserva.

