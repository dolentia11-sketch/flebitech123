# Catálogo de seguros Colsubsidio — para el equipo

Recopilación limpia del portafolio de seguros de Colsubsidio, lista para que el equipo
la revise y la cargue en el motor de cotización del MVP (Reto 02).

## Archivos

| Archivo | Para qué |
|---|---|
| [`catalogo-seguros-colsubsidio.md`](catalogo-seguros-colsubsidio.md) | Vista legible por familia + mapa arquetipo→producto + desbloqueo de asequibilidad + fuentes |
| [`productos-seguros.json`](productos-seguros.json) | Fuente estructurada (21 productos). Cárgala directo en `quote_engine.py` |
| [`productos-seguros.csv`](productos-seguros.csv) | Misma data en hoja de cálculo (separador `;`) |

## Resumen (v2 — corregido tras revisión multiagéntica)

- **26 productos** en 7 familias (Vida y exequial, Salud y asistencias, Hogar,
  Vehículos, Mascotas, Deudores/crédito, Empresas).
- **23 relevantes** para la venta individual del reto (`relevante_reto: true`).
- **Aseguradoras aliadas:** MetLife, Chubb, BMI Seguros Colombia, SURA.
- **Precios:** no públicos (se simulan en el MVP) — **excepto SOAT** (tarifa regulada
  pública; usar valor real).
- **SOAT:** una de las líneas de mayor volumen de ventas según los organizadores
  (presentación en vivo, 22-jul) — ver nota destacada en el catálogo.
- **Pago:** cupo de crédito de la Tarjeta de Afiliación, cuota monetaria, u otro canal.

*Construido con Claude Opus 4.8 (esfuerzo alto); v2 con Claude Fable 5 (esfuerzo
alto), 22-jul-2026.*

## Cómo usarlo en el MVP

1. El motor de recomendación (Python) lee `productos-seguros.json`.
2. Cruza el perfil del afiliado (familia, edad, categoría, consumo) con `relevante_reto`
   y el mapa arquetipo→producto del `.md`.
3. Devuelve producto + razón en lenguaje natural ("por qué a esta persona este seguro").

Fuente y fecha de captura en el `meta` del JSON. Actualizar si Colsubsidio cambia el
portafolio.
