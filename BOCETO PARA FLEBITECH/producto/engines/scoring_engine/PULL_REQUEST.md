# Ranking por lift + disparadores duros

**Tipo:** refactor + corrección de comportamiento
**Rompe compatibilidad:** sí (ver *Migración*)

---

## Problema

El motor ordenaba las recomendaciones por `score` crudo. Eso produce tres
defectos, verificables con los perfiles de demostración que ya venían en el
código.

### 1. El techo es desigual

Cada producto tiene un máximo teórico distinto: Vida llega a 31 puntos,
Arrendamiento a 20. Comparar sus scores crudos es comparar una nota sobre 31
con una sobre 20 — Vida gana por construcción, no por pertinencia.

En el preset *"Pareja con casa propia, mascota, ingreso alto"*:

| Producto | Score | Pct | Posición anterior |
|---|---|---|---|
| Vida | 24/31 | 77,4 % | **2** |
| Hogar | 23/24 | 95,8 % | 3 |

Vida quedaba por encima de Hogar teniendo 18 puntos porcentuales menos de
afinidad. El motor calculaba `pct` y luego lo ignoraba al ordenar.

### 2. El piso también es desigual

Normalizar por el máximo no basta. Variables demográficas como edad, ingreso
y composición familiar reparten puntos a casi todos los productos, así que
cada póliza arrastra un piso propio que no significa afinidad sino ruido
acumulado.

En ese mismo perfil, Arrendamiento salía con **75 % de afinidad** aunque el
cliente respondió `V7 = No` (no arrienda ningún inmueble a terceros). Ese 75 %
venía íntegro de edad, ingreso y situación laboral.

### 3. Los hechos declarados se diluyen

`V9 = Sí` ("tiene mascota") vale 5 puntos dentro de una suma de once sumandos.
En el perfil de arriba, que **declara tener mascota**, el seguro de mascotas
quedaba en el puesto 4. Una condición binaria y verificable no se resuelve con
un score continuo.

---

## Solución

### Lift como criterio de orden

```
lift[p] = pct[p] − baseline_pct[p]
```

El `baseline_pct` es el porcentaje que el producto obtendría de un perfil
promedio. Restarlo convierte la pregunta de *"¿qué tan alto puntúa?"* a
*"¿este cliente encaja más que el cliente típico?"*, que es la pregunta
comercial real.

### Cómo se calcula el piso

El score es una suma de aportes independientes por variable, así que la
esperanza tiene forma cerrada:

```
E[score_p] = Σ_v Σ_c  P(c) · peso[v|c][p]
```

Con distribución uniforme, `P(c) = 1/n`. Esto es **idéntico** a enumerar las
1.620 combinaciones de variables estructurales, pero en 33 operaciones en vez
de 1.620. El test `test_forma_cerrada_iguala_a_la_enumeracion` verifica la
equivalencia numérica contra la enumeración exhaustiva.

Se calcula una vez al construir el motor, no por cada perfil.

### Variables estructurales vs. condicionales

La clasificación es **derivada de los datos**, no una lista escrita a mano:

> Una variable es **estructural** si todas sus categorías tienen algún peso
> distinto de cero. Es **condicional** si alguna categoría tiene el vector
> completo en cero — esa categoría es un "no aplica".

Resultado: V1–V6 estructurales, V7–V11 condicionales. Solo las estructurales
entran al piso. Así, tener carro o mascota se lee como ventaja real sobre el
promedio en lugar de diluirse en él.

### Piso por producto (distribución uniforme)

Los productos con disparador quedan **marcados** en la tabla, como se pidió:

| Producto | E[score] | Máx | Piso % | Disparador |
|---|---|---|---|---|
| Vida | 17,37 | 31 | 56,02 | — |
| Accidentes personales | 14,43 | 24 | 60,14 | — |
| Renta por hospitalización | 14,83 | 23 | 64,49 | — |
| Diagnóstico positivo de cáncer | 14,07 | 21 | 66,98 | — |
| Póliza de salud | 15,87 | 24 | 66,11 | — |
| Exequial familiar | 14,17 | 24 | 59,03 | — |
| Seguro de mascotas | 13,73 | 25 | 54,93 | ⚑ `V9=Sí` |
| Todo riesgo autos y motos | 13,83 | 25 | 55,33 | ⚑ `V8=Carro`, `V8=Moto` |
| Todo riesgo hogar | 15,93 | 24 | 66,39 | — |
| Bicicletas y patinetas | 10,27 | 21 | 48,89 | ⚑ `V10=Sí` |
| Arrendamiento | 9,33 | 20 | 46,67 | ⚑ `V7=Sí` |
| Educación | 13,53 | 25 | 54,13 | — |

Los pisos van de 46,67 % a 66,98 %: **veinte puntos de diferencia** que antes
se comparaban como si fueran equivalentes.

### Disparadores duros, en las dos direcciones

Un disparador modela un hecho verificable ("posee el objeto asegurable"), no
una propensión. Se saca del score y se resuelve como regla:

- `TriggerPromoter` — si el hecho se declara, el producto entra al top-3.
- `TriggerGate` — si el producto exige un hecho y **ninguno** se activó, baja
  al final. Es la mitad simétrica, y es la que arregla el caso de
  Arrendamiento al 75 %. No elimina el producto: lo relega conservando su
  orden, para que siga siendo visible y auditable.

