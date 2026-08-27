# Charla "Gana el mejor pitch" — insights accionables para Scala Labs

**Fuente**: youtube.com/watch?v=QICdEq8shoQ (43 min, 30X AI Devs, 2026-07-23).
Ponente: Ángela (ex-Platzi/escuela de blockchain; ganadora, organizadora y **jurado
activa de hackathons**). Modera: Sandra (30X, ayudó a estructurar los retos con
Colsubsidio). Transcripción extraída de los subtítulos oficiales.

---

## 🚨 Lo que cambia supuestos del equipo

1. **El pitch es PREGRABADO y dura 2 MINUTOS — no 3 en vivo.** Sandra (23:00):
   habrá una plataforma (se compartía "hoy" 23-jul) donde los equipos se registran
   y el domingo suben el proyecto; el pitch va en video pregrabado. **Los
   finalistas** sí presentan en vivo ante el jurado final (formato tipo Global).
   → Ajustar: SC-002 de la spec habla de "guion de 3 minutos"; el guion del demo
   (T024) y el track de pitch (T028–T030) deben apuntar a **video de 2:00**.
2. **La inscripción es en esa plataforma**: crear el equipo + subir proyecto
   (link de demo funcional + repo + video) antes del cierre del domingo. Conecta
   con el pendiente de inscripción del equipo (aún sin dueño).
3. **Los jueces NO ven el código primero.** Escuchan todos los pitches, hacen su
   shortlist y *después* revisan repo/código. "Tu pitch abre la puerta; el código
   solo confirma que lo que dijiste es cierto" (29:00).

## La estructura exacta del pitch de 2 minutos (de una jurado real)

| Bloque | Tiempo | Qué va |
|---|---|---|
| Hook + problema | 20 s | Pregunta fuerte o dato duro. PROHIBIDO abrir con "hola, me llamo…" — "si en los primeros 20 segundos hablaste de ti, estás en problemas" |
| Qué construiste | 20 s | El producto en UNA frase + qué lo hace distinto. Caso de uso central, **no lista de features** |
| Demo | 50 s | El flujo real de punta a punta del caso central ("muestra la sala, no toda la casa") |
| Stack + por qué importa | 10 s | Qué usaron, **cómo resolvieron el problema** y por qué Colsubsidio/30X deberían seguir desarrollándolo |
| Equipo + qué sigue + cierre | 20 s | Quiénes son (1 línea), siguiente paso concreto (ej. piloto de 3 meses), call to action |

**Su ejemplo completo** (24:56): abre con "4,8 millones de hogares en déficit de
vivienda… ¿cuántos califican a un subsidio y nunca lo reclaman? No por plata:
por falta de información" → "Construimos Mi Subsidio: en 3 preguntas te dice a
qué calificas y te arma la solicitud" → demo → stack → "si logramos solo el 5%
de quienes no reclaman, son 100.000 familias" → equipo + piloto + cierre.

**Traducción directa a nosotros**: nuestro hook ya existe — *"En Colombia solo
el 0,24% de las pólizas se vende por canal digital y 9 de cada 10 hogares no
tienen seguro de hogar. No es falta de necesidad: es falla de canal."* → "Construimos
un asesor en WhatsApp que te deja asegurado en menos de 3 minutos" → demo del
camino 1 (afiliada monoparental) → stack con el flywheel ("cada conversación deja
data trazable que reentrena el motor") → equipo + piloto con afiliados.

## Producción del video (recomendaciones concretas)

- **Grabar la pantalla del demo y poner la voz encima** (CapCut, el celular, lo
  que sea). Si hay presentación en vivo (finalistas), tener SIEMPRE el video de
  backup por si falla el wifi.
- Ensayar con cronómetro hasta que suene natural. Energía y contacto visual.
- Slides visuales: bullets y no "paredes de texto"; imágenes > texto.
- Contar una historia / analogía personal — conecta con cualquier jurado.
- Cierre fuerte con call to action.

## Qué hace que un jurado recuerde un pitch (dijo la jurado, 39:32)

- Hoy todos llegan con prototipos funcionales e interfaces limpias — eso ya no
  diferencia. Diferencia: **estructura + saber explicar CÓMO resolvieron el
  problema cuando preguntan**. "La mayoría responde 'no sé' — quien argumenta,
  puntúa".
- **Interfaz que no "huela" a AI genérica**: prefiere templates bien usados a
  diseño-AI obvio. Usar la IA "con criterio": plan mode, revisar el plan, comparar
  modelos — no dejar que "tome todas las decisiones por mí".
- Pasión + orden + datos.
- **Anticipar preguntas de finalistas**: ¿qué harías con 3 meses y equipo? ¿por
  qué ese stack? ¿tamaño de mercado? ¿competidores? (nuestro dossier ya responde
  las 4 — tenerlas listas en una página).

## README y repo (los jueces técnicos auditan DESPUÉS del shortlist)

- README raíz limpio con: sobre el proyecto · built with · cómo probarlo ·
  **link del demo desplegado** · link del video · roadmap ("qué haríamos en los
  3 meses del piloto") · licencia · contacto · agradecimientos (mentores).
- Si hay varios repos/carpetas, el README explica dónde está cada cosa.
- **Commits limpios** — "es mucho más fácil auditar commits limpios que un solo
  commit con todo el repo" (nuestra regla rama+PR ya nos cubre).
- **El demo debe estar desplegado y probable** por los jueces (Vercel/Netlify) —
  no basta el video. Coincide con lo que JD ya planeaba ("entorno cloud").

## Otros consejos del evento (contexto general)

- Hablar con mentores desde YA — "la IA la tienen todos los días; los mentores no".
- Escenarios 1/2/3: mínimo que funcione → +landing → +features (= constitución V).
- "Algo pequeño que funcione le gana a una idea enorme a medias. Simple gana."
- Tools sugeridas: v0 (prototipos), Vercel/Netlify (deploy), Neon/Supabase (DB),
  Excalidraw (diagramas), skills.sh (skills de agentes).
- Post-hackathon: post público con el proceso, etiquetar equipo/mentores/sponsors;
  usar el hackathon como validación si quieren continuar el proyecto.

---

*Transcripción vía subtítulos oficiales de YouTube + análisis con Claude Fable 5
(esfuerzo alto) · 2026-07-24. TXT completo disponible para el equipo.*
