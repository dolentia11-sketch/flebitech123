# Checklist Operativo de Onboarding — Hackathon Colsubsidio 2026

**Equipo:** Scala Labs (liderado por Juan Diego Carvajal) · **Fechas del evento:** 22–26 jul 2026 · **Modalidad:** virtual/híbrida

El objetivo de las primeras 48 horas es una sola cosa: llegar al viernes 24 con reto elegido, equipo con roles claros y entorno funcionando. Todo lo demás es construir. Este checklist se cierra antes de tocar código.

---

## 0. Antes del kickoff (hoy, 21 jul — lo hace Juan)

- [ ] Crear el repo en GitHub (privado) y la página raíz en Notion "Hackathon Colsubsidio 2026".
- [ ] Registrar la **PI preexistente** en la Bitácora de Notion con hash/commit (TyC Punto 6.1). Cada activo previo que entre al proyecto queda fechado y firmado hoy.
- [ ] Dejar lista la plantilla de bitácora diaria (fecha, qué se hizo, quién, commit, uso de IA declarado — TyC Punto 7).
- [ ] Tener a mano este Checklist y el Dossier de Diagnóstico para arrancar el Día 1 sin improvisar.

---

## 1. Mapeo de talentos del equipo (Día 1, primeras 2 horas)

No repartimos tareas por cargo, sino por lo que cada quien hace mejor. Cada integrante llena esta ficha en 10 minutos y la pega en Notion.

**Ficha rápida por persona:**

- [ ] Nombre y contacto (WhatsApp para el canal operativo).
- [ ] Qué sé hacer bien (técnico / diseño / negocio / datos / comunicación).
- [ ] Qué herramientas domino de verdad (Python, n8n, Make, Figma, Canva, APIs, SQL, pitch).
- [ ] Cuántas horas reales puedo dar del 22 al 26.
- [ ] Un entregable pasado del que esté orgulloso (link o captura). Evita el "sé de todo": pide el ejemplo concreto.

**Roles a cubrir (una persona puede llevar dos):**

| Rol | Responsable de | Perfil que encaja |
|-----|----------------|-------------------|
| Lead / Producto | Visión, decisión de reto, UX del MVP, pitch final | Juan |
| Dev backend / automatización | Flujos n8n/Python, APIs, integración IA (Gemini) | Quien domine Python/no-code |
| Dev frontend / UX-UI | Prototipo navegable, funnel, demo visual | Perfil diseño/front |
| Datos / modelo | Segmentación, scoring, lógica de cotización | Perfil analítico |
| Business / pitch support | Viabilidad comercial, guion, video demo | Perfil negocio/comunicación |

- [ ] Asignar cada rol con nombre y suplente. Sin dueño = no existe.

---

## 2. Configuración de entorno (Día 1, en paralelo al mapeo)

Meta: que cualquiera del equipo pueda empujar un cambio y verlo correr antes del almuerzo del Día 1.

**GitHub**
- [ ] Repo creado, todos con acceso, rama `main` protegida.
- [ ] Estructura base de carpetas (`/backend`, `/frontend`, `/data`, `/docs`, `/pitch`).
- [ ] Primer commit de "hola mundo" por cada dev para validar acceso.

**Notion (centro de mando)**
- [ ] Página raíz con sub-páginas: Bitácora PI, Diagnóstico, Roadmap, Pitch, Enlaces.
- [ ] Tablero de tareas con estados (Por hacer / En curso / Hecho) y dueño por tarea.

**n8n / Make**
- [ ] Instancia lista (cloud o self-host) y accesos compartidos.
- [ ] Credenciales de API guardadas en un solo lugar seguro (no en el chat).

**Python**
- [ ] Entorno reproducible (`requirements.txt` o `venv`) para que el modelo corra igual en cualquier máquina.
- [ ] Acceso a la API de IA definido (Gemini API u OpenCode, según TyC Punto 7) y probado con una llamada de prueba.

**Canal operativo**
- [ ] Grupo de WhatsApp para lo urgente; Notion para lo que queda escrito. Regla: decisión que no está en Notion, no se tomó.

---

## 3. Definición rápida del reto (Día 1, cierre de la mañana)

La decisión sale del Dossier de Diagnóstico, no de la corazonada. El Montecarlo (200.000 escenarios) da **Seguros como la apuesta con mayor probabilidad de ganar el jurado (84,3%)** por viabilidad de implementación, mientras **Crédito gana en impacto puro**. La mesa decide con ese dato enfrente.

- [ ] Leer en equipo el resumen ejecutivo del Dossier (10 min).
- [ ] Votar reto con el criterio: qué podemos construir de verdad en 3 días Y qué puntúa mejor ante el jurado.
- [ ] Escribir en una frase el problema que resolvemos y para quién (afiliado Colsubsidio concreto, no "los usuarios").
- [ ] Definir el "quedó hecho" del MVP: la acción mínima que un jurado puede ver funcionando en el demo.

---

## 4. Ritual de trabajo (22–26 jul)

- [ ] **Stand-up de 15 min cada mañana:** qué hice, qué haré, qué me bloquea. Sin desviarse.
- [ ] **Cierre de 10 min cada noche:** actualizar bitácora, commit del día, riesgo del día siguiente.
- [ ] **Congelamiento de código:** domingo 26 a mediodía. Después solo se prepara demo y pitch, no se toca lógica.
- [ ] **IA declarada:** cada uso de IA relevante queda anotado en la bitácora (TyC Punto 7).

---

## 5. Calendario de la ventana (22–26 jul)

| Día | Foco | Salida concreta |
|-----|------|-----------------|
| Mié 22 | Onboarding + elección de reto | Equipo mapeado, entorno vivo, reto elegido |
| Jue 23 | Diagnóstico + diseño del MVP | Arquitectura y UX del MVP definidos |
| Vie 24 | Arquitectura y tech (agentes IA, flujos) | Esqueleto técnico corriendo |
| Sáb 25 | Build core + pruebas de integración | MVP navegable de punta a punta |
| Dom 26 | Packaging: congelar, bitácora, video, pitch 3 min | Demo grabado + Pitch Deck alineado a los 5 criterios |

---

## Cierre — arranque del Día 1

Primer movimiento mañana 8:00: mapeo de talentos (2h) en paralelo con setup de entorno. A mediodía se decide reto. El resto del día es diseñar el MVP. Si algo de la sección 0 no está listo hoy, se cierra antes de dormir.
