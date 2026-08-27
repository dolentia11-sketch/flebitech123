# Contrato — Flujo conversacional (máquina de estados de la UI)

La UI implementa esta máquina; el LLM redacta los textos de cada estado (con
plantilla de fallback estática por estado). Los datos y transiciones los decide
el motor, no el LLM.

## Estados

| Estado | Pregunta/acción | Escribe traza | Transición |
|---|---|---|---|
| `inicio` | Saludo + "¿eres afiliado a Colsubsidio?" | `paso0` | → `identificacion` o `intencion` |
| `identificacion` | (afiliado) SERIE demo / perfil precargado → motor carga perfil | `paso0` | → `intencion` |
| `intencion` | "¿Ya sabes qué seguro buscas o quieres que te ayude?" — texto libre | `intencion` | match (`detectar_intencion`) → `oferta_directa`; sin match → `p1` |
| `p1`–`p5` | Descubrimiento: qué proteger → quién depende → cuánto/mes → cobertura actual → contacto. Afiliado: las que el perfil ya responde se saltan (≤5 total) | `p1`..`p5` | → `recomendacion` |
| `oferta_directa` | Producto pedido + 2 alternativas del score, cada una con prima del motor | `oferta` | → `precio` |
| `recomendacion` | UNA recomendación + "por qué" (variables del score) | `oferta` | → `precio` |
| `precio` | Prima grande, limpia, 1 CTA (playbook Lemonade) | `precio` | → `consentimiento` / `abandono` / `derivacion` |
| `derivacion` | (si `asistida`) "¿seguimos aquí o hablas con una persona?" | `derivacion` | → `consentimiento` o fin simulado |
| `consentimiento` | Frase inline: producto + prima + resumen; checkbox | `consentimiento` | → `cierre` |
| `cierre` | Póliza COL-2026-XXXXX + hash + celebración | `cierre` | → `paquete` (P2) / `lead_afiliacion` (no afiliado) / fin |
| `paquete` | 2–3 complementarias + total mensual único (simulado), opcional | `paquete` | → fin |
| `lead_afiliacion` | "¿Quieres afiliarte a Colsubsidio?" — registra lead | `lead_afiliacion` | → fin |
| `abandono` | (cierre de ventana/inactividad) registra punto de fuga | `abandono` | fin |

## Reglas transversales

- Respuesta ambigua → re-pregunta con opciones cerradas, máx. 2 reintentos.
- Máximo 5 preguntas efectivas al usuario en cualquier camino (FR-001).
- El LLM recibe: estado actual + valores calculados del motor + perfil. Prohibido
  pasarle la decisión de transición o pedirle cifras.
- Timeout LLM (>4 s) → plantilla estática del estado; el flujo nunca se bloquea.
- Textos: español simple, una pregunta a la vez, cero jerga (FR-011).

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24*
