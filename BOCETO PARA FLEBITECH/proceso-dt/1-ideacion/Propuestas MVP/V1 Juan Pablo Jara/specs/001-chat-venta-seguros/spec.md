# Feature Specification: Agente conversacional de venta automatizada de seguros ("Jarvis")

**Feature Branch**: `001-chat-venta-seguros`

**Created**: 2026-07-23 · **Updated**: 2026-07-24 (v2)

**Status**: v2 ajustada a la dirección de la matriz de decisión (C como MVP →
evolución D) + aportes del Día 1. **Pendiente de validación del equipo en el
daily del vie 24-jul 9am** — la votación formal del "frankenstein" se confirma ahí.

**Input**: Reto 02 Colsubsidio: agente que lleva al usuario de "no sé qué seguro
necesito" (o "quiero ESTE seguro") a "quedé asegurado", con máximo 5 preguntas,
scoring determinista decidiendo y el LLM solo conversando. Sin humano, 24/7.

**Dirección adoptada (matriz + Montecarlo, JD)**: C · agente conversacional tipo
Jarvis como MVP, con el scoring (B · Caro/Melissa/Lizeth) como cerebro embebido y
la hiperpersonalización del marketplace (A · JP) como encuadre y evolución (D).
El MVP usa chat web que simula la conversación de WhatsApp (constitución V:
demo primero); WhatsApp real y billetera son interfaces de la visión.

**Tesis de producto (JP — reconcilia A, B, C y D)**: el producto real es la
**infraestructura** — motor determinista + score + DB de trazabilidad + flywheel
de data. Jarvis, la wallet o el marketplace son *features*: caras intercambiables
sobre la misma infraestructura. Por eso el motor se construye contra contrato
(`contracts/motor-scoring.md`) y la UI es reemplazable sin tocar el cerebro. Lo
que se demuestra al jurado no es solo un chat que vende: es que la misma
infraestructura materializa cualquier interfaz que Colsubsidio necesite, a la
escala y velocidad que necesite (camino a producción: arquitectura de 9 capas en
`pi-preexistente/`).

## Flujo de entrada *(nuevo en v2)*

Antes de las 5 preguntas hay dos bifurcaciones que definen el camino:

**Paso 0 · ¿Afiliado o no afiliado?** (aporte de Lizeth)
- **Afiliado**: se identifica por SERIE (simulada en demo) → el motor carga su
  perfil de la base v2 (segmento, categoría, banda salarial) → las preguntas se
  reducen porque el sistema ya sabe; verificación simulada sin fricción
  (hash + consentimiento, cero PII — zona 6 del mapa).
- **No afiliado**: flujo genérico con las 5 preguntas completas → al cierre,
  además de la póliza, se le ofrece la afiliación a Colsubsidio (el chat de
  seguros fabrica leads de afiliación — zona 7 · prospección).

**Pregunta 1 · Bifurcación de intención** (aporte de Lizeth + sticky del equipo)
- **Llega con intención** ("quiero un SOAT", "necesito seguro para mi moto"):
  no se le hace el descubrimiento completo — se le muestra **el producto que
  pidió + 2 alternativas que el score considera más idóneas** para su perfil.
  La cultura local: la gente llega pidiendo un seguro concreto; se respeta esa
  intención y el score complementa, no estorba.
- **No sabe qué necesita**: flujo de descubrimiento (las 5 preguntas) → el
  score decide la recomendación.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compra de un seguro simple por chat (Priority: P1)

Un afiliado de Colsubsidio (perfil demo sintético, ej. mujer 29 años, monoparental,
categoría A, ingreso 1–1,5 SMLV) entra al chat, pasa por las bifurcaciones de
entrada, responde máximo 5 preguntas y sale asegurada con número de póliza, sin
intervención humana.

**Why this priority**: Es la promesa literal del brief y lo que el jurado evalúa en
el demo de 3 minutos. Sin esto no hay nada.

**Independent Test**: Correr el flujo completo con 2 perfiles demo distintos
(uno afiliado con intención, uno no afiliado sin intención) y verificar que
producen recomendación, prima y póliza distintas, con registro en DB.

**Acceptance Scenarios**:

