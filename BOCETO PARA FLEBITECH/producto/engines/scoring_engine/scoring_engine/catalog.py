"""Datos de negocio del motor de scoring (capa de catálogo).

Este módulo es *solo datos*: no contiene lógica de cálculo. Separarlo del motor
permite reemplazar la fuente (hoy constantes en Python, mañana un Excel o una
tabla en base de datos) sin tocar el algoritmo.

Convención crítica
------------------
Todo vector de pesos es una tupla de 12 enteros cuyo orden corresponde
exactamente al orden de :data:`PRODUCTS`. La posición i del vector es el aporte
de esa categoría al producto ``PRODUCTS[i]``.
"""

from __future__ import annotations

from scoring_engine.models import (
    ChecklistDef,
    ProductDef,
    TriggerDef,
    VariableDef,
)

#: Catálogo de pólizas. El orden define el índice de los vectores de pesos.
PRODUCTS: tuple[ProductDef, ...] = (
    ProductDef("vida", "Vida", "Familia"),
    ProductDef("accidentes", "Accidentes personales", "Familia"),
    ProductDef("renta", "Renta por hospitalización", "Familia"),
    ProductDef("cancer", "Diagnóstico positivo de cáncer", "Familia"),
    ProductDef("salud", "Póliza de salud", "Familia"),
    ProductDef("exequial", "Exequial familiar", "Familia"),
    ProductDef("mascotas", "Seguro de mascotas", "Familia"),
    ProductDef("autos", "Todo riesgo autos y motos", "Patrimonio"),
    ProductDef("hogar", "Todo riesgo hogar", "Patrimonio"),
    ProductDef("bicicletas", "Bicicletas y patinetas eléctricas", "Patrimonio"),
    ProductDef("arrendamiento", "Arrendamiento", "Patrimonio"),
    ProductDef("educacion", "Educación", "Familia"),
)

#: Variables del cuestionario. ``origen`` indica si el dato se lee del sistema
#: de afiliados o si hay que preguntarlo en el formulario.
VARIABLES: tuple[VariableDef, ...] = (
    VariableDef(
        code="V1",
        label="Rango de edad",
        origen="sistema",
        categorias=(
            "18-25 años",
            "26-35 años",
            "36-45 años",
            "46-55 años",
            "56-65 años",
            "66+ años",
        ),
    ),
    VariableDef(
        code="V2",
        label="Género",
        origen="sistema",
        categorias=(
            "Masculino",
            "Femenino",
        ),
    ),
    VariableDef(
        code="V3",
        label="Situación laboral",
        origen="sistema",
        categorias=(
            "Formal dependiente",
            "Formal independiente / profesional",
            "Informal / cuenta propia sin cotización",
        ),
    ),
    VariableDef(
        code="V4",
        label="Nivel de ingreso mensual",
        origen="sistema",
        categorias=(
            "Bajo (< $1.3M)",
            "Medio ($1.3M - $4.6M)",
            "Alto (> $4.6M)",
        ),
    ),
    VariableDef(
        code="V5",
        label="Composición familiar",
        origen="sistema",
        categorias=(
            "Soltero(a) sin hijos",
            "Pareja sin hijos",
            "Con hijos menores de edad",
            "Monoparental con hijos",
            "Multigeneracional / adulto mayor a cargo",
        ),
    ),
    VariableDef(
        code="V6",
        label="Tipo de vivienda",
        origen="formulario",
        categorias=(
            "Propia pagada",
            "Propia financiada (hipoteca)",
            "Arrendada",
        ),
    ),
    VariableDef(
        code="V7",
        label="¿Es propietario que arrienda un inmueble a terceros?",
        origen="formulario",
        categorias=(
            "Sí",
            "No",
        ),
    ),
    VariableDef(
        code="V8",
        label="Tenencia de vehículo",
        origen="formulario",
        categorias=(
            "Carro",
            "Moto",
            "No tiene",
        ),
    ),
    VariableDef(
        code="V9",
        label="¿Tiene mascota (perro o gato)?",
        origen="formulario",
        categorias=(
            "Sí",
            "No",
        ),
    ),
    VariableDef(
        code="V10",
        label="¿Usa bicicleta o patineta eléctrica como transporte o deporte habitual?",
        origen="formulario",
        categorias=(
            "Sí",
            "No",
        ),
    ),
    VariableDef(
        code="V11",
        label="¿Es jefatura de hogar femenina sin pareja?",
        origen="formulario",
        categorias=(
            "Sí",
            "No",
        ),
    ),
)

