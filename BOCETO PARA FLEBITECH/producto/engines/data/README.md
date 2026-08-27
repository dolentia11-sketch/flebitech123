# `data/` — export auditable del catálogo de scoring

Este directorio existe para que **Melissa y Caro** puedan revisar y validar las
reglas del motor de scoring **sin abrir código Python**. Es el reemplazo — en
sentido inverso — de la tarea T003 original: en lugar de exportar el Excel a
CSV, exportamos `catalog.py` (fuente de verdad, versionado) a CSVs/XLSX
legibles.

## Qué hay aquí

| Archivo | Contenido | Filas |
|---|---|---|
| `exportar_catalog.py` | Script generador — no editar los CSVs, editar el catálogo | — |
| `productos.csv` | 12 productos (key, nombre, línea Familia/Patrimonio) | 12 |
| `variables.csv` | 11 variables V1..V11, cada categoría en una fila (código, etiqueta, origen sistema/formulario, categoría) | 33 |
| `matriz_pesos.csv` | **La matriz de pesos**. Cada fila = (variable, categoría), columnas = los 12 productos, celdas = peso 0..5, última columna = racional textual | 33 |
| `triggers.csv` | Disparadores duros (V8=Carro → autos, etc.) | 5 |
| `checklist.csv` | Datos requeridos para cerrar cada producto y su modo (con/sin intermediario) | 53 |
| `fuentes.csv` | Fuentes públicas (DANE, Fasecolda, INC, SURA…) que sustentan los pesos | 15 |

## Regla de oro

> **La fuente de verdad es `producto/engines/scoring_engine/scoring_engine/catalog.py`**.
> Los CSVs de este directorio son solo espejo para revisión. Si cambias un CSV, tu cambio **no llega al motor**.

## Cómo lo usan Melissa y Caro

1. **Abrir en Excel/Google Sheets**. Cualquiera de los CSVs se abre haciendo doble clic. Recomendado abrir primero `matriz_pesos.csv`: contiene la vista principal (variables × productos con racional).
2. **Anotar cambios propuestos**. Comentar directamente en el archivo (versión propia en Sheets, o marcar en Excel) qué peso o racional debería ajustarse y por qué. No hay que borrar nada del CSV oficial.
3. **Pasar los cambios a Daniel** (o a quien esté de guardia del motor). Un dev los aplica en `catalog.py` en un PR con la referencia a la anotación.
4. **Re-generar los CSVs** tras el merge (ver abajo). Los CSVs siempre reflejan lo que está en `catalog.py`.

## Cómo regenerar los archivos

Desde la raíz del repo:

```bash
cd producto/engines
python -m data.exportar_catalog
```

Salida esperada:

```
  ✓ engines/data/productos.csv  (12 filas)
  ✓ engines/data/variables.csv  (33 filas)
  ✓ engines/data/matriz_pesos.csv  (33 filas)
  ✓ engines/data/triggers.csv  (5 filas)
  ✓ engines/data/checklist.csv  (53 filas)
  ✓ engines/data/fuentes.csv  (15 filas)
```

### Con XLSX (recomendado si vas a mandarle un solo archivo a Melissa)

```bash
pip install openpyxl
python -m data.exportar_catalog --xlsx
```

Añade `catalog_export.xlsx` con **una hoja por archivo** y un **mapa de calor**
(azul más oscuro = peso más alto) sobre `matriz_pesos`, útil para detectar
outliers de un vistazo.

### Cambiar el directorio de salida

```bash
python -m data.exportar_catalog --out /ruta/donde/quieras
```

## Por qué invertimos la dirección de T003

La T003 original leía `Motor_Scoring_Seguros_Colsubsidio.xlsx` → CSV → motor.
Melissa validó la iteración 2 del catálogo directamente en `catalog.py`, así que:

- **Auditable en PRs**: cada cambio de peso queda en `git blame` con autor, fecha y motivo del commit.
- **Sin paso intermedio**: no hay riesgo de desalineación Excel ↔ código.
- **Un solo motor de exportación**: si mañana queremos publicar la matriz en la
  web o en un dashboard, sale de aquí.