1. **Given** un afiliado nuevo en el chat SIN intención definida, **When**
   responde las 5 preguntas (qué proteger → quién depende de ti → cuánto puede
   pagar/mes → cobertura actual → contacto), **Then** recibe UNA recomendación
   de producto del catálogo con justificación en lenguaje simple ("te recomiendo
   esto porque…") y prima calculada por el motor determinista — nunca por el LLM.
2. **Given** un usuario que llega CON intención ("quiero un SOAT"), **When** el
   chat la detecta en la pregunta 1, **Then** muestra el producto pedido + 2
   alternativas rankeadas por el score para su perfil, cada una con su prima
   del motor, sin forzar el descubrimiento completo.
3. **Given** un usuario NO afiliado, **When** completa el flujo, **Then** el
   sistema procesa la venta con el flujo genérico y al cierre ofrece la
   afiliación a Colsubsidio (lead registrado en DB como señal de prospección).
4. **Given** la recomendación en pantalla, **When** el afiliado pregunta "¿por qué
   este seguro?", **Then** el sistema explica la idoneidad con las variables
   usadas por el score (necesidad declarada, dependientes, capacidad de pago)
   sin jerga.
5. **Given** que el afiliado acepta, **When** confirma el consentimiento explícito
   (checkbox/frase con producto + prima + link al resumen), **Then** se emite
   póliza con número visible (formato COL-2026-XXXXX), se registra en DB con hash
   de trazabilidad y se muestra pantalla de cierre celebratoria.
6. **Given** un afiliado cuyo presupuesto declarado es menor que la prima del
   producto ideal, **When** el motor evalúa idoneidad, **Then** recomienda la
   alternativa asequible (microseguro/AP) — nunca fuerza la venta del producto
   caro. La prima recomendada no supera un umbral responsable del ingreso
   declarado (usar RANGO_SALARIAL de la base v2 como referencia del cálculo).
7. **Given** cualquier paso del flujo, **When** el usuario responde, **Then** el
   dato queda escrito en la DB de trazabilidad (señal → score → oferta → decisión).

---

### User Story 2 - Paquete sugerido post-compra (Priority: P2)

Tras emitirse la póliza, la pantalla final ofrece "tu paquete sugerido": 2–3
pólizas complementarias al perfil con un precio mensual único simulado.

**Why this priority**: Es la semilla del marketplace (encuadre A / evolución D) y
el argumento de cross-sell/CAC negativo del pitch, sin reescribir el motor. Media
jornada de trabajo si la P1 ya corre.

**Independent Test**: Con la P1 cerrada para un perfil, verificar que el paquete
sugerido cambia según el perfil (monoparental ≠ soltero joven) y muestra un único
total mensual.

**Acceptance Scenarios**:

1. **Given** una póliza emitida para un perfil monoparental, **When** aparece la
   pantalla final, **Then** el paquete sugiere productos coherentes con el score
   segmento→producto (ej. vida con beneficiarios + exequial) con precio mensual
   único marcado como simulado.
2. **Given** el paquete en pantalla, **When** el afiliado lo ignora, **Then** el
   cierre de la P1 no se degrada (el paquete es opcional, no bloquea).

---

### User Story 3 - Venta asistida, abandono como señal (Priority: P3)

No todas las pólizas son autoservicio (criterio de Caro): las de mayor
rigurosidad (vida con asesoría, educación) se marcan como **venta asistida** y el
chat ofrece explícitamente "hablar con una persona". Si el usuario abandona el
flujo en cualquier punto, el sistema registra el punto de fuga y la objeción.

**Why this priority**: Sustenta el flywheel (cada conversación deja data, incluso
la que no cierra) y la división venta automática / venta asistida que definió
Caro con los requisitos reales de cada producto. Es narrable en el pitch aunque
se implemente mínimo.

**Independent Test**: Abandonar el flujo en la pantalla de precio y verificar el
registro en DB (paso + motivo si lo dio); pedir un seguro de vida con asesoría y
verificar la oferta de derivación.

**Acceptance Scenarios**:

1. **Given** un usuario que llegó hasta el precio, **When** cierra el chat sin
   comprar, **Then** la DB registra el punto de fuga y la última interacción.
2. **Given** una necesidad clasificada como **venta asistida** (rigurosidad alta
   según la clasificación de Caro), **When** el motor lo detecta, **Then** el
   chat ofrece continuar solo o "hablar con un asesor" (derivación simulada)
   sin abandonar al usuario.

---

### Edge Cases

- Respuestas ambiguas o fuera de opción en las 5 preguntas → el chat re-pregunta
  con opciones cerradas; máximo 2 reintentos por pregunta.
- El usuario pide un producto que el catálogo no cubre → el chat lo dice
  explícitamente y ofrece lo más cercano según el score (constitución: no inventar).
- La intención declarada en pregunta 1 es ambigua ("un seguro para mi familia")
  → se trata como "no sabe qué necesita" y va al descubrimiento.
- Petición de datos personales sensibles → no se piden; solo lo definido en las 5
  preguntas (constitución III).
- El LLM no responde o falla → mensaje de reintento; el motor y la DB nunca
  dependen del LLM para las cifras.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El flujo completo (inicio → póliza emitida) debe tener máximo 5
  preguntas al usuario y debe poder completarse en menos de 3 minutos.
- **FR-002**: Toda cifra mostrada (prima, cobertura, score) proviene del motor
  determinista; el LLM solo redacta alrededor de valores ya calculados.
- **FR-003** *(v2)*: **El score es el core.** El motor implementa en Python el
  modelo de scoring construido por Caro, Melissa y Lizeth
  (`Motor_Scoring_Seguros_Colsubsidio.xlsx`, ya en el repo), enriquecido con las
  variables DANE/Fasecolda que definieron. El Excel es la fuente de las reglas;
  el Python las ejecuta. Cambios de reglas = cambiar datos, no código.
- **FR-004** *(v2)*: El flujo implementa las dos bifurcaciones de entrada:
  afiliado/no afiliado (paso 0) e intención/descubrimiento (pregunta 1), según
  la sección "Flujo de entrada".
- **FR-005**: El catálogo de productos se carga desde el JSON del catálogo
  (26 productos, 7 familias; precios simulados, salvo SOAT que tiene tarifa
  pública). Ubicación final del JSON: dentro de `producto/engines/` (se copia
  desde la carpeta de ideación al montar el motor).
- **FR-006**: La recomendación usa como mínimo: necesidad declarada (o intención),
  dependientes, capacidad de pago declarada, y el score segmento→producto; la
  asequibilidad se valida contra el ingreso (bandas SMLV).
- **FR-007**: El consentimiento y la idoneidad quedan registrados junto a la
  póliza (schema `schema_seguros.sql` + hash).
- **FR-008**: Cada interacción escribe en la DB de trazabilidad (incluido el
  abandono y el lead de afiliación de no afiliados). Un solo esquema, una sola DB.
- **FR-009**: Cada producto del catálogo se clasifica como **venta automática**
  o **venta asistida** (clasificación de Caro por rigurosidad de requisitos);
  la clasificación vive como campo del catálogo/score, no en el código.
- **FR-010**: La UI es un chat web responsive que simula la conversación de
  WhatsApp (visión: WhatsApp real vía n8n); sin integraciones reales de pago ni
  aseguradoras (exclusión del brief).
- **FR-011**: Textos del chat en español simple, sin jerga técnica de seguros
  (patrones del playbook: una pregunta a la vez, precio como recompensa, cierre
  celebratorio).

### Key Entities

- **Usuario (demo)**: afiliado (SERIE sintética, segmento, categoría, banda
  salarial) o no afiliado (solo respuestas del chat). Sin PII.
- **Producto**: del catálogo JSON (26 productos, 7 familias, aseguradora, URL,
  clasificación automática/asistida).
- **Score**: variables del modelo de Caro/Melissa/Lizeth + resultado por
  producto para el perfil.
- **Cotización**: producto + prima + variables usadas + veredicto de idoneidad.
- **Póliza**: número, usuario (SERIE o lead), producto, prima, consentimiento,
  hash, timestamp.
- **Evento de trazabilidad**: paso del flujo, dato capturado, timestamp (incluye
  abandonos y leads de afiliación).

## Success Criteria *(mandatory)*

- **SC-001**: 2 perfiles demo distintos completan el flujo end-to-end en vivo, con
  recomendaciones y primas distintas y explicables.
- **SC-002**: Demo completo cabe en el guion de 3 minutos con al menos 60 segundos
  de flujo en vivo sin cortes.
- **SC-003**: Ante la pregunta del jurado "¿por qué esta cifra/este producto?", la
  respuesta es demostrable en pantalla (evidencia en DB) en menos de 30 segundos.
- **SC-004**: Cero datos personales reales visibles en todo el demo.
- **SC-005** *(v2)*: El demo muestra al menos una bifurcación en vivo (usuario
  con intención vs. sin intención, o afiliado vs. no afiliado) para evidenciar
  la personalización.
- **SC-006** *(v2)*: El pitch demuestra que la interfaz es intercambiable sobre
  la misma infraestructura (narrado con el contrato del motor + diagrama de
  camino a producción — no requiere construir una segunda interfaz).

## Assumptions

- La dirección C→D sale de la matriz de decisión + Montecarlo de JD (C gana 75%
  de escenarios); **la votación formal del equipo se confirma en el daily del
  vie 24-jul** — si cambia, esta spec se ajusta en el mismo daily.
- El stack del motor y la decisión ML vs. reglas de scoring se definen en el
  **levantamiento de requisitos del motor** (equipo dev: Daniel, Sebas + JD),
  vie 24-jul. Esta spec no impone stack; impone el contrato: determinista,
  explicable, reglas en datos.
- La billetera (Caro) y WhatsApp real (JD) son interfaces de la visión; el MVP usa
  chat web que simula la conversación (constitución V: demo primero).
- El "paquete sugerido" (P2) usa precios simulados y no requiere lógica de
  suscripción real.
- El build vive en `producto/` (estructura de JD: `demo/`, `engines/`,
  `recursos-marca/`); esta carpeta de ideación queda como archivo del proceso.

---

*Construido con Claude Fable 5 (esfuerzo alto) · v2 del 2026-07-24 · v1 del 2026-07-23*
