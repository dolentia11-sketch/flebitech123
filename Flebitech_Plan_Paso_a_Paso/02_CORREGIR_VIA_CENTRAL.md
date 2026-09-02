# Etapa 2 — Corregir la respuesta sobre vía central

## Problema exacto

`backend/response_builder.py` selecciona todo medicamento cuya descripción contiene la palabra `central`. Por eso la pregunta “¿Qué medicamentos requieren vía central obligatoria?” mezcla:

- vía central exclusiva;
- vía central condicionada;
- vía central opcional;
- vía periférica válida.

La corrección debe conservar el RAG, el orquestador y el resto de respuestas.

## Archivos autorizados

- `knowledge_base/medicamentos.json`
- `backend/rag_engine.py`
- `backend/response_builder.py`
- `test_conversacional.py`

No modifiques `orchestrator.py` ni `groq_client.py` en esta etapa.

## Paso 1. Crear primero una prueba que falle

En `test_conversacional.py`, reemplaza la prueba actual “Filtro farmacológico de vía central” por:

```python
central_response = check(
    "Vía central exclusivamente obligatoria",
    "¿Qué medicamentos requieren vía central obligatoria?",
    ("nutrición parenteral total", "exclusivamente vía central"),
    forbidden=(
        "| Vancomicina |",
        "| Ciprofloxacina |",
        "| Furosemida |",
        "| Gluconato de Calcio",
    ),
)

check(
    "Vía central condicionada",
    "¿Qué medicamentos pueden requerir vía central según concentración o duración?",
    ("cloruro de potasio", "amiodarona", "condicionada"),
    forbidden=("exclusivamente vía central (cvc o picc",),
)
```

Ejecuta:

```bash
python test_conversacional.py
```

La primera ejecución debe fallar. Esa falla confirma que la prueba detecta el defecto.

## Paso 2. Añadir clasificación estructurada a medicamentos

En cada objeto de `knowledge_base/medicamentos.json`, añade estos campos sin borrar los existentes:

```json
"tipo_via_central": "pendiente_revision",
"criterio_via_central": "",
"fuente_via_central": ""
```

Valores permitidos:

```text
exclusiva
condicionada
opcional
no_aplica
pendiente_revision
```

Clasificación provisional basada únicamente en el texto actual —debe aprobarla farmacia/enfermería antes del merge—:

| Medicamento | Clasificación provisional |
|---|---|
| Nutrición Parenteral Total | `exclusiva` |
| KCl | `condicionada` |
| Amiodarona | `condicionada` |
| Vancomicina | `condicionada` |
| DAD 50% | `condicionada` o `opcional`, según revisión institucional |
| Los demás | Definir desde protocolo; no inferir automáticamente |

No uses la tabla provisional como validación clínica final.

Ejemplo para NPT:

```json
"tipo_via_central": "exclusiva",
"criterio_via_central": "EXCLUSIVAMENTE vía central (CVC o PICC con punta central)",
"fuente_via_central": "PENDIENTE: referencia institucional validada"
```

Ejemplo para KCl:

```json
"tipo_via_central": "condicionada",
"criterio_via_central": "Requiere vía central cuando supera la concentración periférica permitida por el protocolo institucional",
"fuente_via_central": "PENDIENTE: referencia institucional validada"
```

## Paso 3. Incorporar los campos al contexto del RAG

En `backend/rag_engine.py`, dentro de la construcción de `content`, inmediatamente después de `Vía Recomendada`, añade:

```python
f"- Tipo de Vía Central: {med.get('tipo_via_central', 'pendiente_revision')}\n"
f"- Criterio de Vía Central: {med.get('criterio_via_central', '')}\n"
f"- Fuente de Vía Central: {med.get('fuente_via_central', '')}\n"
```

No cambies el ranking, los alias ni los chunks.

## Paso 4. Permitir que el fallback lea esos campos

En `backend/response_builder.py`, agrega al `field_map` de `_medication_record()`:

```python
"tipo de via central": "Tipo de vía central",
"criterio de via central": "Criterio de vía central",
"fuente de via central": "Fuente de vía central",
```

## Paso 5. Sustituir solo el bloque vulnerable

Dentro de `_medication_collection_response()`, sustituye el bloque que comienza con:

```python
if "via central" in text or "central obligatoria" in text ...
```

por:

```python
asks_exclusive = any(term in text for term in (
    "central obligatoria", "central obligatorio", "exclusivamente central",
    "via central exclusiva", "requieren via central",
))
asks_conditional = any(term in text for term in (
    "pueden requerir", "segun concentracion", "segun duración",
    "segun duracion", "central condicionada",
))

if "via central" in text or asks_exclusive or asks_conditional:
    if asks_exclusive:
        selected = [
            record for record in records
            if _plain(record.get("Tipo de vía central", "")) == "exclusiva"
        ]
        title = "## Medicamentos con vía central exclusiva"
        note = (
            "Se incluyen únicamente fichas clasificadas en la base local como de vía central exclusiva. "
            "La validación clínica institucional sigue pendiente si la fuente de vía central no está aprobada."
        )
    elif asks_conditional:
        selected = [
            record for record in records
            if _plain(record.get("Tipo de vía central", "")) == "condicionada"
        ]
        title = "## Medicamentos con vía central condicionada"
        note = "La indicación depende del criterio documentado de concentración, duración u otra condición clínica."
    else:
        selected = [
            record for record in records
            if _plain(record.get("Tipo de vía central", "")) in {"exclusiva", "condicionada", "opcional"}
        ]
        title = "## Uso documentado de vía central"
        note = "La tabla diferencia el tipo de indicación; no todas las opciones son obligatorias."

    if selected:
        rows = "\n".join(
            f"| {record['nombre']} | {record.get('Tipo de vía central', '')} | "
            f"{record.get('Criterio de vía central', record.get('Vía recomendada', ''))} |"
            for record in selected
        )
        return (
            f"{title}\n\n{note}\n\n"
            "| Medicamento | Clasificación | Criterio documentado |\n"
            "|---|---|---|\n"
            f"{rows}{_source_line(sources)}"
        )
```

## Paso 6. Validar JSON y ejecutar pruebas

```bash
python -m json.tool knowledge_base/medicamentos.json > NUL
```

En macOS/Linux usa:

```bash
python -m json.tool knowledge_base/medicamentos.json > /dev/null
```

Después:

```bash
python -m compileall -q backend
python test_conversacional.py
python test_orchestrator.py
```

## Paso 7. Prueba manual obligatoria

Comprueba estas preguntas:

```text
¿Qué medicamentos requieren vía central obligatoria?
¿Qué medicamentos pueden requerir vía central según concentración?
¿Puedo pasar vancomicina por vía periférica?
¿La NPT puede administrarse por vía periférica?
```

No apruebes si la primera respuesta incluye medicamentos condicionados como si fueran exclusivos.

## Paso 8. Commit aislado

```bash
git diff --check
git diff
git add knowledge_base/medicamentos.json backend/rag_engine.py backend/response_builder.py test_conversacional.py
git commit -m "fix: clasificar indicacion de via central sin ambiguedad"
```

## Criterio de salida

- [ ] Existe una prueba negativa.
- [ ] Solo aparecen medicamentos exclusivos en la pregunta “obligatoria”.
- [ ] Ningún registro `pendiente_revision` se presenta como recomendación.
- [ ] Ninguna respuesta visible usa “validada” mientras `fuente_via_central` diga `PENDIENTE`.
- [ ] La clasificación fue revisada clínicamente con fuente, versión, fecha y aprobador.
- [ ] Las pruebas anteriores continúan verdes.