#: Matriz de pesos. Clave ``"<code>|<categoria>"`` -> vector de 12 enteros.
WEIGHTS: dict[str, tuple[int, ...]] = {
    "V1|18-25 años": (1, 3, 1, 0, 2, 1, 3, 1, 1, 4, 1, 1),
    "V1|26-35 años": (3, 3, 2, 1, 3, 1, 4, 3, 2, 3, 3, 3),
    "V1|36-45 años": (5, 2, 3, 2, 3, 2, 3, 4, 4, 2, 3, 5),
    "V1|46-55 años": (4, 2, 4, 4, 4, 3, 2, 4, 4, 1, 2, 3),
    "V1|56-65 años": (2, 2, 5, 5, 4, 4, 1, 3, 3, 1, 1, 1),
    "V1|66+ años": (1, 2, 5, 5, 3, 5, 1, 1, 2, 0, 0, 0),
    "V2|Masculino": (3, 3, 2, 3, 2, 2, 2, 3, 2, 3, 2, 2),
    "V2|Femenino": (4, 2, 3, 4, 3, 3, 4, 2, 2, 2, 2, 3),
    "V3|Formal dependiente": (2, 1, 1, 2, 3, 2, 2, 3, 3, 2, 2, 3),
    "V3|Formal independiente / profesional": (5, 4, 4, 3, 4, 2, 2, 3, 3, 2, 3, 4),
    "V3|Informal / cuenta propia sin cotización": (3, 5, 3, 1, 1, 4, 1, 1, 1, 1, 1, 2),
    "V4|Bajo (< $1.3M)": (1, 3, 1, 1, 0, 4, 1, 0, 0, 2, 0, 1),
    "V4|Medio ($1.3M - $4.6M)": (3, 3, 3, 3, 3, 2, 3, 3, 3, 2, 2, 3),
    "V4|Alto (> $4.6M)": (4, 2, 3, 3, 5, 1, 4, 5, 5, 1, 4, 4),
    "V5|Soltero(a) sin hijos": (1, 3, 1, 1, 2, 1, 4, 2, 1, 4, 1, 0),
    "V5|Pareja sin hijos": (2, 2, 2, 2, 3, 2, 4, 3, 4, 2, 2, 0),
    "V5|Con hijos menores de edad": (5, 3, 4, 3, 5, 3, 2, 3, 4, 1, 1, 5),
    "V5|Monoparental con hijos": (5, 3, 3, 2, 3, 4, 1, 1, 2, 1, 1, 4),
    "V5|Multigeneracional / adulto mayor a cargo": (3, 2, 5, 4, 3, 5, 1, 1, 2, 0, 0, 2),
    "V6|Propia pagada": (2, 1, 1, 1, 2, 1, 2, 2, 5, 1, 1, 1),
    "V6|Propia financiada (hipoteca)": (3, 1, 1, 1, 2, 1, 1, 2, 5, 1, 1, 1),
    "V6|Arrendada": (1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 1),
    "V7|Sí": (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 5, 0),
    "V7|No": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "V8|Carro": (1, 1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0),
    "V8|Moto": (2, 3, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0),
    "V8|No tiene": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "V9|Sí": (0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0),
    "V9|No": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "V10|Sí": (0, 2, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0),
    "V10|No": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "V11|Sí": (3, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 3),
    "V11|No": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
}