Nota de criterio: `V8=Moto` dispara *autos* pero no *accidentes personales*,
aunque tenga peso 3 en ambos. Poseer una moto es un hecho; ser más propenso a
accidentes es una inferencia, y las inferencias se quedan en el score.

---

## Resultado

Preset *"Pareja con casa propia, mascota, ingreso alto"*:

| # | Producto | Score | Pct | Piso | Lift | Nota |
|---|---|---|---|---|---|---|
| 1 | Todo riesgo autos y motos | 24/25 | 96,0 | 55,33 | **+40,67** | ⚑ V8 |
| 2 | Seguro de mascotas | 23/25 | 92,0 | 54,93 | **+37,07** | ⚑ V9 |
| 3 | Todo riesgo hogar | 23/24 | 95,8 | 66,39 | +29,41 | |
| 4 | Vida | 24/31 | 77,4 | 56,02 | +21,38 | |

Mascotas sube del puesto 4 al 2. Vida baja del 2 al 4. Arrendamiento sale del
top-5. Los tres defectos, corregidos.

---

## Cambios estructurales

El archivo único de 1.221 líneas se separó en capas con una responsabilidad
cada una:

```
scoring_engine/
├── models.py      Objetos de valor inmutables (dataclasses congelados)
├── catalog.py     Solo datos: productos, variables, pesos, racionales
├── baseline.py    Cálculo del piso            [Strategy]
├── ranking.py     Orden y ajustes             [Strategy + Chain]
├── engine.py      Orquestación                [Repository]
├── reporting.py   Formateo a texto
└── cli.py         Demostración
tests/
└── test_scoring_engine.py   52 tests
```

### Patrones aplicados y qué desacoplan

| Patrón | Dónde | Qué permite |
|---|---|---|
| **Strategy** | `BaselineProvider` | Cambiar de piso uniforme a piso poblacional sin tocar el motor |
| **Strategy** | `RankingStrategy` | Cambiar la política de orden sin tocar la aritmética |
| **Chain** | `RankingPostProcessor` | Añadir o quitar reglas de negocio de forma independiente y testeable |
| **Repository** | `ScoringCatalog` | Sustituir la fuente de datos (Excel, base de datos) sin tocar el algoritmo |

`PopulationBaseline` ya está implementado y probado: cuando exista la
distribución real de afiliados, se inyecta por constructor y nada más cambia.

### `MAXS` ahora se deriva

Estaba escrito a mano. Ahora se calcula desde la matriz. Coincide exactamente
con los valores anteriores (`test_maxs_coincide_con_el_motor_original`), pero
ya no puede quedar desactualizado si alguien edita un peso.

### Código eliminado

| Elemento | Motivo |
|---|---|
| `ResultadoProducto.to_dict()` | Nunca invocado |
| `top_variables_influyentes()` | Nunca invocado |
| `AFILIADO_EN_SISTEMA` / `SIEMPRE_PREGUNTAR` | Listas sueltas sin uso — ahora son el campo `VariableDef.origen` |
| `self.sources` | Atributo asignado y nunca leído |
| `MAXS` literal | Reemplazado por derivación |
| `_demo()` | Movido a `cli.py` |

---

## Tests

52 tests, `pytest` puro, sin dependencias externas.

- **Catálogo** — largo de vectores, cobertura de racionales, coherencia de
  disparadores, y que el constructor rechace datos malformados.
- **Baseline** — equivalencia con enumeración exhaustiva, exclusión de
  condicionales, normalización de distribuciones poblacionales.
- **Scoring** — reconstrucción del score desde el desglose, inmutabilidad del
  perfil de entrada, determinismo, validación de errores.
- **Estrategias** — monotonía de cada política, parametrizada.
- **Disparadores** — promoción, bloqueo, y precedencia del producto explícito.
- **Regresiones** — los tres defectos de arriba, cada uno con su test que
  compara el comportamiento anterior contra el nuevo.

`ruff check` y `ruff format --check` pasan limpio. Docstrings en formato Google
en todas las funciones públicas.

---

## Migración

```python
# Antes
motor = MotorScoring()
resultado = motor.calcular_scores(perfil, producto_explicito="autos")
resultado.ranking[0].pct

# Ahora
from scoring_engine import MotorScoring
motor = MotorScoring()
resultado = motor.calcular(perfil, producto_explicito="autos")
resultado.top.lift
```

Cambios de API: `calcular_scores` → `calcular`; `resultado.desglose` →
`resultado.aportes`; `ficha_texto` y los formateadores se movieron a
`scoring_engine.reporting` y reciben el motor como primer argumento.

Para reproducir el comportamiento anterior:

```python
MotorScoring(strategy=ScoreRanking(), post_processors=())
```

---

## Limitaciones conocidas

1. **El piso uniforme no es el piso real.** Asume que todas las categorías son
   igual de frecuentes, y no lo son. La corrección requiere la distribución de
   afiliados y `PopulationBaseline`.
2. **Los pesos siguen siendo declarados, no aprendidos.** Este PR mejora cómo
   se comparan los scores, no de dónde salen. Eso necesita historia de
   cotizaciones y compras, que hoy no existe.
3. **`top_n_triggers=3` es arbitrario.** Con cuatro o más hechos declarados,
   alguno queda fuera del top-3. Se debería calibrar con datos de conversión.
