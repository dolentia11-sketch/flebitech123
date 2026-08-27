# Motor de Scoring de Seguros — Colsubsidio

Motor de reglas determinista que ordena 12 pólizas para un perfil de 11
variables. Sin entrenamiento y sin probabilidades: los pesos son declarados y
auditables contra fuentes públicas (DANE, Fasecolda, INC, SURA).

## Archivos

```
mvp/reto02-seguros/
├── scoring_engine/            paquete Python del motor
│   ├── __init__.py           API pública: re-exporta MotorScoring y ScoringCatalog
│   ├── models.py             dataclasses inmutables del dominio
│   ├── catalog.py            datos de negocio (productos, pesos, triggers)
│   ├── baseline.py           cálculo del piso por producto (Strategy)
│   ├── ranking.py            ordenamiento + post-procesos (Strategy + Chain)
│   ├── engine.py             orquestador — único punto de entrada
│   ├── reporting.py          formateo a texto plano
│   └── cli.py                demo por consola
├── tests/
│   └── test_scoring_engine.py suite pytest
├── pyproject.toml            empaquetado + config de ruff/pytest
├── README.md                 este archivo
└── PULL_REQUEST.md           justificación de diseño (lift, triggers)
```

| Archivo | Rol | Qué expone |
| --- | --- | --- |
| `scoring_engine/__init__.py` | API pública del paquete. Permite `from scoring_engine import MotorScoring` como aparece en el ejemplo de uso. | `MotorScoring`, `ScoringCatalog` |
| `scoring_engine/models.py` | Objetos de valor del dominio (dataclasses `frozen`). Base común, sin lógica. | `ProductDef`, `VariableDef`, `TriggerDef`, `ChecklistDef`, `Baseline`, `AporteVariable`, `ResultadoProducto`, `ResultadoScoring` |
| `scoring_engine/catalog.py` | Capa de datos: productos, variables, matriz de pesos, racionales, checklist y disparadores. Constantes puras, sin lógica. | `PRODUCTS`, `VARIABLES`, `WEIGHTS`, `RATIONALE`, `CHECKLIST`, `TRIGGERS`, `CASE_PRESETS` |
| `scoring_engine/baseline.py` | Calcula el piso teórico (E[score]) por producto usando solo variables estructurales. Patrón *Strategy* para poder cambiar la distribución. | `BaselineProvider` (Protocol), `UniformBaseline`, `PopulationBaseline`, `es_estructural` |
| `scoring_engine/ranking.py` | Política de ordenamiento + reglas de post-proceso (gate por trigger, promoción por trigger, promoción explícita). Patrones *Strategy* + *Chain*. | `RankingStrategy`, `LiftRanking`, `PctRanking`, `ScoreRanking`, `RankingPostProcessor`, `TriggerGate`, `TriggerPromoter`, `ExplicitProductPromoter` |
| `scoring_engine/engine.py` | Orquestador. Envuelve el catálogo, valida perfil, corre el pipeline y arma el resultado auditable. Es el único punto de entrada público. | `ScoringCatalog`, `MotorScoring` |
| `scoring_engine/reporting.py` | Formateo a texto plano para consola / asesor (tablas y ficha de cierre). Desacoplado del motor porque la presentación cambia más rápido que el cálculo. | `tabla_baselines`, `tabla_ranking`, `ficha_texto` |
| `scoring_engine/cli.py` | Demo por consola: imprime pisos, ranking de cada caso preset, ficha del primer caso e influencia de variables. | `main` (invocable con `python -m scoring_engine.cli`) |
| `tests/test_scoring_engine.py` | Suite `pytest`: cubre validación, aritmética, baseline, ranking, triggers y promoción explícita. | Casos de test |
| `pyproject.toml` | Empaquetado (Python ≥ 3.11), extras `dev` (pytest, ruff) y config de lint (ruff con convención Google). | Config del paquete `motor-scoring-colsubsidio` |
| `PULL_REQUEST.md` | Justificación del diseño de `lift`, disparadores y separación estructural / condicional. Lectura obligada antes de cambiar pesos. | Documentación de decisiones |

## Flujo de ejecución

Todo pasa por `MotorScoring.calcular(perfil, producto_explicito=None)` en
`engine.py`. El pipeline es determinista y siempre en el mismo orden:

```
                                                       [ archivo responsable ]
perfil (dict V1..V11)
   │
   ▼
[1] validar_perfil           ──────────────────────────  engine.py
        │  faltantes / categorías inválidas → ValueError
   ▼
[2] _aportes                 ──────────────────────────  engine.py + catalog.py
        │  lee pesos y racionales por respuesta
   ▼
[3] _triggers_activos        ──────────────────────────  engine.py + catalog.py
        │  match respuesta == categoría del TriggerDef
   ▼
[4] _puntuar                 ──────────────────────────  engine.py
        │  score = Σ pesos ; pct = score / MAXS * 100
        │  lift = pct − baseline_pct  (baseline precalculado en __init__
        │                              usando baseline.py)
   ▼
[5] strategy.ordenar         ──────────────────────────  ranking.py (LiftRanking)
        │  sort por (lift, pct, score) desc
   ▼
[6] post_processors          ──────────────────────────  ranking.py
        │  TriggerGate       → baja lo que exige trigger no activado
        │  TriggerPromoter   → sube al top_n los productos con trigger
        │  ExplicitProductPromoter → fuerza al 1º el pedido por nombre
   ▼
[7] asignar rank             ──────────────────────────  engine.py
        │
   ▼
ResultadoScoring (ranking + aportes)
```