#: Justificación de cada fila de la matriz. Alimenta la explicación al cliente.
RATIONALE: dict[str, str] = {
    "V1|18-25 años": (
        "Prioridad en bicicleta/patineta eléctrica y mascota (perfil joven urbano); vida y cáncer casi irrelevantes a esta edad."
    ),
    "V1|26-35 años": (
        "Edad pico de tenencia de mascota (30-50 años, SURA) y de arriendo (DANE); comienza a evaluar vida y autos."
    ),
    "V1|36-45 años": (
        "Pico de compra de vivienda y auto propio; arranca la lógica HLV/DIME de vida por responsabilidades familiares."
    ),
    "V1|46-55 años": (
        "21,7% de casos de cáncer ocurre en 55-64 años, el riesgo ya es relevante desde los 46; renta por hospitalización sube."
    ),
    "V1|56-65 años": (
        "Cáncer y renta hospitalización en niveles altos; exequial empieza a ganar peso."
    ),
    "V1|66+ años": (
        "53,2% de los casos de cáncer en hombres ocurre en 65+ años (INC); exequial es prioridad máxima."
    ),
    "V2|Masculino": (
        "Mayor peso relativo en autos/motos y cáncer de próstata/estómago."
    ),
    "V2|Femenino": (
        "76% de clientes de seguros de mascotas son mujeres (SURA); mayor probabilidad de jefatura de hogar."
    ),
    "V3|Formal dependiente": (
        "Ya cuenta con EPS, ARL y pensión vía empleador; prioridad en complementarios por mayor estabilidad de ingreso."
    ),
    "V3|Formal independiente / profesional": (
        "Sin seguro de vida grupal ni ARL automática; el 84% de la PEA no tiene vida individual (Fasecolda)."
    ),
    "V3|Informal / cuenta propia sin cotización": (
        "55,4% de la población ocupada (DANE); sin ARL ni pensión, accidentes y exequial son la protección más accesible."
    ),
    "V4|Bajo (< $1.3M)": (
        "Capacidad de pago limitada a prima baja; exequial tiene fuerte arraigo cultural en estratos bajos."
    ),
    "V4|Medio ($1.3M - $4.6M)": (
        "Segmento de clase media (32-34% de la población, DANE) — el segmento con mayor potencial de conversión."
    ),
    "V4|Alto (> $4.6M)": (
        "Mayor probabilidad de vivienda y vehículo propios; foco en salud complementaria y patrimonio."
    ),
    "V5|Soltero(a) sin hijos": (
        "Sin dependientes económicos; prioridad en mascota, bicicleta/patineta eléctrica y accidentes personales sobre vida."
    ),
    "V5|Pareja sin hijos": (
        "Enfoque en patrimonio compartido (hogar, auto) y mascota."
    ),
    "V5|Con hijos menores de edad": (
        "Máxima prioridad en vida y salud familiar (lógica HLV/DIME); sube renta por hospitalización y educación."
    ),
    "V5|Monoparental con hijos": (
        "24,3% de los hogares (DANE); único proveedor, vida, exequial y educación son críticos."
    ),
    "V5|Multigeneracional / adulto mayor a cargo": (
        "Mayor probabilidad de necesitar renta por hospitalización, cáncer y exequial para el adulto mayor."
    ),
    "V6|Propia pagada": (
        "Activo consolidado sin deuda; el seguro de hogar es decisión 100% voluntaria."
    ),
    "V6|Propia financiada (hipoteca)": (
        "+70% de pólizas de hogar atadas a crédito hipotecario (Fasecolda) — casi obligatorio en la práctica."
    ),
    "V6|Arrendada": (
        "Menor necesidad de seguro de hogar; puede necesitar seguro de contenidos básico."
    ),
    "V7|Sí": (
        "Oportunidad de venta cruzada específica de Arrendamiento (garantía a terceros)."
    ),
    "V7|No": ("Sin relevancia en esta variable."),
    "V8|Carro": (
        "Solo 12,2% del parque automotor tiene todo riesgo (Fasecolda) — alta oportunidad."
    ),
    "V8|Moto": (
        "Motos son 61-63% del parque pero solo 2,8-3% tiene todo riesgo — brecha grande; sube accidentes personales."
    ),
    "V8|No tiene": ("Sin relevancia para productos de vehículo."),
    "V9|Sí": ("Oportunidad de venta cruzada directa de Mascotas."),
    "V9|No": ("Sin relevancia en esta variable."),
    "V10|Sí": (
        "Oportunidad de venta cruzada directa de Bicicletas y patinetas eléctricas (hurto cada 2,5h en Bogotá, 2025)."
    ),
    "V10|No": ("Sin relevancia en esta variable."),
    "V11|Sí": (
        "46,5% jefatura femenina, 68,8% sin pareja (DANE) — foco especial del ICP de soycaropinzón; también sube educación por ser único proveedor."
    ),
    "V11|No": ("Sin relevancia en esta variable."),
}

