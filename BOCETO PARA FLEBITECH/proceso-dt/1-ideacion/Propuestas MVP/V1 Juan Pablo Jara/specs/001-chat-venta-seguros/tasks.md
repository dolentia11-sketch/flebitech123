# Tasks: Agente conversacional de venta automatizada de seguros ("Jarvis")

**Input**: spec.md v2, plan.md, research.md, data-model.md, contracts/
**Prerequisites**: dirección C→D validada en daily vie 24 9am · decisiones D3 (storage) y D4 (transporte) se cierran en el levantamiento de requisitos del motor (vie 24, equipo dev)

**Regla del equipo**: cada tarea = rama propia (`<nombre>/T###-descripcion-corta`) + PR a main. Nunca commit directo a main. JD gestiona merges.

**Sugerencia de dueño** entre `()` al final de cada tarea — se confirma en el daily; cualquiera puede tomar una tarea libre. Tareas con 🔒D3/D4 no arrancan hasta cerrar esa decisión (pero todo lo demás sí).

**Organización**: por user story, para que cada historia sea un incremento demostrable por sí solo (constitución V).

## Phase 1: Setup

**Purpose**: estructura del build en `producto/` y datos fuente listos

- [ ] T001 Crear estructura `producto/engines/{data,db,tests}` y `producto/demo/` con READMEs de una línea, según plan.md "Source Code" (JD)
- [ ] T002 [P] Copiar catálogo a `producto/engines/data/productos-seguros.json` desde `proceso-dt/1-ideacion/Propuestas MVP/V1 Juan Pablo Jara/catalogo-seguros/productos-seguros.json` (JP)
- [x] T003 [P] ~~Script one-shot que lee el Excel~~ → **invertida y hecha**: script `producto/engines/data/exportar_catalog.py` exporta `scoring_engine/catalog.py` (fuente de verdad validada por Melissa en la iteración 2) a `productos.csv`, `variables.csv`, `matriz_pesos.csv`, `triggers.csv`, `checklist.csv`, `fuentes.csv` (+ XLSX opcional con heat-map). Melissa/Caro auditan sobre esos archivos; ver `producto/engines/data/README.md` (Daniel)
- [ ] T004 [P] Crear `producto/engines/data/perfiles_demo.json`: 3 perfiles sintéticos por SERIE — (1) mujer 29 monoparental cat. A 1–1,5 SMLV, (2) hombre 24 soltero informal, (3) no afiliado — campos del contrato `score(perfil)` (JP)

## Phase 2: Foundational

**Purpose**: motor y DB que TODAS las historias necesitan. ⚠️ Bloquea las user stories.

- [ ] T005 `producto/engines/scoring_engine.py`: implementa `score(perfil) → ranking` leyendo `scoring_reglas.csv`, con `variables_usadas` como traza, según contrato motor-scoring.md op. 1 (Daniel)
- [ ] T006 [P] Evolucionar `producto/engines/quote_engine.py` (base: el de JD en `proceso-dt/.../V1 Juan Diego .../mvp/reto02-seguros/quote_engine.py`): `quote()` con veredictos apto/alternativa_asequible/asistida y umbral responsable por RANGO_SALARIAL, según contrato op. 2 (Sebas, pairing con JD)
- [ ] T007 [P] 🔒D3 Extender `schema_seguros.sql` → `producto/engines/db/schema_seguros.sql` con tablas de data-model.md (usuario_demo, score_resultado, cotizacion, poliza, evento_trazabilidad) + módulo `producto/engines/db.py` con `traza(evento)` (Daniel)
- [ ] T008 [P] Tests de casos dorados `producto/engines/tests/test_casos_dorados.py`: perfiles demo 1 y 2 → ranking y primas esperadas FIJAS (calculadas a mano contra el Excel con Melissa); correr con pytest (Melissa define esperados, Sebas escribe el test)
- [ ] T009 Validación async de Lizeth: revisar que `scoring_reglas.csv` + veredictos de T006 reflejan los requisitos que definió (afiliado/no afiliado, score core) — comentario en el PR, no requiere reunión (Lizeth)

**Checkpoint**: `pytest` verde = el cerebro funciona sin UI.

## Phase 3: User Story 1 — Compra de un seguro simple por chat (P1) 🎯 MVP

**Goal**: de "hola" a póliza COL-2026-XXXXX con hash, ≤5 preguntas, <3 min, 3 caminos (descubrimiento, intención, no afiliado).

**Independent Test**: quickstart.md caminos 1–3 + consulta de trazabilidad.

- [ ] T010 [P] [US1] `detectar_intencion(texto)` en `producto/engines/scoring_engine.py` + campo `sinonimos_intencion` en `productos-seguros.json` (26 productos), según contrato op. 3 y research D7 (Caro define sinónimos por producto, Daniel implementa)
- [ ] T011 [P] [US1] `emitir(cotizacion_id, consentimiento) → póliza` con número COL-2026-XXXXX + hash sha256 en `producto/engines/quote_engine.py`, según contrato op. 4 (Sebas)
- [ ] T012 [US1] 🔒D4 Transporte motor↔UI en `producto/engines/servidor.py` (o integración n8n, según decisión): expone las 5 operaciones del contrato (Daniel + Sebas)
- [ ] T013 [P] [US1] Chat UI `producto/demo/index.html` + `style.css`: look WhatsApp, paleta `producto/recursos-marca/` (fondo oscuro — no hay logo para fondo claro), burbujas, input, pantalla de precio limpia (prima grande + 1 CTA) y cierre celebratorio (JP)
- [ ] T014 [US1] Máquina de estados `producto/demo/app.js` según contracts/flujo-chat.md: paso 0 afiliado/no-afiliado → intención → descubrimiento p1–p5 (saltando pre-respondidas para afiliado) → oferta → precio → consentimiento → cierre; cada transición llama `traza()` (JP + Sebas)
- [ ] T015 [US1] Capa LLM: prompts de redacción por estado (valores del motor inyectados, prohibido calcular) + plantillas de fallback estáticas por estado + timeout 4s, sobre `gemini_prompts_seguros.md` de JD como base (JD)
- [ ] T016 [US1] Textos del chat en español simple revisados por la experta: una pregunta a la vez, sin jerga, consentimiento inline legible (Caro)
- [ ] T017 [US1] Lead de afiliación para no afiliados en el cierre (`lead_afiliacion` en traza + pantalla), según flujo-chat.md (JP)
- [ ] T018 [US1] Integración end-to-end de los 3 caminos del quickstart + fix de lo que aparezca (JP + Daniel)

