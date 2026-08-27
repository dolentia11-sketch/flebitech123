# Arranque de MVP — Reto 01 y Reto 02

**Hackathon Colsubsidio 2026 · Scala Labs** · Elaborado 21 jul 2026

Esto es el punto de partida para construir del viernes 24 al domingo 26. Trae la arquitectura, los artefactos que ya corren y el plan por día para los dos retos. No es teoría: el motor de crédito y el de seguros ya generan salidas reales, y la demo HTML abre en el navegador con la misma lógica. Se decide reto el Día 1 y se arranca sobre lo que aplique.

Los archivos están en `OUTPUTS/Hackathon-Colsubsidio/mvp/`:

```
mvp/
├── reto01-credito/   scoring_engine.py · schema_credito.sql · n8n_flow_credito.json · gemini_prompts_credito.md
├── reto02-seguros/   quote_engine.py   · schema_seguros.sql · n8n_flow_seguros.json · gemini_prompts_seguros.md
└── demo/             index.html  (funnel de seguros + flujo de crédito, clicable)
```

## Arquitectura común (sirve para los dos retos)

Los dos retos comparten el mismo patrón, así que el equipo aprende una arquitectura y la reusa. La regla de oro: **el modelo de IA nunca pone las cifras; las pone un motor determinista en Python.** Así el jurado no ve alucinaciones y las cuentas quedan trazadas.

```
Frontend (chat/pantalla)
        │  HTTP
   n8n (orquestador)
        ├── Motor Python (scoring / cotización)  → cifras y decisión
        ├── Gemini API (agente)                  → conversación y redacción
        └── Base de datos                        → trazabilidad (oferta / póliza)
```

El agente Gemini conversa y redacta; el motor Python decide y calcula; n8n conecta y aplica las reglas de cumplimiento (consentimiento antes de personalizar o emitir); la base de datos deja evidencia. Ese "deja evidencia" es lo que responde a la pregunta más peligrosa del jurado: *¿por qué esta oferta / este seguro?*

## Reto 01 — Crédito hiperpersonalizado

**Lo que el jurado ve funcionando:** eliges un afiliado, el sistema lo segmenta, calcula un score y devuelve una oferta concreta (producto, monto, tasa por categoría A/B/C, plazo, cuota y canal) con la lista de razones de por qué esa oferta y no otra.

**Flujo UX (3 pantallas):** perfil del afiliado → oferta generada con medidor de score y justificación → vista del mensaje que saldría por el canal oportuno (WhatsApp/App/Email).

**Componentes:**

- `scoring_engine.py`: segmenta (Consolidado / Crecimiento / Nuevo por activar / Reconstrucción), calcula score 0-100 con reglas explicables y arma la oferta con tope por capacidad de pago (cuota ≤ 30% del ingreso). Ya corre: `python3 scoring_engine.py`.
- `schema_credito.sql`: tablas `afiliado`, `oferta`, `evento_interaccion`. El campo `consentimiento_datos` bloquea la personalización sin Habeas Data.
- `n8n_flow_credito.json`: webhook → chequeo de consentimiento → motor → Gemini → guarda → responde. Importable en n8n.
- `gemini_prompts_credito.md`: el agente redacta la oferta ya calculada, con prohibición de cambiar cifras.

**Diferenciador para puntuar:** transparencia. La mayoría muestra una oferta; nosotros mostramos la oferta y su porqué, trazado en base de datos. Eso ataca de frente la duda del jurado sobre "personalización de caja negra".

## Reto 02 — Venta automatizada de seguros

**Lo que el jurado ve funcionando:** un chat le hace máximo 5 preguntas, detecta su necesidad, recomienda un producto del catálogo, calcula la prima, muestra la idoneidad y —con su consentimiento— lo deja asegurado con número de póliza. Todo sin un humano.

**Flujo UX (un solo hilo):** chat de necesidad → cotización con cobertura y prima → consentimiento → "quedaste asegurado" con póliza.

**Componentes:**

- `quote_engine.py`: recomienda producto según la preocupación, escala la cobertura por dependientes e ingreso, aplica factor de edad y emite solo con aceptación y consentimiento. Ya corre: `python3 quote_engine.py`.
- `schema_seguros.sql`: `producto_seguro`, `conversacion`, `cotizacion`, `poliza`. La póliza no se emite sin `consentimiento`.
- `n8n_flow_seguros.json`: webhook de chat → Gemini (detecta necesidad) → motor de cotización → chequeo aceptación+consentimiento → emite. Importable.
- `gemini_prompts_seguros.md`: agente que pregunta poco, no inventa primas y practica venta adecuada.

**Diferenciador para puntuar:** el cierre 24/7 real con registro de idoneidad y consentimiento. Convierte la objeción regulatoria ("¿se puede vender sin humano?") en un punto a favor: sí, y queda la evidencia de que fue una venta adecuada.

## Plan de build (vie 24 – dom 26)

Cada bloque termina en algo que se puede mostrar. Si un bloque no cierra, se recorta alcance, no calidad del demo.

| Bloque | Ventana | Salida que se puede mostrar |
|--------|---------|-----------------------------|
| Esqueleto técnico | Vie 24 mañana | Repo con motor Python corriendo local y n8n importado |
| Motor + datos demo | Vie 24 tarde | El motor del reto elegido devuelve salidas para 3 perfiles |
| Agente Gemini | Sáb 25 mañana | Gemini conversa/redacta conectado a n8n con una API key |
| Frontend / funnel | Sáb 25 tarde | Pantalla o chat que llama al flujo y muestra el resultado |
| Integración punta a punta | Sáb 25 noche | Un usuario entra y sale con oferta o póliza, guardado en DB |
| Pruebas + bordes | Dom 26 mañana | Casos límite (sin consentimiento, mora alta, edad tope) controlados |
| Congelar + packaging | Dom 26 mediodía | Código congelado, bitácora de PI al día, video demo, deck de 3 min |

## Guion de demo (3 min, alineado a los 5 criterios)

1. **Problema y quién lo sufre (0:00–0:30) — impacto (30%).** Una frase con un afiliado real: acceso a crédito 35,5% o penetración de seguros 3,29% del PIB. A quién le cambia esto.
2. **La demo en vivo (0:30–1:45) — viabilidad técnica e implementación (40%).** Se recorre `demo/index.html`: un perfil entra y sale con oferta explicada o con póliza emitida. Se muestra la evidencia en base de datos.
3. **Cómo está hecho (1:45–2:30) — innovación (20%).** El patrón: motor determinista + agente que no inventa + cumplimiento embebido (consentimiento). Por qué eso es defendible y no humo.
4. **Cierre (2:30–3:00) — presentación (10%).** Qué sigue para llevarlo a producción en Colsubsidio y una línea de negocio. Se cierra con la acción, no con moraleja.

## Cómo correr los artefactos

```bash
# Motores (solo Python estándar, sin instalar nada)
python3 mvp/reto01-credito/scoring_engine.py
python3 mvp/reto02-seguros/quote_engine.py

# Demo navegable: abrir en el navegador
mvp/demo/index.html

# n8n: Import from File → n8n_flow_credito.json o n8n_flow_seguros.json
# Base de datos: correr schema_*.sql en SQLite o Postgres
# Gemini: pegar los prompts de gemini_prompts_*.md y setear GEMINI_API_KEY en n8n
```

## Siguiente paso

Día 1, tras votar el reto: asignar los bloques del plan a cada dueño y correr el motor del reto elegido con un dato real del equipo para validar que las cifras tienen sentido antes de conectar el frontend.
