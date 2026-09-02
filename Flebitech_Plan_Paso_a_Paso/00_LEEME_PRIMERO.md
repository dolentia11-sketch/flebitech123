# Flebitech — Plan de implementación paso a paso

**Repositorio objetivo:** `dolentia11-sketch/flebitech_bot`  
**Punto de partida auditado:** `master`, commit `21502c1`  
**Propósito:** corregir vulnerabilidades y mejorar el chatbot de forma incremental, sin reemplazar su arquitectura, contratos principales ni lógica clínica.

## Qué contiene este paquete

Cada guía corresponde a una etapa independiente:

1. `01_PREPARAR_LINEA_BASE.md`: preparar el proyecto y congelar el comportamiento actual.
2. `02_CORREGIR_VIA_CENTRAL.md`: corregir la clasificación clínica más urgente.
3. `03_PROTEGER_METRICAS_Y_CORS.md`: impedir cruces de información entre sesiones.
4. `04_BLOQUEAR_PROMPT_INJECTION_Y_XSS.md`: validar historial y sanear respuestas.
5. `05_PRUEBAS_AUTOMATICAS_Y_CI.md`: crear una barrera automática contra regresiones.
6. `06_FORTALECER_RAG_Y_FUENTES.md`: mejorar trazabilidad y crecimiento de la base.
7. `07_MEJORAR_MOTOR_CONVERSACIONAL.md`: elevar memoria, precisión y naturalidad.
8. `08_LIMPIEZA_DESPLIEGUE_Y_LIBERACION.md`: limpiar el repositorio y publicar con control.

## Arquitectura que se conserva

No se reemplazan ni se rediseñan:

- `backend/orchestrator.py` como coordinador.
- `backend/rag_engine.py` como recuperación local.
- `backend/groq_client.py` como acceso a Groq.
- `backend/response_builder.py` como fallback determinista.
- `backend/prompt_system.py` como sistema de routing y prompts.
- FastAPI, Streamlit, Vercel y la interfaz estática.
- El contrato principal de `/api/chat`.

## Regla de trabajo

No ejecutes todas las guías el mismo día ni en una sola rama. El orden correcto es:

```text
Crear rama → agregar prueba que detecta el fallo → aplicar cambio mínimo
→ ejecutar pruebas → revisar respuesta manual → hacer commit → desplegar preview
→ aprobar → fusionar → continuar con la siguiente guía
```

## Requisitos antes de comenzar

- Tener Git instalado.
- Tener Python 3.11 recomendado.
- Poder clonar y crear ramas en GitHub.
- No usar datos reales de pacientes en pruebas.
- Tener revisión de farmacia/enfermería para cambios clínicos.

## Comandos que se repiten en todas las etapas

Desde la raíz del repositorio:

```bash
git status
python -m compileall -q backend api
python test_conversacional.py
python test_orchestrator.py
```

Si cualquiera falla, no continúes ni hagas merge.

## Evidencia mínima por etapa

Cada etapa debe cerrar con:

- prueba automatizada que cubra el defecto observado;
- prueba manual de la superficie visible afectada;
- captura o enlace del run de CI cuando aplique;
- lista explícita de riesgos residuales;
- aprobación clínica documentada cuando toque vía, dilución, indicación o conducta.

No uses “validado”, “sin errores” o “cerrado” si la etapa solo mitigó el defecto técnico y aún depende de revisión clínica, identidad/autorización, CSP/SRI, política de retención o protección de rama.

## Criterio para pasar a la siguiente etapa

Solo avanza cuando:

- la prueba nueva pasa;
- las pruebas anteriores siguen pasando;
- el cambio está limitado a los archivos autorizados;
- se revisó el resultado manualmente;
- existe un commit pequeño que puede revertirse;
- los cambios clínicos tienen aprobación profesional documentada.

## Orden de prioridad

| Etapa | Riesgo que resuelve | Prioridad |
|---|---|---|
| 1 | No tener una línea base reproducible | Obligatoria |
| 2 | Clasificación clínica ambigua de vía central | Crítica |
| 3 | Exposición de métricas y CORS abierto | Crítica |
| 4 | Prompt injection y XSS | Crítica |
| 5 | Ausencia de CI confiable | Alta |
| 6 | Fuentes clínicas sin trazabilidad | Alta |
| 7 | Calidad conversacional y evaluación | Media |
| 8 | Repositorio pesado y liberación | Media |

Empieza únicamente por `01_PREPARAR_LINEA_BASE.md`.

La consolidación de hallazgos actualizada vive en `docs/ENDURECIMIENTO_ETAPAS.md`.
