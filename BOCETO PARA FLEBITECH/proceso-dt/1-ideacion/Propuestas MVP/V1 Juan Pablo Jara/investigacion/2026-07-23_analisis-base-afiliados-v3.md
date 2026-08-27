# Análisis de la base de afiliados v3 — base ACTUALIZADA por la organización (23-jul)

Fuente: `Usos_Productos_Afiliados_SIN_ID.xlsx` (versión actualizada anunciada por la
organización el 23-jul). **500.000 filas, 15 columnas.** Procesado por código (pandas).
Reemplaza como fuente activa al CSV de 1.566.028 filas analizado el 22-jul
([[2026-07-22_analisis-base-afiliados]] queda como registro histórico de la v1 de la base).

> Construido con Fable 5 (alto). Recomputado desde cero sobre el archivo nuevo;
> mapeo de valores enmascarados verificado por 4 dimensiones independientes.

## Qué cambió respecto a la base anterior

| Cambio | Antes (CSV 22-jul) | Ahora (XLSX 23-jul) | Implicación |
|---|---|---|---|
| Tamaño | 1.566.028 filas | **500.000 filas** (muestra) | Los porcentajes se sostienen; los conteos absolutos ya no son "toda la base" |
| PII | Traía `NOMBRE_COMPLETO` con nombres reales | **Columna eliminada** | El hallazgo que reportamos fue atendido — la base ahora sí es anónima |
| Valores categóricos | Legibles (A/B/C, "sin grupo familiar"…) | **Enmascarados con letras griegas** (SIGMA, LAMBDA, RHO…) | Hay que trabajar con mapeo inferido (abajo) y pedir el diccionario a la organización |
| Columnas nuevas | — | **RANGO_SALARIAL** (16 bandas SMLV), SEGMENTO_POBLACIONAL, PIRAMIDE_NUEVA, EMPRESA_FOCO | RANGO_SALARIAL es el activo nuevo más valioso (ver abajo) |
| Columnas eliminadas | ESTADOAFILIADO (constante), NOMBRE_COMPLETO | ya no están | Sin pérdida real |
| PISCILAGO | 4,9% SI (señal usable) | **100% NO** | Señal perdida — sacarla del motor |
| DROGUERIA | 5,6% SI | **17,6% SI** | La marca se reconstruyó y creció, pero el acantilado de edad PERSISTE |

## Mapeo inferido de valores enmascarados (verificado, no oficial)

Cada equivalencia se verificó contra la base v1 por 4 dimensiones simultáneas
(% del total, % categoría A, % mujeres, % >55 / edad dominante). Coincidencia
consistente en todas:

**CATEGORIA:** SIGMA = A (72,8%) · PI = B (16,4%) · ZETA = C (9,8%) · MU = sin dato (1,0%)

**SEGMENTO_GRUPO_FAMILIAR:**

| Código | Equivale a (inferido) | n | % base | % cat A (SIGMA) | % F | % >55 | % 20–35 | Edad dominante |
|---|---|---|---|---|---|---|---|---|
| LAMBDA | Sin grupo familiar registrado | 286.457 | 57,3% | 72,3% | 42,7% | 9,8% | 59,3% | 20–35 |
| RHO | Familia monoparental | 121.478 | 24,3% | 80,3% | 58,5% | 3,0% | 44,8% | 20–35 |
| EPSILON | Familia nuclear | 46.999 | 9,4% | 68,8% | 37,4% | 8,7% | 23,5% | 36–45 |
| IOTA | Pareja conyugal | 25.263 | 5,1% | 65,7% | 39,3% | **51,2%** | 11,4% | **>55** |
| CHI | Monoparental ampliada | 11.843 | 2,4% | 64,2% | 58,8% | 7,6% | 41,1% | 20–35 |
| THETA | Sin dato | 7.933 | 1,6% | 34,7% | 44,5% | 4,0% | 61,7% | 20–35 |
| PI | (residuo nuevo, 27 filas) | 27 | 0,0% | — | — | — | — | — |

⚠️ Este mapeo es **inferencia nuestra**, no diccionario oficial. Es sólido (4
dimensiones coinciden con la v1), pero la organización confirmó el 23-jul que el
enmascaramiento es deliberado, "sin divulgar la clasificación original de
Colsubsidio" → **no esperar diccionario de valores, y NO presumir el mapeo en el
pitch** (es ingeniería inversa de algo que decidieron ocultar). Uso correcto:
hipótesis interna de trabajo; ante el jurado, describir los segmentos por sus
características observables (tamaño, edad, género, salario), no por la etiqueta
reconstruida.

## Distribuciones clave (v3)

- **Categoría:** A 72,8% · B 16,4% · C 9,8% · sin dato 1,0% — *(v1: 75,8/14,5/8,8)*.
  El titular "3 de cada 4 afiliados son categoría A" **se sostiene**.
- **Edad:** <19 → 1,4% · 20–35 → 49,6% · 36–45 → 25,7% · 46–55 → 13,3% · >55 → 10,0%.
- **Género:** M 53,7% · F 46,3%.
- **Ciudad:** 57,7% vacía; de las filas con ciudad, Bogotá D.C. = 82,1% (34,7% del
  total). Municipios reales (no enmascarados): Soacha, Fusagasugá, Mosquera…

## EL ACTIVO NUEVO: RANGO_SALARIAL (asequibilidad calculable)

Por primera vez tenemos ingreso declarado por bandas SMLV:

- **Entre 1 y 1,5 SMLV: 60,5%** · Menor al SMLV: 6,8% → **~67% gana ≤1,5 SMLV**
- Entre 1,5 y 2: 8,4% · 2–2,5: 5,5% · 2,5–3: 3,9% · 3–4: 4,8% · 4–6: 4,6% · >6: ~4,9%
- Sin dato: 1,0% (+ bandas residuales con pocos registros: "Menor a 2", "Entre 2 y 4",
  "Entre 4 y 8", "Entre 8 y 19" — parecen restos de otra codificación; reportar)

**Por qué importa:** el motor puede calcular la prima como **% del ingreso real** del
afiliado — la hiperpersonalización de asequibilidad deja de ser proxy por categoría y
se vuelve un cálculo directo. Es el insumo que le faltaba a la pregunta 3 del chat
("¿cuánto puedes pagar al mes?"): el sistema puede validar que la prima recomendada
no exceda un umbral responsable del ingreso. Conecta directo con el argumento de
inclusión (microseguro para el 67% que gana ≤1,5 SMLV).

## Contexto oficial de la organización (23-jul, grupo del reto — Andrea Garzón)

La organización aclaró en el grupo de WhatsApp del reto:

- El enmascaramiento (LAMBDA, SIGMA…) es una **anonimización deliberada** que
  "preserva la consistencia de los datos para análisis, agrupaciones y conteos, sin
  divulgar la clasificación original de Colsubsidio".
- **CATEGORIA** = categoría del afiliado dentro del sistema de subsidio familiar.
- **SEGMENTO_GRUPO_FAMILIAR** = composición del hogar / estructura familiar.
- **SEGMENTO_POBLACIONAL** = segmentación individual del afiliado construida a
  partir de ingresos, edad y PAC (⚠️ "PAC" sin definir — preguntar).
- **PIRAMIDE_NUEVA** = clasifica a la **empresa aportante** dentro de la pirámide
  empresarial de Colsubsidio (es del empleador, no del afiliado).

**Desbloqueo práctico:** al ser consistentes por diseño, los valores enmascarados
son **usables tal cual como features del motor de scoring** — el modelo no necesita
saber qué significa LAMBDA, solo que sea estable. SEGMENTO_POBLACIONAL (composite
oficial de ingreso+edad+PAC) es candidata directa a feature. PIRAMIDE_NUEVA queda
como señal secundaria B2B (baja prioridad para el MVP).

- **EMPRESA_FOCO**: EMP_000001 = 81,7% · EMP_000002 = 18,3%. Única columna que
  sigue sin explicación oficial — preguntar.

Distribuciones de referencia: SEGMENTO_POBLACIONAL → TAU 46,2% (97% cat A) ·
PI 26,9% · ETA 25,5% · OMEGA 1,0% (96% "sin dato" de categoría) · XI 0,3% (99%
cat C). PIRAMIDE_NUEVA → ETA 31,2%, XI 21,7%, UPSILON 20,4%…

## Señales de consumo (v3)

- **DROGUERIA (única marca con señal): la anomalía PERSISTE y se amplificó.**
  % SI por edad: 20–35 → 24,0% · 36–45 → 21,3% · **46–55 → 0,35%** · >55 → 1,25%.
  El acantilado a los 46 años sigue siendo implausible como comportamiento real.
  Regla vigente: usarla solo en menores de 46.
- **Lift familiar dentro de 20–35 (confirmado y más fuerte):** sin grupo 21,8% →
  monoparental 28,4% → nuclear 32,4% → pareja 39,4%. La señal familiar es real.
- **PISCILAGO: muerta** (100% NO — antes 4,9% SI). Sacarla del motor y del mapa
  segmento→producto si se usaba.
- HOTELES (0,03%), AGENCIAS (0,02%), VIVIENDA (0,01%): siguen vacías, inservibles.

## Qué se sostiene y qué cambia en los entregables

**Se sostiene (los titulares del pitch siguen válidos):**
- 3 de cada 4 afiliados = categoría A (72,8%)
- Los segmentos grandes: sin grupo (57,3%) + monoparental (24,3%, 58,5% mujeres,
  80,3% cat A) — la persona del pitch no cambia
- El ejemplo del brief ("casado con hijos") sigue siendo ~9,4%
- Mitad de las parejas conyugales >55 → la edad modula el producto
- Bogotá ~82% de las filas con ciudad

**Cambia (corregir en todos los entregables):**
- "1,56M analizados" → **"muestra oficial de 500.000"** (los 1,6M de afiliados de
  Colsubsidio siguen siendo ciertos como contexto de mercado — Informe 2024 —, pero
  la base entregada ya no es censo)
- El hallazgo de PII pasa de "pendiente" a **"atendido por la organización en la v2
  de la base"** (registro histórico nuestro se mantiene)
- Nueva limitación: valores enmascarados → mapeo inferido, pedir diccionario
- Piscilago fuera del motor; Droguería con % nuevos
- Nueva oportunidad: RANGO_SALARIAL → prima como % del ingreso

## Preguntas actualizadas para la organización

1. ~~¿Diccionario de valores enmascarados?~~ → RESUELTO PARCIAL (23-jul): dieron la
   semántica por columna; los valores seguirán ocultos por diseño. No insistir.
2. ¿Qué significa **PAC** (variable usada en SEGMENTO_POBLACIONAL)?
3. ¿Qué es **EMPRESA_FOCO**? (única columna sin contexto oficial)
4. La anomalía de DROGUERIA a los 46 años persiste en la v2 — ¿artefacto confirmado?
5. ¿La muestra de 500K es aleatoria de la base de 1,56M? (afecta si podemos
   extrapolar conteos absolutos)
6. ¿Las bandas residuales de RANGO_SALARIAL ("Menor a 2", "Entre 2 y 4"…) son
   errores de codificación?
