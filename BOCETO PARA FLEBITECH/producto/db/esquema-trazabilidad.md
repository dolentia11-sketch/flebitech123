# DB de trazabilidad — esquema unificado v1

**Dueño:** Daniel · **Escriben:** motor (Sebas) vía `log_interaction()` + Make (orquestación)
· **Leen:** pantalla "esto aprendió el sistema" (JP) + export de entrenamiento futuro.

Acordado 25-jul (hilo JP↔Sebas + daily): **una sola DB para todo el equipo.**
Motor de almacenamiento: **SQLite** (`interactions.db`) como fuente de verdad
(spec H0.4: cero infraestructura, la consulta de trazabilidad ante el jurado es un
comando). Si la escritura directa desde Make se complica, puente CSV en Drive y se
consolida a SQLite — la ESTRUCTURA no cambia.

## Principio (de la propuesta de Sebas)

Guardar SIEMPRE dos cosas separadas: el **texto original** del usuario y la
**versión estructurada** que usa el motor. Permite auditar, mejorar el parser y
reentrenar después con mejor feature engineering. Hoy: reglas + logging. Mañana:
dataset. Después: modelo offline. Nunca ML en línea, nunca tokens para aprender.

## Tablas

### `sessions` — una fila por conversación
| Campo | Tipo | Nota |
|---|---|---|
| session_id | TEXT PK | UUID |
| started_at / ended_at | TEXT ISO | |
| canal | TEXT | `web` (MVP) · `whatsapp` (visión) |
| origen | TEXT | campaña / QR / referido / directo |
| afiliado | INTEGER 0/1 | rama de la bifurcación |
| id_hash | TEXT | SHA-256 de la cédula si se capturó — NUNCA en claro (Ley 1581) |
| consent_datos | INTEGER 0/1 + ts en events | habeas data — paso propio del flujo |
| consent_compra | INTEGER 0/1 | checkbox producto + prima antes de cerrar |
| estado_final | TEXT | `cerrada` · `abandonada` · `handoff_asesor` · `activa` |
| producto_cerrado | TEXT | id del catálogo, si aplica |
| paso_abandono | TEXT | en qué paso se fue (el abandono es señal — H8.2) |
| aseguradora_id | TEXT | id de la aseguradora del convenio a la que se remitió el lead (discovery 25-jul: en prod el cierre real es la remisión, no la venta directa) |

### `events` — todo lo que pasa, en orden
| Campo | Tipo | Nota |
|---|---|---|
| event_id | INTEGER PK AUTOINCREMENT | |
| session_id | TEXT FK | |
| ts | TEXT ISO | |
| tipo | TEXT | `pregunta` · `respuesta` · `consulta_crm` · `recomendacion` · `consentimiento` · `ajuste` · `cierre` · `handoff` · `abandono` · `respaldo` |
| actor | TEXT | `usuario` · `llm` · `motor` · `make` |
| contenido_raw | TEXT | texto original tal cual |
| contenido_estructurado | TEXT JSON | la lectura del sistema |

### `features` — las 11 variables del perfil (V1–V11)
| Campo | Tipo | Nota |
|---|---|---|
| session_id | TEXT FK | |
| variable | TEXT | `V1`…`V11` (según README del motor) |
| valor | TEXT | |
| fuente | TEXT | `pregunta` · `precarga_crm` · `inferencia` — clave: máx 5 preguntas efectivas (FR-001) |
| ts | TEXT ISO | |

### `outputs` — lo que dijo el motor (y por qué)
| Campo | Tipo | Nota |
|---|---|---|
| output_id | INTEGER PK | |
| session_id | TEXT FK | |
| ts | TEXT ISO | |
| motor_version | TEXT | todo output declara su versión |
| producto_id | TEXT | del catálogo |
| score / pct_afinidad / rank | REAL / REAL / INTEGER | |
| modo_cierre | TEXT | `auto` · `asesor` |
| porque | TEXT | la variable que justifica (H5.1) |

### `labels` — el target que fabrica el flywheel
| Campo | Tipo | Nota |
|---|---|---|
| session_id | TEXT FK | |
| label | TEXT | `compro` · `abandono` · `handoff` · `no_elegible` · `remitido_aseguradora` (discovery 25-jul: cierre real en producción) |
| producto_id | TEXT | |
| ts | TEXT ISO | |

## Identificación (insight de Emmy, 25-jul)

Colsubsidio usa **Salesforce como CRM**. En producción: el número de WhatsApp se
cruza con el CRM al entrar y de ahí arranca el flujo. En el MVP (chat web): el
flujo de Caro ya lo emula — cédula del afiliado → **consulta al "CRM simulado"**
→ devuelve nombre/edad/género/ocupación/ciudad → solo el nombre se usa en la
conversación, el resto entra a `features` como `precarga_crm`. Nómbrenlo así:
la caja del diagrama "consulta simulada" ES el Salesforce de la visión.

## Sesión dorada (para probar la integración ANTES de las 3pm)

1 sesión de ejemplo con: afiliado=1, consulta_crm, 3 preguntas, 11 features
(mezcla de fuentes), 1 recomendación top-3 en `outputs`, consentimiento,
cierre con label `compro`. Si esa sesión se escribe y se lee completa, la
integración de las 5pm está asegurada.

## Regla de oro

Cero PII en claro (hash siempre) · el LLM nunca escribe cifras en `outputs`
(solo el motor) · todo artefacto declara versión.

---
Construido con Claude Fable 5 (sesión central del sábado) · 2026-07-25.