**Checkpoint**: US1 demostrable en vivo — si solo esto existe el domingo, HAY DEMO.

## Phase 4: User Story 2 — Paquete sugerido post-compra (P2)

**Goal**: pantalla final ofrece 2–3 complementarias con total mensual único simulado.

**Independent Test**: quickstart — paquete distinto para perfil 1 vs. perfil 2; ignorarlo no rompe el cierre.

- [ ] T019 [P] [US2] `paquete(serie, poliza) → complementarias` en `producto/engines/scoring_engine.py`: toma el ranking del score, excluye lo comprado, arma 2–3 + total (Melissa define reglas de compatibilidad, Daniel implementa)
- [ ] T020 [US2] Pantalla de paquete en `producto/demo/app.js` + textos de Caro; opcional, no bloquea cierre; escribe `paquete` en traza (JP)

## Phase 5: User Story 3 — Venta asistida + abandono como señal (P3)

**Goal**: productos rigurosos derivan a humano; todo abandono queda registrado con punto de fuga.

**Independent Test**: quickstart "Validación P3".

- [ ] T021 [P] [US3] Clasificar los 26 productos como `automatica`/`asistida` en `productos-seguros.json` con criterio de rigurosidad documentado en el mismo JSON (Caro)
- [ ] T022 [US3] Estado `derivacion` en `producto/demo/app.js` + regla en `emitir()` (falla si asistida sin derivación ofrecida), según contratos (Sebas)
- [ ] T023 [US3] Registro de abandono: listener de cierre/inactividad en `producto/demo/app.js` → `traza(abandono)` con punto de fuga (JP)

## Track Pitch — corre en PARALELO desde el viernes (dueño: JP)

**Purpose**: el pitch no se hace a última hora. Narrativa: la infraestructura es el
producto; Jarvis es la primera feature; misma infraestructura → cualquier interfaz,
a la escala y velocidad que Colsubsidio necesite (SC-006). Jurado: Colsubsidio + 30X.

- [ ] T028 [P] VIERNES: esqueleto narrativo del pitch en `producto/demo/PITCH.md` — problema (0,24% venta electrónica, 90,7% hogares sin seguro) → tesis de infraestructura → demo → flywheel/forma de X → camino a producción (9 capas) → cifras de la investigación con fuente (JP)
- [ ] T029 [P] SÁBADO: materiales del pitch — deck o soporte visual con paleta `producto/recursos-marca/`, diagrama interfaz-intercambiable (motor por contrato → chat/WhatsApp/wallet/marketplace), y revisión del video de referencia que recomendó JD (JP, input de JD)
- [ ] T030 SÁBADO noche: ensayo 1 del pitch contra el demo real (cronometrado, 3 min) + ajustes; DOMINGO mañana: ensayo final con el equipo (JP + todos)

## Phase 6: Polish & Demo

- [ ] T024 [P] Guion del demo de 3 min sobre los 3 caminos + consulta de trazabilidad en vivo ante el jurado (SC-002/SC-003) en `producto/demo/GUION.md` — se integra al PITCH.md de T028 (JP + JD)
- [ ] T025 [P] Barrido de PII: grep de nombres/datos reales en `producto/`, DB y logs (SC-004) (JP)
- [ ] T026 Prueba de fuego: correr demo completo SIN API key del LLM (solo plantillas) — constitución I (Daniel)
- [ ] T027 /speckit-analyze (consistencia spec/plan/tasks) el sábado al cierre + /speckit-converge antes de congelar el domingo (JP)

## Dependencies

- Phase 1 → Phase 2 → US1 (T010–T018) → US2/US3 (independientes entre sí) → Polish
- 🔒D3 bloquea T007; 🔒D4 bloquea T012 — todo lo demás de Phases 1–2 arranca YA tras el daily
- T005+T006 bloquean T008; T012+T014 bloquean T018

## Parallel Example (viernes por la mañana, tras el daily)

```
Daniel:  T003 → T005          Sebas: T006          Melissa: valida T003, define T008
JP:      T002, T004 → T013    Caro:  sinónimos T010, textos T016    JD: T001 → T015
```

## Implementation Strategy

MVP = solo US1 (T001–T018). US2 cuesta media jornada si US1 corre. US3 es narrable
aunque quede mínima. El track de pitch (T028–T030) corre en paralelo desde el
viernes — el pitch NO se hace el domingo; el domingo solo se ensaya. Sábado al
cierre: auditoría (T027-analyze). Domingo: pulir + ensayar, cero features nuevas.

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24 · pendiente validación en daily 9am*
