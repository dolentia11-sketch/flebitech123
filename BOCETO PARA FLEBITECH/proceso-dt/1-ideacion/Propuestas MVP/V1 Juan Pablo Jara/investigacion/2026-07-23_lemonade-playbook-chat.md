# Lemonade Playbook — Diseño de chat de venta de seguros

> Construido con Claude Sonnet 4.6 (investigación web dirigida). Fecha: 2026-07-23.

---

## Resumen ejecutivo

- **Maya hace entre 10 y 17 preguntas en conversación uno-a-uno**, y entrega un quote en menos de 90 segundos. El proceso completo de bind (póliza activa con número) tarda entre 90 segundos y 2 minutos. Más del 90% de las pólizas se venden hoy a través de bots sin intervención humana.
- **El precio aparece como "momento mágico" después de las preguntas**, no al inicio. Lemonade identificó que mostrar el precio demasiado pronto causaba abandono masivo; simplificaron esa pantalla a solo el precio y un botón de compra.
- **AI Jim (claims) es el principal argumento de confianza en la venta**: "firmás una honesty pledge, grabás un video, y recibís el pago en segundos" es el counter-narrative contra el miedo histórico a los seguros. El récord documentado es 2 segundos; el caso fundacional fue 3 segundos.
- **El diseño conductual anticipa el fraude desde el flujo de venta**: la "honesty pledge" en claims (y su equivalente en onboarding) está inspirada en la ciencia del comportamiento de Dan Ariely — el compromiso explícito de honestidad antes de declarar reduce las declaraciones falsas.
- **Lemonade solo opera en EE.UU. y algunos países de Europa**: no tiene presencia en Colombia ni Latinoamérica. Sus mecanismos regulatorios (disclosures por estado, licencias NAIC) no son trasladables directamente, pero sus patrones de UX y conversión sí lo son.

---

## El flujo de Maya paso a paso

### Fuentes verificadas

Las fuentes no publican el script completo de Maya (Lemonade no lo ha divulgado). Lo que sigue es la reconstrucción más fiel posible a partir de reviews de UX, artículos de producto y descripciones de usuarios reales.

### Estructura general (renters insurance como caso base)

**Pantalla 0 — Bienvenida y creación de cuenta**
- Email + contraseña (o login social).
- Maya se presenta: nombre, tono amigable, conversacional.

**Bloque 1 — Datos de contexto (≈ 3–5 preguntas)**

Los datos recopilados en este bloque determinan el riesgo base y el precio:

1. ¿Dónde vives? (dirección / ZIP code) — define el mercado y las regulaciones aplicables.
2. ¿Qué tipo de residencia? (apartamento, casa, estudio) — determina tipo de cobertura.
3. ¿Cuántas personas viven contigo? — afecta cobertura de responsabilidad civil.
4. Fecha de inicio de la cobertura (selector de fecha).

**Bloque 2 — Necesidades de cobertura (≈ 4–6 preguntas)**

5. ¿Cuánto valen tus pertenencias? (slider con rangos predefinidos como ancla visual).
6. ¿Tienes objetos de alto valor? (joyería, instrumentos, bicicleta) — dispara riders adicionales.
7. ¿Tienes dispositivos de seguridad en casa? (alarma, extintores, detector de humo) — descuento documentado.
8. ¿Has tenido reclamos en los últimos 5 años? (SÍ/NO — afecta precio).

**Bloque 3 — Datos personales (≈ 2–3 preguntas)**

9. Nombre completo.
10. Fecha de nacimiento.
11. Número de teléfono (verificación posterior por SMS).

**Pantalla del Quote — "Momento mágico"**

- Maya muestra el precio mensual / anual en una pantalla limpia, sin jargón.
- Hay un slider para ajustar el deducible y ver cómo cambia el precio en tiempo real.
- Botón de "Get Discounts" que permite agregar información adicional (alarmas, etc.) para bajar el precio.
- Lemonade eliminó toda la navegación y el jargón de esta pantalla después de detectar caída masiva de conversión aquí. Solo precio + botón.

