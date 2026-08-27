# Insights de Lemonade para el Reto 02 — Venta Automatizada de Seguros

> Fuente: entrevista a Daniel Schreiber (CEO de Lemonade) en After Earnings,
> "How Lemonade Uses AI to Compete in the MASSIVE Insurance Market" (~30 min).
> https://youtu.be/fBmk4mqZf1g · Transcripción completa extraída y analizada.
> Construido con Fable 5 (alto).

## Por qué importa para el reto

Lemonade es una aseguradora pública en EE.UU. (NYSE: LMND) fundada en 2015 que
opera **exactamente el modelo que pide el Reto 02**: venta de seguros por chat sin
humano, 24/7, con cierre real. No es una hipótesis — es una empresa con 2,3 millones
de clientes y ~US$890M en primas vigentes. Para un jurado de expertos en seguros,
citar a Lemonade convierte "¿esto funciona?" en "esto ya funciona a escala; la
pregunta es quién lo trae al afiliado de Colsubsidio primero".

## Cifras clave (para el pitch y el deck)

| Métrica | Valor | Uso en el pitch |
|---|---|---|
| Pólizas vendidas por bots | **97%** | Prueba de existencia del modelo del reto |
| Claims resueltos automatizados | 55% | La automatización no para en la venta |
| Clientes menores de 35 años | 70% | El digital-first sí compra seguros |
| Clientes / primas vigentes | 2,3M / ~US$890M | Escala real, no piloto |
| Crecimiento vs. headcount (3 años) | Negocio 2x, headcount +2% | Viabilidad operativa |
| Último trimestre | Top line +24%, headcount −7%, sin despidos | Idem |
| Loss ratio | 73% (−10 pts YoY) | La IA mejora el pricing del riesgo |
| Tamaño del sector seguros | ~11% del PIB (mayor que petróleo, defensa o software) | Tamaño del premio |

## 8 insights mapeados a los criterios del jurado

### 1. Prueba de existencia global → Viabilidad (20%+20%) y Pitch (10%)
Frase candidata: *"Esto no es una apuesta nuestra: Lemonade, aseguradora pública en
EE.UU., vende el 97% de sus pólizas por chat desde hace años. Lo que proponemos es
traer ese modelo probado al 1,56M de afiliados de Colsubsidio."*
Desactiva la objeción central ante expertos del sector.

### 2. La desconfianza es EL problema del sector → Impacto (30%) e Innovación (20%)
Schreiber: el mayor problema de los seguros es la **desconfianza** — se percibe como
juego de suma cero ("si me niegan el claim, ellos se quedan la plata"), y eso produce
fraude por decenas de miles de millones, baja lealtad y churn. Su respuesta es
**Giveback**: la utilidad de underwriting que exceda un umbral va a ONGs que elige el
cliente → "no estamos peleando por esa moneda".
**Mapeo Colsubsidio:** una caja de compensación está *mejor* posicionada que Lemonade
para esto — el excedente puede volver al ecosistema del afiliado (subsidios,
beneficios, convenios). Giro potencial del pitch: *"el afiliado nunca pierde: lo que
no se paga en siniestros regresa a su caja"*. ⚠️ Hipótesis regulatoria por validar
(SFC / régimen de cajas) antes de decirlo en el pitch.

### 3. "Graduarse con el cliente" → soporta la idea del marketplace/suscripción
Lemonade arrancó con renters (barato, joven) y fue sumando mascotas, hogar y auto a
medida que sus clientes avanzan de etapa de vida. Mapeo directo a nuestra base:
soltero joven (51,6%) entra por microseguro/AP/protección urbana; monoparental
(24,6%) escala a vida/educación; etc. El chat es la puerta de entrada; el LTV está
en el viaje. Encaja con la propuesta de marketplace con suscripción única (pestaña 6
del reporte del 22-jul).

### 4. Propensión y LTV calculados en tiempo real → Data e Innovación
Cada visitante de Lemonade pasa por ~50 modelos de ML (probabilidad de claim, churn,
cross-sell) que se descuentan a valor presente: "este cliente vale $1.300 hoy". El
90% del gasto de marketing se asigna así ("algo trading approach to acquiring
customers"). Para el MVP basta un score de propensión simple por segmento (ya
tenemos la segmentación v2 de la base); para la slide de visión, este es el norte.
Insight profundo citado por Schreiber: colapsar el feedback de 1–2 años a lectura
instantánea de qué cliente estás adquiriendo.