Los pasos 1–4 son **aritmética pura**: mismo perfil ⇒ mismo score, siempre. Los
pasos 5–6 son **política de negocio inyectable**: se cambian por constructor
sin tocar el cálculo (esto es lo que hace `tests/` verificable en aislamiento).

El **piso** (`baseline_pct`) se calcula una sola vez al construir el motor,
no por cada perfil.

Salida y presentación:

```
ResultadoScoring ──► reporting.py ──► tabla_ranking / ficha_texto
                                            │
                                            ▼
                                       stdout (cli.py)
```

## Contexto: otros archivos en la carpeta

Además del paquete `scoring_engine`, en esta carpeta viven **4 archivos del MVP
v1** (`quote_engine.py`, `schema_seguros.sql`, `n8n_flow_seguros.json`,
`gemini_prompts_seguros.md`) que se añadieron en el commit base de Scala Labs
(`dfd8dcc`). No están integrados con el motor de scoring; conviene entender la
diferencia para no confundirlos.

### `quote_engine.py` — cotizador del MVP v1

Motor **cotizador** de ~150 líneas. Toma 5 respuestas (edad, dependientes,
vivienda, ingreso, preocupación), mapea preocupación → producto por
diccionario, aplica un factor de edad y **calcula prima y cobertura**. Cierra
emitiendo un número de póliza vía hash. Cataloga **5 productos** (vida,
accidentes, exequial, hogar, desempleo).

**Diferencia con `scoring_engine/engine.py`:** son cosas distintas, no
versiones. Coexisten:

| | `quote_engine.py` | `scoring_engine/engine.py` |
| --- | --- | --- |
| Rol | **Cotizador** (calcula plata) | **Ranker** (ordena por afinidad) |
| Pregunta que responde | "¿Cuál te vendo y en cuánto?" | "¿Qué producto te encaja más y por qué?" |
| Productos | 5 | 12 |
| Entradas | 5 respuestas | 11 variables (V1..V11) |
| Salida | prima + cobertura + póliza | ranking de 12 con `lift`, `pct`, `baseline`, triggers, aportes por variable |
| Diseño | Un archivo, dicts hardcodeados | Paquete con Strategy/Chain, catálogo separado, baseline calculado, tests |
| Auditabilidad | Baja | Alta (racional por peso, datos declarados vs. fuentes públicas) |

Son **complementarios**: el motor de scoring decidiría *qué* póliza ranquear
#1; el cotizador la cotizaría. Hoy no están integrados.

### `schema_seguros.sql` — persistencia del MVP v1

Esquema mínimo SQLite/Postgres, 4 tablas modelando la cadena documentada en
`juampablos.md`:

```
producto_seguro ──► conversacion ──► cotizacion ──► poliza
   (catálogo)      (respuestas del   (producto +      (número +
                    cliente, JSON,    cobertura +      consentimiento +
                    canal, necesidad) prima +          vigencia)
                                      idoneidad)
```

**Para qué se usa:** persistir el flujo del `quote_engine` cuando lo orquesta
n8n con Gemini. Cada conversación se guarda, cada cotización queda con estado
(`cotizada` / `aceptada` / `emitida` / `descartada`) para auditar la venta
adecuada (regulatorio). El schema está **alineado con `quote_engine.py`**
(mismas 5 pólizas, mismos campos: `prima_mensual`, `cobertura`, `idoneidad`,
`estado`), **no con `scoring_engine`** — el motor de scoring no persiste nada.

Los archivos `n8n_flow_seguros.json` y `gemini_prompts_seguros.md` completan
ese MVP v1: el flujo del orquestador n8n y los prompts del modelo Gemini que
conducen la conversación.

> **Nota:** en `origin/main` estos 4 archivos ya fueron eliminados por el
> commit `b5789cb` (2026-07-23). Vale la pena confirmar con el equipo si
> el MVP v1 se descontinuó o si fue reemplazado por otra pieza aguas arriba
> antes de mezclar este branch con `main`.

## Instalación

```bash
python -m pip install -e ".[dev]"
```

Requiere Python 3.11+. El motor en sí no tiene dependencias.

## Uso

```python
from scoring_engine import MotorScoring

motor = MotorScoring()
resultado = motor.calcular({
    "V1": "36-45 años",
    "V2": "Femenino",
    "V3": "Formal independiente / profesional",
    "V4": "Alto (> $4.6M)",
    "V5": "Pareja sin hijos",
    "V6": "Propia financiada (hipoteca)",
    "V7": "No",
    "V8": "Carro",
    "V9": "Sí",
    "V10": "No",
    "V11": "No",
})

print(resultado.top.nombre, resultado.top.lift)
```

## Demostración

```bash
python -m scoring_engine.cli
```

## Tests

```bash
python -m pytest tests -v
ruff check .
```

## Documentación

- Contrato de entrada/salida y flujo de ejecución: docstring de
  `scoring_engine/engine.py`.
- Justificación del diseño de lift y disparadores: `PULL_REQUEST.md`.
