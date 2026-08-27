# Análisis de la base de afiliados — Reto 02 Seguros (v2, corregido)

> ⚠️ **HISTÓRICO (23-jul):** la organización publicó una base actualizada (500K
> filas, sin PII, valores enmascarados, columnas nuevas). El análisis vigente es
> [[2026-07-23_analisis-base-afiliados-v3]]. Este doc queda como registro de la
> base v1 y del hallazgo de PII que fue atendido.

Fuente: `Usos_Productos_Afiliados_SIN_ID.csv` entregado por la organización (Drive
"Recursos Reto Seguros"). **1.566.028 filas**, separador `;`, 16 columnas. Procesado
por código (no cabe en Excel).

> **v2 (22-jul, tarde):** corregida tras una revisión independiente multiagéntica.
> Cambio principal: la v1 segmentaba con un orden de precedencia que ponía la edad
> (">55") por encima de la estructura familiar, lo que absorbía p. ej. al 53,5% de las
> parejas conyugales dentro de "adulto mayor" y distorsionaba tamaños. La v2 usa la
> **estructura familiar como eje** y la edad como corte transversal. Los vacíos se
> reportan aparte, nunca mezclados.

## Qué mide cada variable (leer antes de usar)

- `SEGMENTO_GRUPO_FAMILIAR` mide **beneficiarios registrados en la caja**, no estado
  civil. "Sin grupo familiar" ≠ soltero: el afiliado puede tener familia no registrada
  o cubierta por otra caja (vía cónyuge). Todas las etiquetas de abajo son **proxies**.
- Las 5 marcas de consumo son **SI/NO sin fecha**: uso histórico, no reciente. No
  soportan afirmaciones de "acaba de usar X".
- `ESTADOAFILIADO` es constante ("Al día" en el 100%) y `CIUDAD_AFILIADO` está vacía
  en el 58,3% — de las filas con ciudad, 81% es Bogotá D.C. (≈34% de la base total).

## Notas de manejo de datos (hechos, para decisión del equipo)

1. **La base trae `NOMBRE_COMPLETO` con nombres reales** pese a que el instructivo la
   describe como anonimizada. Manejo aplicado: se trabaja solo por `SERIE` y no se
   muestran nombres en ningún entregable. Si se notifica a la organización, y cómo se
   menciona (o no) en el pitch, es decisión del equipo.
2. **Anomalía en DROGUERIA:** el % de "SI" por edad cae de 6,92% (36–45) a 0,09%
   (46–55). Un acantilado así es implausible como comportamiento (los mayores usan más
   farmacia, no menos); parece un artefacto de cómo se construyó la marca (p. ej. datos
   de un canal que no cubre a mayores). **Pregunta para la organización.** Mientras
   tanto: usarla como señal solo en menores de 46.
3. Hoteles (0,03% SI), Agencias (0,02%) y Vivienda (0,07%) están casi vacías: no
   sirven como criterio de recomendación.

## Distribuciones clave

- **Categoría:** A 75,8% · B 14,5% · C 8,8% · sin dato 0,9% (más 2 filas "D").
- **Edad:** <19 → 1,5% · 20–35 → 47,0% · 36–45 → 24,9% · 46–55 → 15,3% · >55 → 11,3%.
- **Género:** M 55,6% · F 44,4%.

## Segmentos por estructura familiar (eje corregido)

| Segmento (proxy registral) | N | % base | % cat A | % F | % >55 | % 20–35 | Edad dominante |
|---|---|---|---|---|---|---|---|
| Sin grupo familiar registrado | 908.102 | 58,0% | 76,3% | 41,0% | 11,0% | 56,9% | 20–35 |
| Familia monoparental | 367.713 | 23,5% | 82,4% | 56,8% | 3,5% | 42,4% | 20–35 |
| Monoparental ampliada | 33.963 | 2,2% | 67,8% | 57,8% | 9,7% | 34,6% | 20–35 |
| Familia nuclear (integral + ampliada) | 147.358 | 9,4% | 69,9% | 35,4% | 9,7% | 20,4% | 36–45 |
| Pareja conyugal | 85.695 | 5,5% | 67,3% | 38,3% | **53,5%** | 8,7% | **>55** |
| Sin dato | 23.197 | 1,5% | 35,7% | 43,7% | — | — | 20–35 |

Notas:
- "Monoparental" aquí es el segmento puro (un solo adulto registrado con dependientes).
  La variante "ampliada" (33.963) tiene otros adultos en el grupo y se reporta aparte.
- La mitad de las parejas conyugales es mayor de 55 — para ese subgrupo, salud/exequial
  compite con lo patrimonial. La edad modula el producto dentro de cada segmento.

## Señal de consumo controlada por edad (lift real)

Dentro de la banda 20–35, DROGUERIA=SI crece con la estructura familiar:
sin grupo 7,1% → monoparental 9,8% → nuclear 11,7% → pareja 15,1%. Es decir, la señal
familiar **sí existe** cuando se controla por edad; los promedios crudos por segmento
mezclaban efecto edad con efecto familia.

## Insights (de la data — las decisiones son del equipo)

1. **3 de cada 4 afiliados son categoría A** (menor ingreso) → sugiere priorizar
   productos de precio bajo. Qué producto y a qué precio es decisión de diseño del
   equipo.
2. El ejemplo del brief ("casado con 3 hijos") describe un segmento de 9,4%. Los
   segmentos grandes reales son **sin grupo registrado (58%)** y **monoparental
   (23,5%, 57% mujeres, 82% categoría A)**.
3. El segmento monoparental es candidato fuerte a persona del pitch por tamaño y carga
   emocional (hogares con un solo adulto proveedor **registrado**) — **a decidir en
   equipo**. Ojo: la data no dice si están asegurados o no; "subatendido" requeriría
   fuente externa.
4. **SOAT:** según los organizadores (presentación en vivo, 22-jul), es una de las
   líneas de mayor volumen de ventas. Con 58% de la base sin grupo registrado y
   mayoría 20–35, el SOAT (renovación anual obligatoria) es un punto de contacto
   recurrente natural — relevante para el mapa de recomendación.
5. Timing/canal: la data no trae fechas ni eventos de vida. Cualquier "momento de
   contacto" del MVP se simula o se valida con la organización.

## Preguntas abiertas para el equipo

- ¿Persona del pitch? (candidatos con data: monoparental, sin-grupo joven)
- ¿Cómo se construyó la marca DROGUERIA? (preguntar a la organización)
- ¿Alcance del catálogo: solo /seguros o también medicina prepagada (vertical Salud)?
- ¿Se notifica el hallazgo de nombres reales en la base? ¿Quién?

---
*Construido con Claude Opus 4.8 (esfuerzo alto) el 22-jul-2026; corregido a v2 con
Claude Fable 5 (esfuerzo alto) tras revisión multiagéntica de 7 agentes el mismo día.*