#: Disparadores duros. Cuando el cliente responde ``categoria`` a ``code``, el
#: producto entra al top-N sin depender del score acumulado. Modelan hechos
#: verificables ("posee el objeto asegurable"), no propensiones.
TRIGGERS: tuple[TriggerDef, ...] = (
    TriggerDef("V7", "Sí", "arrendamiento", "Declara arrendar un inmueble a terceros."),
    TriggerDef("V8", "Carro", "autos", "Declara poseer carro."),
    TriggerDef("V8", "Moto", "autos", "Declara poseer moto."),
    TriggerDef("V9", "Sí", "mascotas", "Declara tener perro o gato."),
    TriggerDef(
        "V10", "Sí", "bicicletas", "Declara usar bicicleta o patineta eléctrica."
    ),
)

#: Datos necesarios para cotizar y modo de cierre por producto.
CHECKLIST: dict[str, ChecklistDef] = {
    "vida": ChecklistDef(
        modo="Con intermediario",
        items=(
            "Cédula",
            "Fecha de nacimiento",
            "Género",
            "¿Conduce moto? Sí/No",
            "¿Actividades de alto riesgo? Sí/No",
            "Valor a asegurar",
            "Ocupación o profesión",
            "— Vida oneroso: valor del crédito",
            "— Vida ahorro: valor de la póliza + ahorro mensual deseado",
        ),
    ),
    "salud": ChecklistDef(
        modo="Con intermediario",
        items=(
            "Cédula",
            "Fecha de nacimiento",
            "Ciudad",
            "Preexistencias (diabetes, cáncer, VIH, etc.)",
            "Coberturas preferidas (maternidad, cáncer, alto costo)",
            "Ocupación",
        ),
    ),
    "educacion": ChecklistDef(
        modo="Con intermediario",
        items=(
            "Cédula del asegurado (quien compra el seguro)",
            "Fecha de nacimiento del asegurado",
            "Ocupación",
            "Ciudad de residencia",
            "Fecha de nacimiento del hijo",
            "Grado de escolaridad",
            "Valor mensual o anual que está dispuesto a invertir en la educación del hijo, o valor que desea asegurar para sus estudios",
        ),
    ),
    "exequial": ChecklistDef(
        modo="Sin intermediario",
        items=(
            "Cédula del afiliado principal",
            "Grupo familiar (padres, hijos, tíos, hermanos, primos)",
            "Edades de cada uno",
        ),
    ),
    "mascotas": ChecklistDef(
        modo="Sin intermediario",
        items=(
            "Cédula del propietario",
            "Género del propietario",
            "Fecha de nacimiento",
            "Tipo de mascota (perro/gato)",
            "Edad de la mascota",
            "Raza (define si es de alta peligrosidad)",
            "Género de la mascota",
        ),
    ),
    "autos": ChecklistDef(
        modo="Sin intermediario",
        items=(
            "Placa",
            "Si es 0 km: marca, referencia y modelo",
            "Cédula del propietario",
            "Género",
            "Fecha de nacimiento",
            "Ciudad de circulación",
        ),
    ),
    "hogar": ChecklistDef(
        modo="Sin intermediario",
        items=(
            "Cédula del propietario",
            "¿Vivienda propia o arrendada?",
            "Estrato (dirección)",
            "Valor comercial del inmueble",
            "Tipo: casa, apto o finca recreo",
            "Sector rural o urbano",
            "Ciudad",
        ),
    ),
    "bicicletas": ChecklistDef(
        modo="Sin intermediario",
        items=(
            "Cédula",
            "Fecha de nacimiento",
            "Ciudad de residencia",
            "Valor del equipo (bicicleta o patineta eléctrica)",
        ),
    ),
    "accidentes": ChecklistDef(
        modo="Sin intermediario",
        items=None,
    ),
    "renta": ChecklistDef(
        modo="Con intermediario",
        items=None,
    ),
    "cancer": ChecklistDef(
        modo="Con intermediario",
        items=None,
    ),
    "arrendamiento": ChecklistDef(
        modo="Sin intermediario",
        items=None,
    ),
}

