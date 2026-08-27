# Plan del sábado 25 — un solo objetivo

> **A las 5 de la tarde, todo lo que construimos por separado funciona junto,
> de principio a fin, en un solo lugar. Después de las 5 no agregamos nada
> nuevo: solo probamos, grabamos y subimos.**

Esto es una hackathon: no necesitamos el producto más robusto del mundo.
Necesitamos un MVP completo que demuestre potencial de negocio y que puede
crecer sin riesgo. Como dijo JD: **mejor un MVP completo que uno a medias.**
El domingo es solo para ponerlo bonito, ensayar y entregar.

> **Veredicto del mentor Jorge (sesión del viernes):** *"Entorno simulado, con
> flujos automatizados, pero sobre bases de datos sanitizadas."* Es decir: firma
> y pago se SIMULAN (en el mensaje del producto se cuentan como visión), los
> flujos corren de verdad, y la base de Colsubsidio se usa limpia. Este plan
> está construido sobre ese veredicto.

---

## Priorización (idea de JD: matriz de Eisenhower)

**✅ MAÑANA (lo único que importa):** unir el motor + el chat + los datos en un
solo flujo que corra completo · el pago en modo prueba · el traspaso a humano
cuando aplica · **el uso visible de la base de datos de Colsubsidio**
(recomendación del mentor Jorge — ver "el bucle" abajo) · subir el demo a
internet · grabar el video del demo.

**📅 DOMINGO (si mañana cerramos bien):** pulir textos y colores · ensayar el
pitch · **preparar el repo para revisión con IA** (es probable que la primera
ronda de jurados use agentes para revisar todos los repos: README que explica el
proyecto de corrido, con cada afirmación enlazada al archivo que la prueba, un
índice para agentes, y una prueba con nuestro propio "juez simulado" — le damos
el repo en frío a un agente evaluador y corregimos lo que no entienda. Todo
honesto: facilitar la comprensión, nunca frases para manipular al evaluador) ·
revisión final · entrega en la plataforma.

**⏳ SOLO SI SOBRA TIEMPO (nadie lo arranca sin avisar):** sugerir seguros
adicionales después de la compra · afinar el mapa de prospección con más cortes.

**❌ NO ENTRA EN EL MVP (queda para después, según cómo avance el proyecto):**
meter los 26 seguros al motor (con los 11 que pesaron las expertas basta y
sobra) · entrenar modelos de machine learning con la data (el sistema YA captura
la data que lo hará posible — eso se cuenta como el siguiente paso natural) ·
automatizar la conexión Notion–GitHub · cualquier idea nueva que aparezca mañana
(se anota y se decide después).

---

## El bucle de retroalimentación (ya está adentro — solo hay que MOSTRARLO)

La venta de seguros no es solo el chat que cierra: es saber **a quién escribirle,
cuándo, con qué oferta y por qué**. Nuestro sistema ya resuelve la mitad de eso
desde el diseño, y mañana lo hacemos visible con dos piezas baratas:

1. **Lo que el sistema aprende en cada conversación.** Mientras Camila chatea,
   cada paso queda guardado: quién es, qué le interesó, qué seguro le gustó,
   cómo se le explicó, si compró o en qué momento se fue. Eso YA funciona (la
   base de trazabilidad que armó Daniel). En el demo se muestra al final: "esto
   aprendió el sistema de Camila en 3 minutos".
2. **El mapa de prospección con la base de Colsubsidio** (lo que pidió Jorge):
   corremos nuestro motor sobre la base real de afiliados y sacamos, por cada
   seguro, los grupos de personas con mayor afinidad. Resultado: una vista
   simple de "a quiénes vale la pena escribirles primero y con qué oferta". La
   base que "no servía" se convierte en el arranque del motor de prospección —
   eso es exactamente lo que el jurado quiere ver.

**¿Y el machine learning?** Hoy no hace falta y nos pondría en riesgo: la base
no trae la respuesta "compró/no compró", así que no hay de dónde aprender
todavía. Pero cada conversación del sistema FABRICA esa respuesta. El cuento
para el jurado es redondo: *"hoy decidimos con reglas expertas trazables;
con la data que el propio sistema genera, mañana esas reglas se vuelven
predicciones"*. Se vende la visión, se construye lo simple.

---

## Qué hace cada quien (máximo 3 cosas por persona)

### 🧠 Daniel (desde las 11am)
1. Enseñarle al chat a entender qué seguro pide la persona cuando escribe con
   sus palabras ("quiero un SOAT", "algo para mi perro"). **No es machine
   learning**: es comparar contra la lista de palabras que arma Caro. La guía
   exacta ya está escrita — Juan Pablo te la pasa.
2. Dejar el motor listo para que n8n (o Make) lo pueda llamar y recibir la
   respuesta.
