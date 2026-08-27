# Propiedad intelectual preexistente — Arquitectura Sierra Analytics (FreeMind Agents)

**Origen y titularidad:** arquitectura desarrollada por **Juan Pablo Ruiz Jara con su
equipo de FreeMind Agents (FMA), por fuera y antes de esta hackathon**. Se comparte
con el equipo Scala Labs como insumo de diseño para el Reto 02, bajo el marco de la
Bitácora de Propiedad Intelectual Preexistente del Notion del equipo (código de ética
y NDA): la PI corresponde a FMA/JP; su uso aquí es de referencia arquitectónica.

## Qué contiene

| Archivo (draw.io) | Qué es |
|---|---|
| `Modelo de capas.drawio` | El modelo de 9 capas (Capa 0 Estrategia → Capa 8 Observabilidad y Gobierno) |
| `Sierra_Analytics_Arquitectura_Completa.drawio` | Arquitectura completa con componentes por capa |
| `Sierra_Analytics_Arquitectura_Multivista.drawio` | Vistas múltiples: mapa general + detalle por capa |
| `Sierra_Analytics_Flujo_General.drawio` | Flujo end-to-end: usuario → planner → orquestador → microagentes → data → modelos → respuesta |
| `Diagrasma general.drawio` | Diagrama simplificado: request → planner → orquestador → agentes → data → API |

Se abren en [draw.io](https://app.diagrams.net/) o con la extensión Draw.io de VS Code.

## Por qué es relevante para el Reto 02

La tesis de la propuesta es que **la interfaz es intercambiable y la infraestructura
de datos es el producto**. Este modelo de capas es esa infraestructura, con lenguaje
de producción. Mapeo directo:

| Capa Sierra Analytics | Equivalente en la propuesta del reto |
|---|---|
| Capa 0 · Estrategia y generación de valor | El flywheel de datos y el modelo de negocio (marketplace) |
| Capa 1 · Interacción (Frontend, API Gateway, WebSocket, Auth) | La capa de presentación intercambiable: WhatsApp, billetera, web, asesor |
| Capa 2 · Planificación y orquestación (Planner, Orchestrator, State/Memory Manager) | La infraestructura agéntica (n8n + orquestador) y la memoria por usuario |
| Capa 3 · Microagentes | Los agentes del flujo: conversación, cotización, idoneidad |
| Capa 4 · Gestión de datos (Lake, Warehouse, Feature Store, Vector DB, RAG) | La DB única de trazabilidad + los scores de propensión (Feature Store) + el motor de compliance documental (RAG sobre clausulados) |
| Capa 5 · Modelos y algoritmos | El motor de scoring/propensión |
| Capa 6–7 · Ejecución ML + MLOps | El ciclo de reentrenamiento del flywheel: cómo los scores mejoran con cada conversación sin romper producción |
| Capa 8 · Observabilidad y Gobierno | Trazabilidad regulatoria: idoneidad, consentimiento, hash, evidencia ante SFC/Colsubsidio |

**Uso sugerido en la hackathon:** no construir las 9 capas (imposible en 3 días) —
usarlas como el "camino a producción" del cierre del pitch: el MVP demuestra las
capas 1–4 en miniatura; la arquitectura muestra que sabemos a dónde escala.

> Registrado como PI preexistente el 23-jul-2026. Los archivos fuente y su historia
> de construcción viven en los sistemas de FMA.
