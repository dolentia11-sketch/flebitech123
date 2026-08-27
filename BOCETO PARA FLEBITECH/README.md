<p align="center">
  <img width="1500" height="600" alt="Banner Scala Labs — Hackathon Colsubsidio × 30X" src="https://github.com/user-attachments/assets/b32af668-9cdc-4b69-af04-47453fff23ab" />
</p>

<h1 align="center">Amparito by Scala Labs</h1>
<p align="center"><b>Un asesor de seguros en WhatsApp que lleva a la persona de "no sé qué seguro necesito" a "quedé asegurado", ya quedé asegurado" sin que tenga que hablar con nadie y con soporte 24/7.</b></p>

<p align="center">
  <img alt="Hackathon" src="https://img.shields.io/badge/Hackathon-Colsubsidio%20%C3%97%2030X-0067B1">
  <img alt="Reto" src="https://img.shields.io/badge/Reto%2002-Venta%20automatizada%20de%20seguros-FFD000?labelColor=575756">
  <img alt="Estado" src="https://img.shields.io/badge/Estado-MVP%20en%20construcci%C3%B3n-0067B1">
  <img alt="Repositorio" src="https://img.shields.io/badge/Repositorio-Público-575756">
</p>

---

Repositorio del equipo **Scala Labs** para la Hackathon Colsubsidio × 30X (22–26 jul 2026). Parte de los activos son **preexistentes** (registrados en la Bitácora de PI en Notion) y el resto se construye durante el evento.

## Contenido

- [El reto](#el-reto)
- [La solución](#la-solución)
- [Ver el demo](#ver-el-demo)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Stack](#stack)
- [Flujo de trabajo](#flujo-de-trabajo)
- [Equipo](#equipo)
- [Propiedad intelectual](#propiedad-intelectual)
- [Centro de mando](#centro-de-mando)

## El reto

Hoy, comprar un seguro en Colsubsidio exige un asesor comercial: no escala, no está disponible 24/7 y la experiencia es inconsistente. El reto es llevar al potencial cliente desde *"no sé qué seguro necesito"* hasta *"ya quedé asegurado"* **sin que tenga que hablar con nadie**, ayudándolo a encontrar la opción más adecuada dentro de la oferta de varias aseguradoras.

## La solución

**Jarvis**, un asesor conversacional que se interesa en conocerte, entiende qué seguro buscas o te sugiere el que encaja con tu momento de vida y tu bolsillo, te lo explica sin tecnicismos y te deja asegurado.

> **Regla de arquitectura:** el modelo de lenguaje **conversa y explica**; un **motor determinista** pone las cifras (propensión y cotización). Así cada recomendación tiene un porqué auditable. Nada de caja negra.

## Ver el demo

El frontend del producto es un sitio autónomo de un solo archivo:

```
producto/demo/index.html   →  doble clic para abrirlo en el navegador
```
```
Y puedes ingresar y probarlo aquí:
```
https://amparitohelp.netlify.app/

Incluye inicio, el chat de cotización, documentación, equipo y privacidad. El chat llama a un webhook de Make que consulta el motor; mientras el motor no está conectado, corre un guion de respaldo por producto para que el recorrido nunca se vea roto.

## Estructura del repositorio

```
Scala_Labs/
├── producto/                 # Lo que corre: el producto
│   ├── demo/                 #   Frontend del asistente (index.html + logos)
│   ├── engines/              #   Motor de scoring / cotización
│   └── recursos-marca/       #   Marca aplicada al producto
├── proceso-dt/               # El proceso (design thinking) y el pitch
│   ├── 1-ideacion/           #   Ideas, matriz de escenarios, motor de scoring, propuestas MVP
│   ├── 2-definicion/         #   Reto elegido, dossier, backlog & DoR
│   ├── 3-diseno/             #   Lenguaje del asistente, guion, scoring
│   ├── 4-testing/            #   Pruebas y feedback
│   ├── 5-pitch/              #   Pitch: escenas, guion de voz, video
│   └── recursos-marca/       #   Brandbook Colsubsidio (BRAND.md, logos, paleta)
└── pi-preexistente/          # IP previa al evento, registrada por autor
```

## Stack

Interfaz conversacional (WhatsApp / chat web) · un modelo de lenguaje para la conversación · un **motor determinista en Python** para las cifras · orquestación en **Make** (n8n como plan B) · bases de datos sanitizadas. Marca oficial de Colsubsidio (`proceso-dt/recursos-marca/BRAND.md`).

## Flujo de trabajo

- **Ramas + Pull Request.** Cada quien trabaja en su rama y abre un PR; los merge a `main` los centraliza el dueño del repositorio.
- **Código aquí, decisiones en Notion.** *Decisión que no queda escrita, no se tomó.*
- **Nunca** subir llaves ni archivos `.env`. Las API keys van en variables de entorno o en Make/n8n, jamás en el código.
- Stand-up de 15 min en la mañana y cierre de 10 min en la noche (bitácora + commit).

## Equipo

| Persona | Rol |
|---|---|
| Juan Diego Carvajal | Producto y orquestación |
| Daniel Rojas | Datos y motor |
| Sebastián | Desarrollo del motor |
| Carolina Pinzón | Dominio de seguros |
| Juan Pablo Jara | Investigación y estrategia (Scrum) |

## Propiedad intelectual

Repositorio **privado**. Los activos preexistentes al evento están registrados en la Bitácora de PI (autor y fecha) en Notion; el resto se construye durante la hackathon. Firma y pago se **simulan** en el MVP (el reto los excluye) y se documentan como camino a producción.

## Centro de mando

Notion — página raíz del equipo: <https://jddevs.notion.site/Hackathon-Colsubsidio-2026-Scala-Labs-3a4aaa9c5e0b818cb1d0f13475744ca1?source=copy_link>