### 5. El roadmap de asesores queda validado → Viabilidad de implementación (20%)
Lemonade duplicó el negocio con headcount casi plano y **sin despidos**: la gente que
respondía tickets hoy entrena IAs, audita respuestas y corrige prompts, sin ser
ingenieros ("managers de IAs"). Esto valida punto por punto el roadmap de 3 fases que
JP ya metió a la propuesta (asistida → autonomía progresiva → asesores a
postventa/retención). Frase de Schreiber utilizable ante un jurado sensible al
empleo: *"el headcount humano quedó estático; la cantidad total de inteligencia
desplegada creció dramáticamente"*.

### 6. Microseguro para bajos ingresos ya probado → Impacto (30%)
Lemonade.org (su brazo sin ánimo de lucro) vende seguro de cosechas a agricultores de
subsistencia en África subsahariana: se compra desde el teléfono y **paga
automáticamente** (paramétrico, smart contracts) porque el costo tradicional de
distribución y ajuste hacía imposible asegurarlos. Argumento para nuestra base (76%
categoría A): *"el costo de distribución es lo que excluye al afiliado de bajos
ingresos; la automatización no es un gadget — ES la política de inclusión"*.

### 7. Disciplina de foco: asegurar solo lo que sabes evaluar → defensa en Q&A
Lemonade NO vende hogar en Florida ni en zonas de incendio de California: donde no
tiene ventaja de underwriting, no juega. Lección para el alcance del MVP: el chat de
5 preguntas debe ofrecer solo productos donde la idoneidad sí se puede evaluar con
esas preguntas (AP, protección urbana, SOAT como ancla, mascotas), y decir
explícitamente cuáles quedan fuera y por qué. Respuesta lista para "¿y si le venden
lo que no le conviene?": el sistema sabe qué NO vender.

### 8. Frases y analogías citables
- "Comprar tu seguro en pijama a las 2 a.m. y que te paguen el claim en segundos."
- "El sector es ~11% del PIB — más grande que petróleo, defensa o software — y está
  desatendido precisamente porque se percibe gris y aburrido." (= ventaja del
  outsider con ojos frescos, nuestra narrativa de mitigación del punto ciego)
- "No descubrimos la IA en 2023" → nosotros tampoco llegamos a improvisar: llegamos
  con el playbook de quien ya lo hizo.
- "Dos tercios de los conductores son mejores que el promedio" → personalizar
  beneficia a la mayoría; los promedios castigan al buen cliente.

## Lo que NO aplica (para no distraerse)

- **Telemática del teléfono** para pricing de auto: fuera de alcance del reto.
- **Synthetic agents** (General Catalyst financia 80% del CAC contra 16% de primas):
  fascinante pero irrelevante para un demo de 3 min. A lo sumo, nota mental para la
  vida real de FMA.
- **Blockchain/cripto** del caso África: citar el resultado (pago paramétrico
  instantáneo), no la tecnología — con este jurado suma más "automático y auditable"
  que "smart contract".

## Mini-plan de investigación propuesto (horas, no días — build empieza vie 24)

1. **Playbook de venta por chat de Lemonade** — Investor Day nov (video público) +
   S-1/shareholder letters: flujo real de preguntas de Maya (su bot), tiempos de
   cierre, manejo de idoneidad/consentimiento. Output: 1 pág. de patrones para el
   diseño del chat del MVP.
2. **Benchmarks de venta digital de seguros en Colombia/Latam** — R5, Seguros
   Falabella, 123Seguro, Betterfly, Súper (SFC) sobre canales digitales. Output:
   2–3 cifras locales para que el pitch "huela a real" ante Colsubsidio.
3. **Validación regulatoria del "giveback criollo"** — ¿puede el excedente volver al
   afiliado vía beneficios de la caja sin romper régimen de seguros/cajas? Extiende
   la investigación de recaudo del 22-jul. Output: semáforo (se dice en el pitch /
   se dice como visión / no se dice).
4. **Referentes de microseguro inclusivo** — lemonade.org, Pula, MicroEnsure y casos
   Latam. Output: 2 datos duros para el bloque de impacto (76% categoría A).

Cada frente es un agente en paralelo (~1 sesión). Prioridad si hay que recortar:
1 y 3 (alimentan demo y pitch directamente).