3. Con Melissa: correr el motor sobre la base de Colsubsidio (ya limpia) y
   sacar el **mapa de prospección** (los grupos con mayor afinidad por seguro).
   Esto va en la tarde, cuando el flujo principal ya esté conectado.

### 🔧 Sebas
1. El pago en modo prueba: **la pantalla simulada con look real es lo acordado
   con Jorge** (entorno simulado). Si dentro de las mismas 2 horas alcanza a
   salir el sandbox de una pasarela real (Wompi o Mercado Pago en modo prueba),
   mejor — pero es un bonus, no la meta. Nadie pelea con una pasarela hoy.
2. El cierre de la compra: número de póliza + comprobante que queda guardado.
3. Apoyar a JD con el canal (WhatsApp o chat web).

### 🎛 JD
1. Armar el "director de orquesta" en n8n o Make: recibe el mensaje de la
   persona, le pregunta al motor, y devuelve la respuesta. *(Elige la
   herramienta con la que avances más rápido HOY — hay créditos de Make del
   evento, y Juan Pablo tiene "skills" de n8n para Claude que aceleran mucho;
   te las comparte.)*
2. Los textos que dice el asesor, con textos de respaldo por si la IA falla.
3. **El intento de WhatsApp de prueba, SOLO hasta la 1:30pm.** Si a esa hora no
   entra y sale un mensaje, lo soltamos sin drama: el demo va con el chat web
   (que ya existe) y WhatsApp se cuenta como el siguiente paso. El pitch no
   cambia nada.

### 🎨 Caro
1. Buena noticia: **el paso a paso ya casi lo tienes** — tu documento del
   asistente de venta (el de In Review, que ya distingue afiliado/no afiliado)
   ES el insumo. Mañana solo: completar la información ficticia que dijiste y
   revisar que las pantallas que genere Juan Pablo con Claude Design queden
   fieles a lo que definiste. Tú pones el contenido, la herramienta pone el
   dibujo.
2. La lista de palabras por seguro: cómo pide la gente cada producto ("SOAT",
   "moto", "carro", "perro", "gato", "mi familia"…). Es el insumo de la tarea 1
   de Daniel.
3. La lista de seguros que SÍ necesitan una persona (por su complejidad o
   requisitos) y las frases con que el asesor confirma el traspaso.

### 📊 Melissa (por chat, a tu ritmo)
1. Escribir 2 personas de ejemplo (edad, familia, ingreso…) con el resultado
   EXACTO que el motor debe darles — nuestra prueba de que nada se dañó al
   conectar todo (1 hora).
2. Cuando el flujo esté conectado (tarde): revisarlo contra los requisitos que
   definiste y comentar qué falta o qué sobra.
3. Con Daniel: el mapa de prospección sobre la base de Colsubsidio (tarde).

### 🎬 Juan Pablo
1. Reunión con Emmy: avance del pitch + las pantallas del chat (generadas con
   Claude Design sobre el paso a paso de Caro).
2. Conectar y probar todo de punta a punta (con los 2 ejemplos de Melissa).
3. Subir el demo a internet con un link que cualquiera pueda abrir + grabar el
   video del recorrido para el pitch.

---

## El traspaso a humano (reglas claras — la promesa es venta 24/7 SIN humanos)

El asesor **nunca ofrece hablar con una persona por iniciativa propia** — si lo
hiciera, la promesa de venta automatizada se debilita. El traspaso ocurre solo
en dos casos:

1. **El usuario lo pide** ("quiero hablar con alguien", "¿me pueden llamar?") →
   el asesor lo confirma con calidez y hace el traspaso (simulado en el demo).
2. **El usuario pide un seguro que exige intervención humana** (la lista la
   define Caro) → el asesor lo explica y conecta.

La idea de fondo (para el pitch): la persona es **un recurso más al que el
sistema puede acceder** — como consulta el motor o el catálogo. Una dupla
cuando aporta, nunca un reemplazo del flujo automático.

---

## Horario del día

| Hora | Qué pasa |
|---|---|
| 9:00 | Daily: validamos este plan (10 min) y arrancamos |
| 1:30 | Punto de control de 15 min: ¿WhatsApp sí o no? ¿pasarela sí o no? ¿algún frente trabado? |
| 5:00 | **Se congela**: no entra nada nuevo. Solo conectar, probar, grabar |
| Noche | Demo en internet + video grabado + revisión de que lo construido cumple lo prometido |

## No se nos puede olvidar

- **Registro en la plataforma (Hackradar)**: el cupo es de 5. Confirmar quién es
  "Juan Muñoz", que estén los 5 correctos y que nadie que deba estar quede por
  fuera (Melissa acordó entrar como apoyo).
- Si alguien se siente saturado o trabado más de 30 minutos: lo dice en el
  grupo. Nadie pierde una tarde peleando solo con algo.

---

*Plan preparado por JP (Scrum Master) con Claude Fable 5 (esfuerzo alto) ·
2026-07-24 noche · se valida en el daily del sábado 9:00am*
