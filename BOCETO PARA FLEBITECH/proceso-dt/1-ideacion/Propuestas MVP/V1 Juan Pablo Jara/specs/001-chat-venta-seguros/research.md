# Research — 001 · Agente de venta de seguros (Phase 0)

Resuelve las incógnitas del Technical Context. Las marcadas **[ABIERTA — dev vie 24]**
se cierran en el levantamiento de requisitos del motor (Daniel, Sebas, JD); aquí
van las opciones con recomendación para no llegar a esa reunión en blanco.

## D1 · ¿ML o reglas para el scoring? (bloqueo declarado de Daniel)

- **Decisión recomendada**: reglas deterministas (matriz de pesos del Excel), NO ML entrenado.
- **Rationale**: (1) la base v2 no tiene variable target — entrenar supervisado es
  inviable en 3 días (el resto del reto está atascado exactamente ahí); (2) el reto
  pide recomendación con idoneidad explicable, no predicción; (3) constitución I
  exige explicabilidad total ("¿por qué esta cifra?" → traza en datos); (4) el
  flywheel: cada conversación fabrica data etiquetada — el ML es la evolución
  natural POST-hackathon, con la data que el propio sistema genera. Ese es el
  argumento para el pitch, no una carencia.
- **Alternativas consideradas**: clustering no supervisado sobre base v2 (útil como
  insumo de segmentos, no como motor de decisión — puede alimentar pesos, no
  reemplazarlos); LLM decidiendo (prohibido por constitución I).

## D2 · Cómo pasan las reglas del Excel al motor

- **Decisión**: exportar las hojas "Variables y Categorías" y "Matriz de Pesos" a
  CSV (`producto/engines/data/scoring_reglas.csv`) una sola vez por script; el
  motor lee el CSV. El Excel queda como fuente editable por Caro/Melissa/Lizeth:
  si cambian pesos, se re-exporta (script de 1 comando), sin tocar código.
- **Rationale**: "reglas en datos, no en código" (spec FR-003); evita que el motor
  dependa de openpyxl en runtime; las expertas mantienen la propiedad del modelo.
- **Alternativas**: leer el xlsx en runtime (frágil, dependencia extra); re-tipear
  pesos en Python (dos fuentes de verdad — descartado).

## D3 · Storage **[ABIERTA — dev vie 24]**

- **Recomendación**: SQLite. Cero infraestructura, archivo único versionable en
  esquema (no en datos), suficiente para demo, y la consulta en vivo ante el
  jurado ("aquí está el hash de tu póliza") es un comando.
- **Alternativas**: Postgres (si el equipo dev ya lo tiene montado, vale; si no,
  es fricción sin retorno en 3 días); JSON plano (pierde la credibilidad de
  "queda registrado en base de datos" ante jurado).

## D4 · Transporte motor ↔ chat **[ABIERTA — dev vie 24]**

- **Opciones**: (a) FastAPI/Flask local con 2 endpoints (`/score`, `/quote`);
  (b) n8n orquestando y llamando al motor como script; (c) backend único simple
  que sirve la UI y expone el motor.
- **Recomendación**: (c) para el demo (menos piezas que pueden fallar en vivo);
  (a) si Daniel/Sebas prefieren separación clara. n8n (b) se reserva para la
  visión WhatsApp real — mostrable como diagrama, no como dependencia del demo.
- **Criterio de decisión**: lo que el equipo dev pueda operar con confianza el
  domingo bajo presión. El contrato (`contracts/motor-scoring.md`) es el mismo
  en las tres opciones.

## D5 · LLM en el flujo

- **Decisión**: Gemini redacta la conversación (tono, explicación de idoneidad,
  re-preguntas) SOBRE valores ya calculados que recibe en el prompt. Cada
  pantalla tiene plantilla de fallback estática: si el LLM falla o tarda >N s,
  el demo sigue (constitución I + edge case de la spec).
- **Rationale**: quita al LLM del camino crítico del demo; la cita de Schreiber
  ("falta el andamiaje") defiende esta arquitectura ante "¿wrapper de Gemini?".
- **Nota Qwen**: el beneficio de 2B tokens de Qwen no está disponible (JD, 23-jul
  noche) — no se planifica nada sobre ese stack.

## D6 · UI del chat

- **Decisión**: HTML/CSS/JS vanilla, una página, estética de chat WhatsApp con
  paleta oficial (`producto/recursos-marca/`, ojo: no hay logo para fondo claro —
  usar fondo oscuro o el isotipo amarillo). Máquina de estados en `app.js`
  (bifurcaciones + preguntas + cierre); el flujo es demostrable offline con
  plantillas.
- **Alternativas**: React/Next (overkill, más build que valor en 3 días); Gemini
  Canvas (prototipo de JD útil como referencia visual, no como base de código
  del repo).

## D7 · Detección de intención en pregunta 1

- **Decisión**: híbrida y barata: matching por palabras clave contra el catálogo
  (nombres + sinónimos por familia: "SOAT", "moto", "carro", "mascota", "perro",
  "vida"…) resuelto por el motor; si el texto no matchea con confianza, se trata
  como "no sabe" → descubrimiento (edge case de la spec). El LLM puede ayudar a
  normalizar el texto, pero la asignación producto↔intención la valida el motor
  contra el catálogo (nunca inventa producto).
- **Rationale**: la bifurcación es demostrable determinísticamente; sin
  dependencia del LLM para la decisión.

## D8 · Verificación de afiliado (paso 0)

- **Decisión**: simulada — el usuario elige "soy afiliado" e ingresa una SERIE
  demo (o elige un perfil precargado); el motor carga el perfil sintético de
  `perfiles_demo.json`. En pantalla se narra la versión de producción (OTP al
  celular / validación de documento — zona 6 del Miro) sin construirla, por
  decisión ya registrada (bitácora 23-jul: el brief excluye integraciones
  reales).

---

*Construido con Claude Fable 5 (esfuerzo alto) · 2026-07-24*
