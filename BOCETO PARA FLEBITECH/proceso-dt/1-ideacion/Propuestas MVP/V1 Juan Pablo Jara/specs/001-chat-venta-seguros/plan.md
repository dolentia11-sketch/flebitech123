# Implementation Plan: Agente conversacional de venta automatizada de seguros ("Jarvis")

**Branch**: `001-chat-venta-seguros` (trabajo real en ramas `*/tarea-*` + PR) | **Date**: 2026-07-24 | **Spec**: [spec.md](./spec.md)

**Input**: Spec v2 (dirección C→D de la matriz + bifurcaciones afiliado/no-afiliado e intención + score como core)

## Summary

Chat web que simula WhatsApp lleva al usuario de "quiero un seguro" (o "no sé qué
necesito") a póliza emitida con número y hash, en ≤5 preguntas y <3 minutos. El
cerebro es el **motor determinista de scoring** (Python) que ejecuta las reglas del
Excel de Caro/Melissa/Lizeth (`Motor_Scoring_Seguros_Colsubsidio.xlsx`: variables
V1–V7 + matriz de pesos por 7 familias); el LLM solo conversa y explica. Todo evento
(respuesta, oferta, abandono, lead) escribe en una DB única de trazabilidad.

**Punto de partida real (no de cero):**
- `quote_engine.py` de JD (motor standalone, catálogo parametrizable, corre con stdlib) → base del motor.
- `Motor_Scoring_Seguros_Colsubsidio.xlsx` → fuente de reglas del score (se exporta a datos, no se re-tipea en código).
- `schema_seguros.sql` de JD → base del esquema de DB.
- `catalogo-seguros/productos-seguros.json` (26 productos, 7 familias) → catálogo.
- `producto/` (demo/, engines/) → donde vive el build.

## Technical Context

**Language/Version**: Python 3.11+ (motor, ya existente); HTML/CSS/JS para el chat web (sin framework pesado, demo primero)

**Primary Dependencies**: Motor: stdlib + `openpyxl`/export CSV (una sola vez, para extraer reglas del Excel). Chat: LLM del equipo (Gemini) SOLO para redactar; el flujo funciona con textos de plantilla si el LLM falla (constitución I). **DECISIÓN ABIERTA → levantamiento de requisitos vie 24 (equipo dev)**: servir el motor como (a) API local FastAPI/Flask, (b) función llamada desde n8n, o (c) backend simple integrado al chat. Recomendación: (c) o (a) — lo que menos fricción dé al demo.

**Storage**: **DECISIÓN ABIERTA**. Recomendación: SQLite (cero infraestructura, archivo único, enseñable en demo, `schema_seguros.sql` compatible). Alternativa: Postgres si el equipo dev ya tiene uno montado. Lo NO negociable: una sola DB, un solo esquema (FR-008).

**Testing**: pytest para el motor (casos dorados: 2 perfiles demo con resultados esperados fijos); prueba manual guiada por `quickstart.md` para el flujo completo.

**Target Platform**: navegador (desktop + móvil responsive); corre local para el demo (sin dependencia de internet salvo el LLM, con fallback a plantillas)

**Project Type**: web app pequeña (chat UI + motor backend + DB)

**Performance Goals**: respuesta del motor <1s; flujo completo <3 min (SC-002); demo sin cortes ≥60s

**Constraints**: cero PII (constitución III); cifras solo del motor (constitución I); sin integraciones reales de pago/aseguradoras (brief); valores enmascarados de la base v2 se usan sin interpretar (constitución IV)

**Scale/Scope**: demo de jurado: 2–3 perfiles sintéticos, 26 productos, 1 pantalla de chat + pantalla de cierre. No es producción.

## Constitution Check

*GATE: evaluado contra constitución v1.0.0 (pendiente ratificación del equipo — gobernanza: aprueba JD).*

| Principio | Cumplimiento en este plan |
|---|---|
| I · Motor determinista manda cifras | ✅ Toda prima/score sale del motor Python; LLM redacta sobre valores ya calculados; fallback a plantillas si LLM falla |
| II · Cumplimiento embebido | ✅ Idoneidad + consentimiento inline + póliza con hash son parte del flujo P1, no adorno |
| III · Cero PII | ✅ Perfiles sintéticos por SERIE; base oficial fuera del repo; DB solo guarda SERIE/lead sintético |
| IV · Valores enmascarados sin interpretar | ✅ El score usa las bandas legibles (RANGO_SALARIAL, RANGO_EDAD, GENERO) + valores enmascarados como features opacas; ninguna etiqueta inferida en UI ni pitch |
| V · Demo primero | ✅ Fases del plan = P1 → P2 → P3; no se arranca P2 sin P1 end-to-end |
| VI · Escrito o no existe | ✅ Este plan + tasks.md; desviaciones → primero se actualiza la spec |

**Post-diseño**: sin violaciones. Complexity Tracking vacío.

## Project Structure

### Documentation (this feature)

```text
specs/001-chat-venta-seguros/
├── spec.md              # v2 (este PR)
├── plan.md              # este archivo
├── research.md          # Phase 0 — decisiones y opciones abiertas
├── data-model.md        # Phase 1 — entidades y DB
├── quickstart.md        # Phase 1 — cómo correr y validar el demo
├── contracts/
│   ├── motor-scoring.md # contrato del motor (entrada/salida, sin stack)
│   └── flujo-chat.md    # contrato del flujo conversacional (estados)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
producto/                          # estructura de JD en main
├── engines/
│   ├── scoring_engine.py          # score: perfil → ranking de productos (reglas del Excel)
│   ├── quote_engine.py            # prima + idoneidad (evolución del de JD)
│   ├── data/
│   │   ├── productos-seguros.json # catálogo (copiado de ideación) + campo automatica/asistida
│   │   ├── scoring_reglas.csv     # matriz de pesos EXPORTADA del Excel (fuente: el Excel)
│   │   └── perfiles_demo.json     # 2–3 perfiles sintéticos por SERIE
│   ├── db/
│   │   ├── schema_seguros.sql     # esquema único (evolución del de JD)
│   │   └── trazabilidad.db        # SQLite (gitignored; se regenera)
│   └── tests/
│       └── test_casos_dorados.py  # 2 perfiles demo → resultados fijos esperados
└── demo/
    ├── index.html                 # chat UI (simula WhatsApp, paleta recursos-marca/)
    ├── app.js                     # máquina de estados del flujo (bifurcaciones + 5 preguntas)
    └── style.css
```

**Structure Decision**: web app mínima dentro de `producto/` (estructura que JD dejó
en main). El motor es un módulo Python independiente y testeable sin la UI
(constitución I); la UI habla con el motor por el contrato de
`contracts/motor-scoring.md`, sea cual sea el transporte que elija el equipo dev.

**Esta separación ES la tesis de producto**: la infraestructura (motor + score +
DB + trazabilidad) es el producto; el chat es la primera feature encima. Cambiar
de chat web a WhatsApp real, wallet o marketplace = cambiar el consumidor del
contrato, cero cambios en el cerebro. Es el argumento de escalabilidad del pitch
(SC-006) y la defensa ante "¿wrapper de Gemini?".

## Fases de implementación

- **Fase A (P1 core)**: exportar reglas del Excel → `scoring_engine.py` + casos dorados → integrar `quote_engine.py` → DB + trazabilidad.
- **Fase B (P1 UI)**: chat UI con máquina de estados (paso 0 afiliado/no-afiliado → pregunta 1 intención → descubrimiento) → consentimiento → póliza + hash → pantalla de cierre.
- **Fase C (P1 LLM)**: capa de redacción (Gemini) sobre valores del motor, con plantillas de fallback.
- **Fase D (P2)**: paquete sugerido post-compra (reusa el ranking del score).
- **Fase E (P3)**: clasificación automática/asistida en catálogo + derivación simulada + registro de abandono.

Gate entre fases: la anterior corre end-to-end (constitución V).

## Complexity Tracking

Sin violaciones que justificar.

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24 · pendiente validación en daily 9am*
