# PITCH — video pregrabado 2:00 (guion v2 · hook congelado 24-jul)

**Formato decidido (JP)**: tipo Loom — cámara de JP en burbuja sobre la pantalla,
un solo take si sale bueno. Hook híbrido (persona + dato). Cierre piloto + flywheel.

**Regla de oro del guion**: cada bloque tiene SU tiempo. Ensayar con cronómetro
hasta que suene natural (consejo literal de la jurado). ~2,6 palabras/segundo.

---

## Guion por bloques

### ⏱ 0:00–0:20 · HOOK + PROBLEMA (~64 palabras — ensayar brisk, tolerancia +2s)

> Nadie se despierta queriendo comprar un seguro. Camila tampoco: 29 años,
> 2 hijos. La idea le suena cara, enredada, llena de papeleo y asesores. Y como
> el 62% de los colombianos, nunca ha cotizado uno. Por eso, en 2026, 9 de cada
> 10 hogares siguen desprotegidos. Esto no es falta de necesidad: **es que nadie
> les ha mostrado lo simple que puede ser.**

*[TEXTO CONGELADO por JP (24-jul tarde) — redacción final suya. Ángulo: el
paradigma (nadie piensa en seguros; los cree caros/complejos), no "falla de
canal". Camila = persona 100% sintética (nombre inventado, rostro generado).
Cifras y fuentes: **62% nunca cotiza** (Aseguradora Solidaria, campo dic-2024→
may-2025, vía El Tiempo/El Colombiano) · **90,7% hogares sin seguro de hogar**
(Fasecolda mar-2026 × viviendas DANE, vía Semana). El 0,24% queda RETIRADO
(dato 2017, Superfinanciera vía El Tiempo — desactualizado: en 2023 el 27,5% ya
se comercializó no presencial, URF+PNUD). Detalle completo:
`investigacion/2026-07-24_verbalizacion-problema-pitch.md`.]*

### ⏱ 0:20–0:40 · QUÉ CONSTRUIMOS (~56 palabras · CONGELADO 24-jul tarde)

> Por eso construimos un asesor que funciona como una conversación y decide como
> un actuario. Le hablas con tus palabras; él cruza tu edad, tu familia y tu
> ingreso, y te entrega la mejor recomendación posible — explicándote por qué
> ese seguro y no otro. Sin letra pequeña. Y en 3 minutos, tienes tu primera
> póliza — con todas las de la ley.

*[Ajuste JP 24-jul noche: cierre "tu primera póliza — con todas las de la ley"
(antes "la póliza está a tu nombre"). En pantalla, al decir "las de la ley",
aparecen 3 sellos REALES del repo: ✓ Consentimiento explícito (gate en
quote_engine.emitir) · ✓ Venta adecuada (nota de idoneidad del motor) ·
✓ Datos protegidos · Ley 1581. NO mostrar firma Ley 527 / PCI / retracto /
verificación de identidad (no existen; el brief los excluye). Inventario
completo para Q&A: `investigacion/2026-07-24_inventario-cumplimiento-legal.md`.]*

