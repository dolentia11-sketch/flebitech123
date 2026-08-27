# Guion de voz en off — ElevenLabs (video pitch 2:00)

**Guion congelado 25-jul madrugada.** Tono: comercial emotivo — cálido, cercano,
seguro; NUNCA voz de locutor de promociones. Piensa en el narrador de un
documental corto de marca: habla bajo, con convicción. Español neutro
latinoamericano (acento colombiano suave bienvenido).

## Configuración sugerida en ElevenLabs

- **Modelo:** Eleven v3 (o Multilingual v2 si v3 no está disponible)
- **Voz:** femenina o masculina cálida en español — buscar en Voice Library
  "Spanish (Latin America) · warm · narration". Generar 2-3 candidatas y elegir.
- **Ajustes:** Stability ~35-40% (deja respirar la emoción) · Similarity ~75% ·
  Style 25-35% · Speaker boost ON.
- Generar **por bloques separados** (5 audios): permite ajustar el timing de
  cada escena en edición sin regenerar todo.

## Versión para PEGAR en ElevenLabs (números en letras, pausas con puntuación)

### Bloque 1 · Hook (objetivo: 20s)

Nadie se despierta queriendo comprar un seguro. Camila tampoco: veintinueve años, dos hijos. La idea le suena cara, enredada, llena de papeleo y asesores. Y como el sesenta y dos por ciento de los colombianos, nunca ha cotizado uno. Por eso, en dos mil veintiséis, nueve de cada diez hogares siguen desprotegidos. Esto no es falta de necesidad… es que nadie les ha mostrado lo simple que puede ser.

### Bloque 2 · Qué construimos (objetivo: 20s)

Por eso construimos un asesor que funciona como una conversación, y decide como un actuario. Le hablas con tus palabras; él cruza tu edad, tu familia y tu ingreso, y te entrega la mejor recomendación posible — explicándote por qué ese seguro, y no otro. Sin letra pequeña. Y en tres minutos, tienes tu primera póliza… con todas las de la ley.

### Bloque 3 · Demo (objetivo: 45-48s de voz repartida en 50s — dos actos)

Míralo en vivo. Camila no sabe qué necesita — el asesor se lo descubre en cinco preguntas. Prima ajustada a su ingreso, el porqué claro, consentimiento… y su primera póliza.

Pero en esos mismos tres minutos pasó algo más: el asesor construyó el expediente de Camila. Sus datos de siempre — familia, trabajo, contacto — y los que nadie captura: qué la hizo decidir, con qué palabras habla, qué la preocupa… y qué sueña. Y eso, es oro.

### Bloque 4 · Por qué importa (objetivo: 10s)

Porque vender seguros veinticuatro siete no es atender un chat: es saber a quién venderle, y cómo hablarle. Cada conversación se lo enseña al sistema: entre más conversa, mejor vende.

### Bloque 5 · Cierre (objetivo: 20s)

¿Y los asesores humanos? Son el corazón del piloto: tres meses entrenando al agente — y quedándose con los casos que merecen su tiempo. Somos Scala Labs, y esto es lo que creemos: la transacción la resuelve cualquier chatbot. La venta real es valor genuino y transparente — Colsubsidio lo entiende desde hace sesenta y nueve años. Y eso fue exactamente lo que construimos.

## Dirección de actuación por bloque (si usas Eleven v3 con audio tags)

- B1: arranque íntimo casi confesional; sube apenas en "nueve de cada diez";
  el remate lento, con pausa antes de "es que nadie…".
- B2: cambia a energía de solución — ritmo más ágil, sonrisa en la voz.
- B3 acto 1: tono de demostración, factual. Acto 2: baja la velocidad en
  "qué la preocupa… y qué sueña" — es el momento más humano del video.
- B4: convicción de tesis, la frase de negocio dicha sin afán.
- B5: el más emotivo. "Colsubsidio lo entiende desde hace sesenta y nueve años"
  con respeto genuino; "Y eso fue exactamente lo que construimos" — lento,
  definitivo, es la última frase del video.

## Nota operativa

No hay API key de ElevenLabs en el sistema. Dos caminos: (a) JP comparte
`ELEVENLABS_API_KEY` y Claude genera los 5 audios por API directamente a
`5-pitch/voz/`; (b) JP pega los bloques en elevenlabs.io y descarga los MP3.
La decisión ElevenLabs vs. voz de JP tipo Loom se toma el sábado tras el
feedback (ruta de producción en PITCH.md).

---
*Guion: congelado por JP. Preparación TTS y dirección: Claude Fable 5 (alto) · 25-jul-2026.*
