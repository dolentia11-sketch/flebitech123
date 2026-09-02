# Etapa 7 — Mejorar el motor conversacional sin reescribirlo

## Objetivo

Hacer el chat más preciso, natural y consistente preservando `ConversationalOrchestrator`, los intents y el fallback local.

## Restricción

Cada mejora debe corresponder a un fallo demostrado por una conversación de prueba. No se agregan reglas por intuición.

## Paso 1. Crear banco de conversaciones

Crea `tests/data/conversations.json` con casos de varios turnos:

```json
[
  {
    "id": "medication_followup",
    "turns": [
      {"query": "pH de vancomicina", "required": ["2.5 - 4.5"]},
      {"query": "¿Y la dilución?", "required": ["5 mg/ml"], "forbidden": ["amiodarona"]},
      {"query": "¿Y amiodarona?", "required": ["amiodarona"], "forbidden": ["síndrome del hombre rojo"]}
    ]
  }
]
```

Añade estos grupos:

- continuación de medicamento;
- cambio explícito de entidad;
- comparación de dos fármacos;
- escala y grado contextual;
- pregunta ambigua;
- negación;
- corrección del usuario;
- consulta fuera de dominio después de un tema clínico.

## Paso 2. Medir routing determinista

Prueba directamente `deterministic_route()` con:

- intent esperado;
- profundidad esperada;
- `is_continuation` esperado;
- contenido mínimo de `rewritten_query`.

Corrige solo la rama de decisión que falla. No reordenes todas las intenciones en un mismo PR.

## Paso 3. Mejorar negaciones

Agrega detección explícita de palabras como:

```text
no
nunca
excepto
sin
cuáles no
contraindicado
```

La negación debe viajar como parte de la consulta reescrita y llegar al constructor local. Añade primero pruebas como:

```text
¿Qué medicamentos NO requieren vía central?
¿Cuál no se diluye con SSN?
```

## Paso 4. Controlar memoria

Mantén la ventana actual de historial. Añade estas reglas puntuales:

- el medicamento mencionado en el turno actual tiene prioridad;
- una comparación conserva exactamente dos entidades;
- una pregunta fuera de dominio no hereda automáticamente una entidad clínica;
- si dos entidades previas son plausibles, se pide una aclaración breve;
- no se copia una respuesta completa dentro de la consulta del RAG.

## Paso 5. Definir respuesta parcial correctamente

Actualmente una respuesta no vacía puede terminar con `had_answer=true`. Añade pruebas para distinguir:

- respuesta completa;
- respuesta parcial;
- brecha documental;
- fuera de dominio.

Sin cambiar todavía el contrato público, una respuesta parcial debe decir exactamente qué dato sí existe y cuál falta. No debe presentarse como certeza total.

## Paso 6. Comparar Groq y fallback

Para datos críticos —pH, vía, dilución, tiempo, riesgo y conducta— valida que la respuesta Groq contenga valores presentes en el contexto. Si no pasa la validación, usa `build_local_response()`.

Hazlo mediante una función auxiliar pequeña dentro del flujo actual; no agregues un segundo orquestador.

Casos:

```text
El LLM cambia 2.5–4.5 por 5.5 → rechazar y usar fallback.
El LLM mezcla vancomicina y amiodarona → rechazar.
El LLM omite la fuente → limpiar/agregar fuente, sin inventarla.
```

## Paso 7. Mejorar el tono con criterios medibles

La respuesta debe:

- comenzar con el dato solicitado;
- evitar repetir la pregunta;
- no cerrar con una oferta genérica;
- usar tabla solo en listas/comparaciones;
- conservar advertencias clínicas necesarias;
- citar fuente real al final.

No evalúes calidad solo con “me gusta”. Usa términos requeridos, prohibidos, longitud máxima por nivel y revisión humana ciega.

## Paso 8. Métricas de aceptación

| Métrica | Meta inicial |
|---|---:|
| Entidad correcta | 100% en medicamentos críticos |
| Continuidad correcta | ≥95% en conjunto dorado |
| Mezcla de medicamentos | 0 casos |
| Fuera de dominio aceptado | <2% |
| Datos críticos alterados por LLM | 0 casos |
| Pruebas heredadas | 100% verdes |

## Paso 9. Implementar por micro-PR

Orden recomendado:

1. negaciones;
2. ambigüedad;
3. continuidad larga;
4. validación factual del LLM;
5. estilo y concisión.

Cada punto debe ser una rama y un PR independiente.

## Criterio de salida

- [ ] Cada regla nueva tiene un caso que antes fallaba.
- [ ] No se mezclan medicamentos.
- [ ] Groq no puede alterar datos críticos recuperados.
- [ ] El fallback mantiene la misma funcionalidad.
- [ ] El orquestador sigue siendo único.

