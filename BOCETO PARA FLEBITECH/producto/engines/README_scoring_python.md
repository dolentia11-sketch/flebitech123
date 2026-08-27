# Documentación del scoring en Python — Colsubsidio

## Propósito

Este documento explica cómo se construyó el motor de scoring de seguros en Python para Colsubsidio, cuál es su lógica, qué archivos componen la carpeta de trabajo y cómo debe ejecutarse y mantenerse dentro del repositorio de GitHub [file:76][code_file:80][code_file:85][code_file:86].

El objetivo del motor es recibir un perfil de cliente, cruzarlo contra una matriz de pesos y devolver un ranking de productos de seguro por afinidad, junto con el modo de cierre comercial de cada uno [file:76]. El motor es determinístico: no usa machine learning, no consume APIs externas y no depende de servicios de IA, sino de reglas ponderadas definidas en una sola base lógica [file:76].

## Cómo se construyó

La fuente de verdad original del scoring fue una matriz en Excel llamada `Motor_Scoring_Seguros_Colsubsidio.xlsx`, complementada con un documento de requisitos de cotización por producto; el archivo `motor-colsubsidio.py` es la traducción de esa lógica a Python estándar para que pueda ejecutarse como librería, script CLI o backend de cualquier interfaz [file:76]. La implementación se diseñó como una traducción 1:1 del perfilador previo en HTML/JS, pero aislando la lógica de negocio en un solo módulo reutilizable [file:76].

La construcción del motor sigue cuatro capas: catálogo de productos, variables de segmentación, matriz de pesos y reglas de salida [file:76]. Esa estructura permite que el scoring sea auditable, porque cada resultado puede rastrearse hasta combinaciones explícitas del tipo `Vx|categoría` y sus pesos asociados [file:76].

## Estructura del archivo principal

El archivo `motor-colsubsidio.py` define 12 productos de seguro, entre ellos vida, accidentes personales, salud, exequial, mascotas, autos, hogar, bicicletas, arrendamiento y educación [file:76]. También define el máximo teórico por producto, que se usa para convertir el puntaje bruto en un porcentaje de afinidad [file:76].

Las 11 variables de entrada del perfil son `V1` a `V11`: edad, género, situación laboral, ingreso, composición familiar, tipo de vivienda, arriendo a terceros, vehículo, mascota, uso de bicicleta/patineta y jefatura femenina sin pareja [file:76]. El archivo además separa qué datos podrían existir ya para afiliados (`AFILIADO_EN_SISTEMA`) y cuáles siempre habría que preguntar (`SIEMPRE_PREGUNTAR`), lo que conecta directamente el scoring con el diseño conversacional del journey [file:76].

## Lógica del scoring

La lógica central está en `calcular_scores(perfil, producto_explicito=None)`, que valida que el perfil tenga todas las variables requeridas y que cada categoría pertenezca al catálogo permitido para esa variable [file:76]. Si falta una variable o llega una categoría inválida, el motor levanta un `ValueError`, lo que evita resultados silenciosamente incorrectos [file:76][code_file:80].

Después de validar, el motor recorre las 11 variables, busca la fila de pesos correspondiente a cada respuesta del cliente y suma esos pesos producto por producto [file:76]. Con ese total construye una lista de resultados con `score`, `max_score`, `pct`, `modo_cierre` y `rank`, luego ordena el ranking de mayor a menor afinidad y, si el usuario pidió un producto puntual, aplica la regla de negocio de subir ese producto al primer lugar para entregar “lo pedido + sugerir 2 más” [file:76].

## Reglas de negocio incorporadas

El scoring no solo clasifica afinidad, sino que traduce la salida en una decisión comercial, porque cada producto queda asociado a un modo de cierre: `auto` si puede venderse sin intermediario y `asesoria` si requiere acompañamiento humano [file:76]. Esa lógica sale del bloque `CHECKLIST`, donde también están los datos mínimos para cotización por producto, como placa para autos, datos del inmueble para hogar o información del grupo familiar para exequial [file:76].