**Pantalla de pago y bind**

- Ingreso de datos de tarjeta.
- Confirmación de cobertura.
- Pantalla de éxito: número de póliza, fecha de inicio, acceso a la app.

**Post-bind**

- Verificación del número de teléfono.
- Activación de notificaciones push.
- Bienvenida a la comunidad (Giveback: el afiliado elige una causa social).

### Tiempos documentados

| Etapa | Tiempo reportado |
|---|---|
| Quote completo (inicio a precio) | < 90 segundos |
| Proceso completo (inicio a póliza activa) | ≈ 90 segundos – 2 minutos |
| Pago de claims (casos simples, AI Jim) | 2–3 segundos (récord verificado) |

**Fuentes:** [PageFlows — Lemonade iOS onboarding (48 pantallas)](https://pageflows.com/post/ios/onboarding/lemonade/), [UX Review Medium](https://medium.com/@musingmurmurs/ux-review-of-lemonade-insurance-c5648593e7f9), [Perspective AI case study](https://getperspective.ai/blog/lemonade-case-study-conversational-ai-insurance), [UXReactor](https://uxreactor.com/lemonade-ai-disrupts-insurance-industry/).

---

## Patrones de diseño extraíbles para un chat de 5 preguntas

Estos patrones son accionables y directamente aplicables al MVP del hackathon.

### 1. Orden de preguntas: contexto → necesidad → datos personales

**Patrón de Lemonade:** Primero las preguntas que construyen el contexto de riesgo (¿dónde?, ¿qué tipo?), luego las que revelan la necesidad (¿cuánto vale?, ¿qué tienes?), y solo al final los datos personales (nombre, fecha de nacimiento, teléfono).

**Por qué funciona:** Pedirle el nombre y la cédula a alguien antes de demostrarle valor genera abandono. El afiliado primero ve que el sistema "lo entiende", y recién entonces entrega datos sensibles.

**Aplicación para 5 preguntas:**
1. ¿Qué quieres proteger? (vida, hogar, accidente, educación) — detección de necesidad
2. ¿Cuántas personas dependen de ti? — contexto de exposición
3. ¿Cuánto puedes pagar al mes? (rangos: menos de $30K / $30–80K / más de $80K COP) — ancla de precio y suitability
4. ¿Tienes algún seguro actualmente? — idoneidad y oportunidad de mejora
5. ¿Cuál es tu correo o celular? — captura de contacto solo al final, cuando ya hay intención

### 2. Una pregunta a la vez (nunca formulario)

**Patrón de Lemonade:** Maya presenta siempre UNA sola pregunta en pantalla. No hay un formulario visible ni barra de progreso explícita en algunas versiones. Esto reduce la ansiedad cognitiva ("¿cuánto falta?") y aumenta la tasa de completación.

**Microcopy clave:** Las preguntas usan lenguaje coloquial, no técnico. "¿Cuánto valen tus cosas más o menos?" en vez de "Indique el valor de los bienes asegurados".

### 3. El precio como recompensa, no como punto de entrada

**Patrón de Lemonade:** El quote solo aparece DESPUÉS de responder todas las preguntas. Mixpanel documentó que mostrar el precio en una pantalla con jargón causaba caída masiva de conversión; al simplificarla, lograron un aumento de 250% en la tasa de conversión quote-a-compra.

**Aplicación:** Después de la pregunta 5, mostrar la prima calculada en pantalla limpia. Solo el número, el periodo (mensual) y un botón verde. Nada más.

### 4. Sliders con anclas visuales para el precio

**Patrón de Lemonade:** El afiliado puede mover un slider de deducible y ver el precio cambiar en tiempo real. Esto crea engagement y da sensación de control. El rango del slider está diseñado para que la opción "media" (la más seleccionada) sea la más rentable para Lemonade.

**Aplicación:** En el paso de la suma asegurada, usar rangos pre-definidos en botones (ej. "Protección básica $10M / Protección media $30M / Protección completa $50M") en lugar de campo libre. El del medio siempre estará pre-seleccionado.

### 5. Consentimiento integrado en el flujo, no en una cláusula al final

**Patrón de Lemonade:** Los disclosures aparecen inline, en lenguaje simple, en el momento en que son relevantes (no en un bloque de texto legal al final). El consentimiento de datos aparece antes de pedir información personal. La "honesty pledge" en claims aparece como primer paso del proceso, no al final.

**Aplicación para Colombia (venta adecuada / SFC):**
- Antes de la pregunta 4 (¿tienes seguro actualmente?): "Voy a hacerte una pregunta sobre tu situación actual para asegurarme de recomendarte lo que más te conviene, no lo más caro."
- Antes de mostrar el quote: "Con base en tus respuestas, encontré la cobertura más adecuada para ti. Aquí está tu prima:"
- Antes del pago: checkbox explícito "Entiendo que estoy contratando [nombre del producto] por [prima] mensuales. He leído el [link resumen de póliza]."

### 6. Tono: amigable pero directo, sin jerga técnica

**Patrón de Lemonade:** Maya usa primera persona ("Hola, soy Maya"), frases cortas, emojis ocasionales, y nunca usa términos como "prima de riesgo", "deducible por evento", "coaseguro". Todo se traduce: "lo que pagas al mes", "lo que pones tú cuando hay un reclamo".

**Microcopy recomendado para el MVP:**
- En vez de "suma asegurada": "¿cuánto necesitas que te cubra el seguro?"
- En vez de "vigencia": "¿desde cuándo quieres estar cubierto?"
- En vez de "exclusiones": "esto es lo que no cubre este plan" (con lista clara)
- En vez de "póliza emitida": "listo, ya estás asegurado"

### 7. Momento del número de póliza: inmediato y celebratorio

**Patrón de Lemonade:** Al finalizar el pago, la pantalla de éxito muestra el número de póliza de forma prominente, junto con una confirmación por email/SMS. No hay "proceso de aprobación pendiente". La póliza es instantánea.

**Aplicación MVP:** La pantalla final del chat debe mostrar:
- Número de póliza (formato legible, ej. COL-2026-XXXXX)
- Nombre del producto y coberturas
- Prima mensual confirmada
- Fecha de inicio y fecha de primer cobro
- CTA: "Descargar certificado de seguro"

---

## Cómo AI Jim integra confianza en la venta

### El mecanismo

AI Jim es el bot de claims de Lemonade. El flujo de un reclamo simple es:

1. El afiliado abre la app y describe el siniestro.
2. Firma una **honesty pledge** digital (compromiso explícito de veracidad — ciencia conductual).
3. Graba un **video corto** explicando qué pasó.
4. AI Jim ejecuta **18 algoritmos anti-fraude simultáneamente** (verificación de póliza, análisis del video, patrones históricos, etc.).
5. Si todo pasa, el pago se transfiere al banco **en segundos**. El récord verificado documentado es de **2 segundos** (pagado en diciembre de 2016); el caso publicado en prensa fue de 3 segundos.
6. Si hay señales de fraude o el reclamo es complejo, se escala automáticamente a un experto humano.

**Automatización actual (Q2 2025):** 55% de los reclamos se procesan completamente por IA sin intervención humana. El 96% de los primeros avisos de siniestro son gestionados por chatbots.

### Por qué esto sirve como argumento de venta

El miedo histórico a los seguros no es "¿puedo pagarlo?" — es **"¿me van a pagar cuando lo necesite?"**. Lemonade invierte el argumento: la velocidad del claims es el cierre de venta. En el chat de venta, mencionan explícitamente: "Si algo pasa, lo resolvemos en minutos, no en semanas."

**Aplicación para el MVP:** En la pantalla post-quote (antes del pago), agregar un bloque de confianza con el argumento de velocidad de pago. No necesitas récord Guinness — con "respuesta en menos de 24 horas" y "sin papeleo" ya diferencias frente al modelo tradicional de Colsubsidio.

### Nota importante sobre la honesty pledge

La investigación conductual de Dan Ariely (Chief Behavioral Officer de Lemonade, 2015–2020) que sustentaba la efectividad del pledge para reducir fraude fue cuestionada en 2021 por estar basada en datos fabricados. Sin embargo, el mecanismo de video + compromiso sigue siendo parte del producto de Lemonade, y la práctica de obtener compromisos explícitos antes de declarar información sigue siendo una técnica de diseño válida y usada en la industria. **Fuente:** [Insurance Thought Leadership — A Behavioral Science Scandal](https://www.insurancethoughtleadership.com/personal-lines/behavioral-science-scandal).

---

## Métricas del funnel de Lemonade (datos verificados)

| Métrica | Valor | Fuente |
|---|---|---|
| Tiempo hasta quote | < 90 segundos | Múltiples fuentes |
| Tiempo hasta bind | 90 seg – 2 min | Reviews de usuarios |
| % de pólizas vendidas por bots | > 90% | Trixly AI case study (Q2 2025) |
| % de reclamos automatizados completamente | 55% | Velocity AI / Trixly (Q2 2025) |
| % primeros avisos de siniestro por bot | 96% | Velocity AI |
| Récord de pago de reclamo (AI Jim) | 2 segundos | AI Magazine / Insurtech Insights |
| Aumento en conversión quote-a-compra | 250% (Extra Coverage) | Mixpanel case study |
| Aumento en conversión Extra Coverage | 50% | Mixpanel case study |
| NPS / tasa de renovación | 94% renovación | Insurnest case study |
| Clientes que recomendarían | 96% | Insurnest case study |
| Satisfacción en claims | 97% | Insurnest case study |
| Calificación en app stores | 4.9/5 | UXReactor |
| IFP (prima en vigor) a Q2 2025 | > $1 mil millones USD | Perspective AI |

---

## Qué NO copiar: contexto EE.UU. que no aplica a Colombia

### 1. El modelo de flat fee + Giveback

Lemonade cobra un fee fijo del 20–25% de la prima y devuelve el excedente de siniestros a causas sociales elegidas por el afiliado. Este modelo requiere una licencia específica (Public Benefit Corp.) y estructura de reservas que no existe en Colombia. Colsubsidio tiene su propio modelo de subsidio. **No replicar este modelo de negocio en el MVP — sí se puede replicar el mensaje de "sin conflicto de interés".**

### 2. El flujo de "video de claims" como requisito regulatorio

En EE.UU., el video es una decisión de producto de Lemonade, no un requisito legal. En Colombia, el proceso de liquidación de siniestros está regulado por la SFC y los productos de Colsubsidio tienen sus propios protocolos. El chat del MVP es solo para la venta — no para el claims.

### 3. Los disclosures por estado (state-specific)

Lemonade adapta sus disclosures por cada estado de EE.UU. (California tiene reglas distintas a Nueva York). En Colombia, el marco es nacional (Decreto 2673/2012, Circular Externa 050/2018 de la SFC sobre canales digitales de venta). Los disclosures del MVP deben seguir el marco colombiano.

### 4. La arquitectura de reaseguro y underwriting propios

Lemonade hace su propio underwriting con ML propio. Para el hackathon, el underwriting es el de Colsubsidio — el chat solo captura datos y los pasa al motor de cotización existente. No inventar underwriting propio.

### 5. La personalidad "startup hipster" de Maya

Maya usa un tono muy informal, con referencias a cultura pop y humor irreverente que funciona para millennials urbanos de Nueva York. Para afiliados de Colsubsidio (amplio rango de edades y perfiles), el tono debe ser cálido y accesible, pero no necesariamente irreverente. Cuidado con sonar como si estuvieras vendiendo seguros en Brooklyn.

### 6. La integración de Giveback como argumento principal

El Giveback (donar el excedente) es el pilar de confianza de Lemonade. Colsubsidio ya tiene un propósito social institucional fuerte — usar eso como argumento de confianza es más honesto y relevante que copiar el Giveback.

---

## Fuentes

Todas las afirmaciones con URL verificada:

- [UXReactor — Lemonade AI disrupts insurance](https://uxreactor.com/lemonade-ai-disrupts-insurance-industry/)
- [Medium — Love at first chat with Maya](https://medium.com/marketing-in-the-age-of-digital/love-at-first-chat-with-lemonades-ai-chatbot-maya-7b4a105824bd)
- [Medium / ProductSins — UX Review of Lemonade Insurance](https://medium.com/@musingmurmurs/ux-review-of-lemonade-insurance-c5648593e7f9) — fuente del dato "17 preguntas, 1.5 minutos"
- [PageFlows — Lemonade iOS Onboarding (48 pantallas)](https://pageflows.com/post/ios/onboarding/lemonade/)
- [Perspective AI — Lemonade conversational AI case study](https://getperspective.ai/blog/lemonade-case-study-conversational-ai-insurance)
- [Trixly AI — Agentic AI in Insurance: Lemonade](https://www.trixlyai.com/blog/our-blog-1/agentic-ai-insurance-lemonade-case-study-28)
- [AI Magazine — Lemonade 2-second claim record](https://aimagazine.com/articles/lemonade-sets-world-record-with-2-second-ai-insurance-claim)
- [Insurtech Insights — Lemonade 2-second claim](https://www.insurtechinsights.com/lemonade-sets-new-record-by-settling-claim-in-two-seconds/)
- [IIReporter — 3-second claim original story](https://iireporter.com/lemonade-reports-insurance-claim-paid-in-3-seconds-with-no-paperwork/)
- [Velocity AI Partners — Lemonade AI claims case study](https://insights.velocityaipartners.co/case-studies/lemonade-ai-claims-processing-insurance)
- [Mixpanel — Lemonade drives 6x growth](https://mixpanel.com/customers/lemonade-drives-growth-mixpanels-user-insights/) — fuente del dato 250% conversión
- [Insurnest — Lemonade case study](https://insurnest.com/blog/lemonade-insurance-case-study/)
- [Perspective AI — AI-native insurance onboarding 2026](https://getperspective.ai/blog/ai-native-insurance-onboarding-2026-from-application-to-activation)
- [Fast Company — Lemonade behavioral science](https://www.fastcompany.com/3068506/lemonade-is-using-behavioral-science-to-onboard-customers-and-keep-them-honest)
- [Insurance Thought Leadership — Behavioral Science Scandal (Ariely)](https://www.insurancethoughtleadership.com/personal-lines/behavioral-science-scandal)
- [Lemonade Investor Day 2024 PDF](https://s24.q4cdn.com/139015699/files/doc_presentations/2024/Lemonade-Investor-Day-2024.pdf) — [no verificado: archivo excedió límite de carga]
- [Lemonade — Transparency page](https://www.lemonade.com/transparency) — [no verificado: página devolvió 403]
- [Lemonade — Blog "Secret behind instant insurance"](https://www.lemonade.com/blog/secret-behind-lemonades-instant-insurance/) — [no verificado: página devolvió 403]

### Afirmaciones no verificadas (marcadas explícitamente)

- **[no verificado]** Número exacto de preguntas: la fuente "17 preguntas" viene de una sola review de UX (ProductSins/Medium) de una versión antigua del flujo. El flujo actual puede ser diferente. PageFlows cuenta 48 pantallas totales en iOS, que incluyen creación de cuenta, verificación, onboarding, ajustes de cobertura y pago — no 48 preguntas puras.
- **[no verificado]** Métricas del Investor Day 2024: el PDF estuvo inaccesible durante la investigación. Los datos citados de Q2 2025 vienen de fuentes secundarias (Trixly AI, Velocity AI), no del documento de Lemonade directamente.
- **[no verificado]** Datos del S-1 de la SEC: el documento devolvió 403. Los datos de S-1 citados (% clientes bajo 35, crecimiento de GWP) vienen de TechCrunch y análisis de terceros del IPO.
- **[no verificado]** Detalles internos del flujo conversacional de Maya en 2025: Lemonade no publica el script de Maya. La reconstrucción del flujo en esta investigación es una síntesis de múltiples reviews de usuarios y análisis de UX, no una documentación oficial.