*[TEXTO CONGELADO por JP. Decisiones: (1) "decide como un actuario" carga el
rigor técnico — "motor determinista" se reserva para el Q&A (si preguntan "¿cómo
decide?": motor determinista, reglas trazables, la IA nunca pone cifras);
(2) "cruza tu edad, tu familia y tu ingreso" = variables reales del motor que
corre hoy (quote_engine.py); (3) "WhatsApp" sale de la voz (no hay conector en
el repo) — la promesa de canal se muda a la E4 como tesis de infraestructura
("cambiar de chat a WhatsApp es cambiar un conector, no el motor", SC-006);
(4) coletilla pendiente del veredicto de Jorge (meet 24-jul 5:15pm): si
firma/pasarela REALES entran → insertar "con firma digital y pago en el mismo
chat" antes de "Tres minutos"; si SIMULADO → la frase queda como está;
(5) si el sábado se integran los 26 seguros del catálogo al motor → puede
insertarse "contra 26 seguros" tras "tu ingreso". En pantalla: mockup del chat
(escena E2).]*

### ⏱ 0:40–1:30 · DEMO EN DOS ACTOS (CONGELADO 25-jul madrugada)

**Acto 1 — La venta (0:40–1:05):**

> Míralo en vivo. Camila no sabe qué necesita — el asesor se lo descubre en
> 5 preguntas. Prima ajustada a su ingreso, el porqué claro, consentimiento…
> y su primera póliza.

**Acto 2 — El expediente (1:05–1:30):**

> Pero en esos mismos 3 minutos pasó algo más: el asesor construyó el expediente
> de Camila. Sus datos de siempre — familia, trabajo, contacto — y los que nadie
> captura: qué la hizo decidir, con qué palabras habla, qué la preocupa y qué
> sueña. Y eso es oro.

*[Pantalla: mockup animado calidad-final (`escenas/E3-demo.html`) → se reemplaza
por screen recording real cuando el demo esté grabable. Cronómetro visible
cerrando en ~2:47. Acto 2 = la pantalla "esto aprendió el sistema de Camila"
(el equipo la hace visible el sábado). ⚠️ "Míralo en vivo" solo es válido con
material real — si al final queda mockup, cambiar a "Así funciona".]*

### ⏱ 1:30–1:40 · POR QUÉ IMPORTA (CONGELADO — el stack se muda a la pantalla)

> Porque vender seguros 24/7 no es atender un chat: es saber a quién venderle
> y cómo hablarle. Cada conversación se lo enseña al sistema: entre más
> conversa, mejor vende.

*[El diagrama del flywheel (`escenas/E4-flywheel.html`) carga el stack en labels
(Python · DANE · Fasecolda · trazabilidad): la voz dice el porqué, la pantalla
el cómo. "Motor determinista" se reserva para el Q&A.]*

### ⏱ 1:40–2:00 · CIERRE (CONGELADO con ajustes de JP)

> ¿Y los asesores humanos? Son el corazón del piloto: 3 meses entrenando al
> agente — y quedándose con los casos que merecen su tiempo. Somos Scala Labs,
> y esto es lo que creemos: la transacción la resuelve cualquier chatbot. La
> venta real es valor genuino y transparente — Colsubsidio lo entiende desde
> hace 69 años. Y eso fue exactamente lo que construimos.

*[**69 años** verificado: fundada en 1957 (ANDI, Bogotá; personería Res. 3.286
del 4-dic-1957 — Wikipedia/SuperSubsidio). "Estamos listos" ELIMINADO (decisión
JP). 💡 Idea GUARDADA para el pitch EN VIVO de finalistas: cerrar con QR de
"agenda nuestra reunión de onboarding" — el siguiente paso natural de
contratarnos. NO va en el video pregrabado.]*

---

## Storyboard para el video (Claude Design + screen recording)

La cámara de JP va en burbuja SIEMPRE (formato Loom). Esto es lo que va en pantalla:

| Escena | Tiempo | Visual en pantalla | Fuente |
|---|---|---|---|
| E1 | 0:00–0:20 | Apertura 0–3s: pantalla oscura solo con "Nadie se despierta queriendo comprar un seguro." → avatar sintético de Camila + chips (`29 años` `2 hijos`) → creencias apareciendo alrededor ("cara" "enredada" "papeleo" "asesores") → dato **62%** (Solidaria 2025) → cifra grande contador **90,7%** (Fasecolda · mar 2026) → remate en amarillo "nadie les ha mostrado lo simple que puede ser" | Claude Design (animación) — v2 sobre E1-hook.html |
| E2 | 0:20–0:40 | El chat aparece (mockup animado mientras no exista; screenshot real después) con la conversación iniciando | Claude Design → reemplazar por screenshot real |
| E3 | 0:40–1:30 | **Screen recording real del demo**, sin cortes, siguiendo el guion. Zoom suave en: pantalla de precio, consentimiento, número de póliza, consulta de DB | Grabación del demo (depende de T018) |
| E4 | 1:30–1:40 | Diagrama animado del flywheel: conversación → data → motor → mejor venta → (loop). Paleta de marca | Claude Design (animación) |
| E5 | 1:40–2:00 | Equipo (foto/avatares + roles en 1 línea) → cierre con logo Colsubsidio×30X y "Estamos listos" | Claude Design |

**Especificaciones**: 16:9 · paleta `recursos-marca/` (fondo oscuro — no hay logo
para fondo claro) · texto en pantalla mínimo y grande (la jurado: bullets, no
paredes de texto) · subtítulos quemados (se ve sin audio en la plataforma).

## Producción — checklist

- [ ] Guion v2 con la voz de JP (leerlo en voz alta y marcar lo que no suene a él)
- [ ] Ensayo con cronómetro: cada bloque en su tiempo (tolerancia ±2s)
- [ ] Escenas E1/E2/E4/E5 generadas con Claude Design (se pueden hacer YA, sin demo)
- [ ] E3: screen recording del demo real sin cortes (bloqueado por T018 — integración)
- [ ] Grabación Loom: buena luz, micrófono cerca, energía alta, contacto a cámara
- [ ] Edición: burbuja + escenas + subtítulos (CapCut o similar)
- [ ] Backup: exportar y subir ANTES del cierre del domingo; probar reproducción
- [ ] Página de preguntas de finalistas (¿3 meses? ¿stack? ¿mercado? ¿competidores?) — el dossier ya las responde; condensar en 1 página

## Pendientes de decisión

- Link de la plataforma del evento (registro del equipo + subida) — buscar en el grupo general
- ¿Quién graba la voz/cámara de respaldo si JP queda como finalista presencial?

---

*Guion v1 asistido por Claude Fable 5 (esfuerzo alto) sobre decisiones creativas
de JP (hook híbrido, formato Loom, cierre piloto+flywheel) · 2026-07-24*

---

## 🎬 CHANGELOG v2 — `video/pitch-scala-labs-v2.mp4` (25-jul noche)

Feedback aplicado (mentores + JD + discovery 25-jul). **La voz NO se regeneró** —
todo es visual/timing. Cambios que requerirían regrabar quedan en "Decisiones
pendientes de JP" (abajo).

**Naming y lenguaje (feedback mentor):**
- El personaje ahora es **"Amparito · tu asesora digital de confianza"** en la
  cabecera del chat de E2 y E3 (antes "Asesor de seguros").
- **"actuario" eliminado de pantalla** (E2: "Decide como un actuario" →
  "Decide con rigor matemático · reglas claras y auditables"). La voz aún lo
  dice — ver pendientes.

**Modelo de remisión (hallazgo de JP, discovery 25-jul):** Colsubsidio no
recauda ni emite. En E2/E3 el cierre del chat ya NO muestra pago/firma:
- Chips "✓ Firma electrónica / ✓ Pago aprobado" → "✓ Lead validado /
  ✓ Solicitud remitida a la aseguradora".
- Tarjeta final "Quedaste asegurada · PÓLIZA POL-905446" → "Solicitud enviada
  a la aseguradora · SOL-905446 · confirmación a tu correo".
- Mensaje de consentimiento: "¿Confirmas que enviemos tu solicitud a la
  aseguradora?" (antes "¿Confirmas la compra?").
- E2 k6: "3 minutos → tu seguro en camino" (antes "tu primera póliza").

**Diferenciación explícita (feedback mentor de pitch):**
- E3 (cola del acto 2): badges **"Expediente vivo del cliente"** y **"Motor que
  aprende de cada conversación"** (27.9s/28.7s de la escena).
- E4: panel **"HOY → CON AMPARITO"** con los números del discovery (tal cual):
  contacto→cotización **8 días → minutos** · feedback aseguradoras **1 Excel al
  mes → labels en tiempo real** · pie: **1.200 leads/mes · 15% conversión ·
  CAC $40.000** (fuente: discovery 25-jul).

**Silencio incómodo 1:18–1:25 (feedback JD) — diagnóstico y solución:**
La voz del bloque 3 termina en 1:18.6 y la del bloque 4 arranca en 1:22.3
(~3.7s de aire que caían sobre pantalla casi estática). Además la transcripción
palabra-a-palabra reveló que los MP3 se cortaron en fronteras distintas al
guion: el bloque 2 TERMINA con "Míralo en vivo…" y el bloque 4 ARRANCA con
"Y eso es oro". Solución visual: la cola de E3 ahora encadena remate "Y eso es
oro." (27.0s) + los 2 badges de diferenciación (27.9/28.7s), y E4 abre con el
panel HOY→AMPARITO animado desde 0.5s — no queda pantalla muerta. Sin cama
musical: **no hay pista de música licenciable en el sistema** (se buscó);
pipeline de mezcla listo abajo.

**Desalineaciones voz↔pantalla (feedback JD)** — verificado con transcripción
word-level (faster-whisper) de los 5 bloques y corregido:
- **E1**: remate "es que nadie les ha mostrado…" 21.3s → 23.3s (la voz lo dice
  en 23.5s).
- **E2**: las claves iban 3–5s tarde. Retimed: "rigor" 4.0s · chips 7.8s ·
  "por qué ese seguro" 13.0s · "sin letra pequeña" 15.9s (voz: 15.9s) ·
  "3 minutos" 17.6s (voz: 17.5s) · tarjeta final 19.3s · sellos ley 20.3s
  (voz "las de la ley": 20.2s) · nueva clave "Míralo en vivo →" 22.2s (la voz
  lo dice en 22.0s, dentro del bloque 2).
- **E3**: acto 1 comprimido a ritmo timelapse real: reco 3.7s (voz "prima
  ajustada" 2.8s) · porqué 4.8s (voz 4.8s) · consentimiento 6.0s (voz 6.1s) ·
  solicitud enviada 8.6s (voz "su primera póliza" 8.5s) · acto 2 entra 9.6s
  (voz "pero en esos mismos 3 minutos" 9.3s) · "datos de siempre" 15.0s (voz
  15.3s) · filas sincronizadas (contacto 18.5s = voz 18.5s) · filas oro 21.2 /
  22.6 / 24.1 / 25.3s (voz: 21.2 / 22.7 / 24.2 / 25.3s).
- **E5**: nuevo beat **"Somos Scala Labs."** en 9.0–11.2s — la voz lo dice en
  9.3–10.4s y la pantalla quedaba en velo vacío.
- Micro-fix técnico en E3 (reloj del cronómetro anclado al primer frame del
  rAF — elimina el salto del timer en render headless).

**Cama musical (pendiente de pista de JP)** — cuando exista `musica.mp3`:
```bash
ffmpeg -y -i pitch-scala-labs-v2.mp4 -i musica.mp3 \
  -filter_complex "[1:a]atrim=0:119.6,volume=-22dB,afade=t=in:st=0:d=2,afade=t=out:st=115.6:d=4[m];\
[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k pitch-scala-labs-v2-musica.mp4
```

## 🔶 DECISIONES PENDIENTES DE JP

**1. One-liner más simple (feedback mentor: el actual es complejo).** Tres
opciones — el producto: chat que vende seguros 24/7, perfila en ≤5 preguntas,
recomienda con su porqué y remite el lead listo a la aseguradora en minutos:
- (a) **"Amparito convierte una conversación en un seguro: 5 preguntas, una
  recomendación con su porqué, y tu solicitud con la aseguradora en minutos."**
- (b) **"Un chat que vende seguros 24/7 — de '¿qué necesito?' a lead remitido
  en 3 minutos, no en 8 días."**
- (c) **"La asesora digital que nunca duerme: te perfila en 5 preguntas, te
  explica el porqué y deja tu seguro en camino en minutos."**

**2. Frases de la VOZ actual desalineadas con los cambios** (por si JP quiere
regrabar en ElevenLabs web, ~10 min — bloques afectados: 2 y 3):
- B2 dice **"un asesor que… decide como un actuario"** → pantalla ya dice
  Amparito y sin "actuario". Reemplazo propuesto: *"Por eso construimos a
  Amparito: una asesora que funciona como una conversación y decide con rigor
  matemático."*
- B2 dice **"tienes tu primera póliza — con todas las de la ley"** y B3
  **"…y su primera póliza"** → modelo remisión (Colsubsidio no emite). Es
  DEFENDIBLE sin regrabar porque la pantalla muestra la secuencia correcta
  (consentimiento → solicitud → aseguradora → confirmación al correo), pero si
  se regraba: B2 *"Y en tres minutos, tu solicitud ya está con la aseguradora —
  con todas las de la ley."* · B3 *"…consentimiento… y su solicitud remitida."*
- B3 dice **"el asesor"** (2 veces) → *"Amparito se lo descubre en cinco
  preguntas"* / *"Amparito construyó el expediente de Camila"*.
- Nota de refuerzo: el antes/después del discovery (remisión hoy manual por
  correo → automática en segundos) apoya exactamente este cierre de remisión —
  vale la pena decirlo en el Q&A aunque no se regrabe.

**3. Cama musical**: no hay pista en el sistema. Si JP consigue una (licencia
limpia), el comando de mezcla de arriba la monta a -22dB con fades en <1 min.

*v2 construida por Claude Fable 5 (esfuerzo alto): transcripción word-level de
la voz, retiming de las 5 escenas, re-render determinista Chrome headless
(3.588 frames, 30fps) + ensamble ffmpeg · 2026-07-25*

## ⏱ Tiempos v3 — escenas retimeadas a la voz real (El Faraón, 25-jul)

| Escena | Duración | Audio | Acumulado |
|---|---|---|---|
| E1 Hook | 26,5s | `voz/bloque-1-hook.mp3` | 0:00–0:26 |
| E2 Qué construimos | 25,4s | `voz/bloque-2-que-construimos.mp3` | 0:26–0:52 |
| E3 Demo (2 actos) | 30,0s (voz 26,7 + aire) | `voz/bloque-3-demo.mp3` | 0:52–1:22 |
| E4 Flywheel | 13,8s | `voz/bloque-4-flywheel.mp3` | 1:22–1:36 |
| E5 Cierre | 23,9s | `voz/bloque-5-cierre.mp3` | 1:36–2:00 |

**Total: 119,6s ≈ 2:00** ✅. Los beats de cada escena están sincronizados a las
pausas reales del audio (analizadas con silencedetect). E3 acto 1 quedó en modo
"timelapse" (ráfaga rápida de chat — la voz lo cubre: "se lo descubre en 5
preguntas"). Si se cambia a la voz de JP (decisión post-feedback), se repite el
retiming con el mismo método.

## Ruta de producción acordada (JP, madrugada 25-jul)

1. **Voz en off ElevenLabs** (estilo comercial emotivo) sobre el guion congelado
   → `guion-voz-elevenlabs.md`. Pendiente: API key de JP (no hay en el sistema)
   o generar en la web de ElevenLabs pegando el guion anotado.
2. **Animaciones calidad-final** de TODAS las escenas (E3 con mockup de producto
   suficientemente bueno para pasar como final; solo se intercambian los mockups
   por renders/grabación real después).
3. **Sábado:** ronda de feedback del pitch (equipo + mentora Emmy) → ajustes.
4. **Después del feedback:** efectos de sonido + música de fondo.
5. **Decisión final:** mantener VO de ElevenLabs o JP graba tipo Loom (burbuja
   de cámara) acompañando las animaciones.
6. Ajuste fino de timing voz↔animación: AL FINAL, con la voz definitiva.