Además, el motor tiene racionales documentados para las combinaciones variable-categoría, de forma que cada peso puede explicarse con argumentos de negocio o mercado, por ejemplo mayor relevancia de autos cuando existe carro, de mascotas cuando hay mascota o de arrendamiento cuando el usuario arrienda un inmueble a terceros [file:76]. Eso permite justificar ante producto, negocio o compliance por qué un seguro sube o baja en el ranking [file:76].

## Archivos de prueba de la carpeta

La carpeta de trabajo quedó organizada alrededor de un archivo principal y varios scripts de validación [file:76][code_file:80][code_file:85][code_file:86]. La recomendación para GitHub es dejar esta estructura mínima:

| Archivo | Función |
|---|---|
| `motor-colsubsidio.py` | Motor principal de scoring y utilidades de análisis [file:76] |
| `test_motor_colsubsidio.py` | Batería base de pruebas funcionales y validaciones de entrada [code_file:80] |
| `stress_test_motor_colsubsidio.py` | Stress test con 100 perfiles aleatorios válidos [code_file:85] |
| `test_negocio_stress_motor_colsubsidio.py` | Pruebas de negocio + stress test consolidado [code_file:86] |

El archivo base de pruebas valida casos afiliados y no afiliados, manejo de variables faltantes, categorías inválidas, perfiles extremos y producto explícito [code_file:80]. El stress test genera 100 perfiles aleatorios válidos usando el catálogo oficial de categorías y revisa que nunca falten productos, que exista top recomendado y que el ranking quede ordenado correctamente [code_file:85].

## Validaciones de negocio ya cubiertas

El archivo `test_negocio_stress_motor_colsubsidio.py` agrega reglas de negocio explícitas para reducir el riesgo de regresiones funcionales [code_file:86]. Entre ellas, valida que si el usuario tiene carro e ingreso alto, el producto `autos` quede en top 3; que si tiene mascota, `mascotas` no quede irrelevante; que si arrienda a terceros, `arrendamiento` quede visible; y que si usa bicicleta o patineta, `bicicletas` aparezca en posiciones competitivas [code_file:86].

Este archivo también vuelve a correr 100 perfiles aleatorios válidos, por lo que consolida pruebas estructurales y pruebas de negocio en una misma ejecución [code_file:86]. En la práctica, es la mejor batería para CI o para validación antes de un merge en GitHub [code_file:86].

## Cómo ejecutar la carpeta

Para correr el motor como demo local, basta ejecutar `python3 motor-colsubsidio.py`, lo que imprime casos de ejemplo, ranking top 3, ficha de cierre, variables influyentes y reglas de producto [file:76]. Para correr las pruebas, se pueden usar estos comandos [file:76][code_file:80][code_file:85][code_file:86]:

```bash
python3 test_motor_colsubsidio.py
python3 stress_test_motor_colsubsidio.py
python3 test_negocio_stress_motor_colsubsidio.py
```

Todos los scripts fueron ajustados para cargar correctamente `motor-colsubsidio.py` usando `importlib` y registrando el módulo en `sys.modules`, lo que evita errores con `@dataclass` en Python 3.14 [code_file:80][code_file:85][code_file:86].

## Qué debe entender el equipo

El scoring no es un modelo probabilístico ni una caja negra, sino un sistema de reglas ponderadas que busca priorizar la recomendación comercial de seguros a partir del perfil del cliente [file:76]. Su ventaja es que es interpretable, auditable y fácil de versionar, porque cualquier cambio de negocio se implementa cambiando pesos, checklist o reglas explícitas en un archivo controlado [file:76].

En términos de producto, este motor es el corazón del MVP porque conecta perfilamiento, recomendación y venta cruzada en una sola pieza [file:76]. En términos técnicos, deja lista una base para conectar frontend conversacional, formulario web o canal asesor sin reescribir la lógica del negocio [file:76].

## Recomendación para GitHub

La recomendación es subir la carpeta con el archivo principal, los tres scripts de prueba y este documento como `README_scoring_python.md`, de modo que cualquier miembro del equipo pueda clonar, ejecutar y entender el motor sin depender del contexto oral del sprint [file:76][code_file:80][code_file:85][code_file:86]. También conviene agregar en el repositorio una regla simple: no modificar pesos ni categorías sin acompañar el cambio con un ajuste en pruebas de negocio [file:76][code_file:86].