#: Fuentes públicas que sustentan los pesos. Se expone en la ficha de auditoría.
SOURCES: tuple[tuple[str, str, str], ...] = (
    (
        "Penetración del seguro",
        "Colombia cerró 2024 en 3,29% primas/PIB vs. 6,2% OCDE.",
        "Fasecolda / La República, feb-2025",
    ),
    (
        "Informalidad laboral",
        "55,4% de la población ocupada es informal (57,8% hombres, 51,9% mujeres).",
        "DANE, GEIH sep-nov 2025",
    ),
    (
        "Composición de hogares",
        "Hogar promedio 2,86 personas; 46,5% jefatura femenina, 68,8% de ellas sin pareja.",
        "DANE, ECV 2024",
    ),
    (
        "Vivienda",
        "40,4% en arriendo; 36% propia pagada; 3,5% pagándola.",
        "DANE, ECV 2024",
    ),
    (
        "Vida individual",
        "Solo ~16% de la PEA tiene vida individual; consumo per cápita ~$370.000/año.",
        "Fasecolda, dic-2024",
    ),
    (
        "Salud voluntaria",
        "~4,25M colombianos con esquema de salud voluntario adicional.",
        "Fasecolda / Acemi / Proesa, 2024",
    ),
    (
        "Cáncer por edad",
        "53,2% casos en hombres y 38,3% en mujeres ocurren en 65+ años.",
        "INC, 2022-2024",
    ),
    (
        "Exequial",
        "47,5% de hogares con algún esquema; solo 2,7% con póliza fúnebre formal.",
        "Superfinanciera / Fasecolda, 2018-2021",
    ),
    (
        "Autos y motos",
        "Solo 12,2% del parque tiene todo riesgo (27% carros, 2,8-3% motos).",
        "Fasecolda, 2024-2025",
    ),
    (
        "Hogar",
        "Solo 9,3% de hogares con seguro de vivienda voluntario; +70% atadas a hipoteca.",
        "Fasecolda / Semana, mar-2026",
    ),
    (
        "Mascotas",
        "60-70% de hogares tiene mascota; mercado crece 40% anual.",
        "DANE / Kantar / SURA, 2024-2026",
    ),
    (
        "Bicicletas y patinetas eléctricas",
        "Hurto de una bicicleta cada 2,5h en Bogotá (2025); el parque de patinetas eléctricas crece rápido y sin cifra de aseguramiento consolidada.",
        "Secretaría de Seguridad Bogotá, 2024-2026",
    ),
    (
        "Arrendamiento",
        "Costo típico 40-75% de un canon; 1 de cada 4 contratos termina en conflicto.",
        "Coriesgos / Inmobiliare Latam, 2026",
    ),
    (
        "Estratos e ingreso",
        "Clase media $853.608-$4.596.352 (32-34% de la población).",
        "DANE, GEIH 2024",
    ),
    (
        "Representatividad Colsubsidio",
        "Afilia principalmente trabajadores dependientes formales — mayor formalidad que el promedio nacional.",
        "Supuesto de trabajo — no público",
    ),
)

#: Perfiles de demostración usados por la CLI y por los tests.
CASE_PRESETS: tuple[dict, ...] = (
    {
        "label": "Madre soltera, 2 hijos, banco, 1 SMMLV",
        "afiliado": True,
        "profile": {
            "V1": "26-35 años",
            "V2": "Femenino",
            "V3": "Formal dependiente",
            "V4": "Bajo (< $1.3M)",
            "V5": "Monoparental con hijos",
            "V6": "Arrendada",
            "V7": "No",
            "V8": "No tiene",
            "V9": "No",
            "V10": "No",
            "V11": "Sí",
        },
    },
    {
        "label": "Joven en moto, informal, arrienda solo",
        "afiliado": False,
        "profile": {
            "V1": "18-25 años",
            "V2": "Masculino",
            "V3": "Informal / cuenta propia sin cotización",
            "V4": "Bajo (< $1.3M)",
            "V5": "Soltero(a) sin hijos",
            "V6": "Arrendada",
            "V7": "No",
            "V8": "Moto",
            "V9": "No",
            "V10": "No",
            "V11": "No",
        },
    },
    {
        "label": "Pareja con casa propia, mascota, ingreso alto",
        "afiliado": True,
        "profile": {
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
        },
    },
    {
        "label": "Adulto mayor a cargo de la familia",
        "afiliado": False,
        "profile": {
            "V1": "66+ años",
            "V2": "Masculino",
            "V3": "Formal dependiente",
            "V4": "Medio ($1.3M - $4.6M)",
            "V5": "Multigeneracional / adulto mayor a cargo",
            "V6": "Propia pagada",
            "V7": "No",
            "V8": "No tiene",
            "V9": "No",
            "V10": "No",
            "V11": "No",
        },
    },
)
