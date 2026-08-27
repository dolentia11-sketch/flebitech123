# -*- coding: utf-8 -*-
"""
Motor de Scoring de Seguros — Colsubsidio
Motor MVP en Python puro, sin APIs externas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

PRODUCTS: List[Dict[str, str]] = [
  {
    "key": "vida",
    "nombre": "Vida",
    "linea": "Familia"
  },
  {
    "key": "accidentes",
    "nombre": "Accidentes personales",
    "linea": "Familia"
  },
  {
    "key": "renta",
    "nombre": "Renta por hospitalización",
    "linea": "Familia"
  },
  {
    "key": "cancer",
    "nombre": "Diagnóstico positivo de cáncer",
    "linea": "Familia"
  },
  {
    "key": "salud",
    "nombre": "Póliza de salud",
    "linea": "Familia"
  },
  {
    "key": "exequial",
    "nombre": "Exequial familiar",
    "linea": "Familia"
  },
  {
    "key": "mascotas",
    "nombre": "Seguro de mascotas",
    "linea": "Familia"
  },
  {
    "key": "autos",
    "nombre": "Todo riesgo autos y motos",
    "linea": "Patrimonio"
  },
  {
    "key": "hogar",
    "nombre": "Todo riesgo hogar",
    "linea": "Patrimonio"
  },
  {
    "key": "bicicletas",
    "nombre": "Bicicletas y patinetas eléctricas",
    "linea": "Patrimonio"
  },
  {
    "key": "arrendamiento",
    "nombre": "Arrendamiento",
    "linea": "Patrimonio"
  },
  {
    "key": "educacion",
    "nombre": "Educación",
    "linea": "Familia"
  }
]

MAXS: List[int] = [
  31,
  24,
  23,
  21,
  24,
  24,
  25,
  25,
  24,
  21,
  20,
  25
]

VARIABLES: List[Dict[str, Any]] = [
  {
    "code": "V1",
    "label": "Rango de edad",
    "categorias": [
      "18-25 años",
      "26-35 años",
      "36-45 años",
      "46-55 años",
      "56-65 años",
      "66+ años"
    ]
  },
  {
    "code": "V2",
    "label": "Género",
    "categorias": [
      "Masculino",
      "Femenino"
    ]
  },
  {
    "code": "V3",
    "label": "Situación laboral",
    "categorias": [
      "Formal dependiente",
      "Formal independiente / profesional",
      "Informal / cuenta propia sin cotización"
    ]
  },
  {
    "code": "V4",
    "label": "Nivel de ingreso mensual",
    "categorias": [
      "Bajo (< $1.3M)",
      "Medio ($1.3M - $4.6M)",
      "Alto (> $4.6M)"
    ]
  },
  {
    "code": "V5",
    "label": "Composición familiar",
    "categorias": [
      "Soltero(a) sin hijos",
      "Pareja sin hijos",
      "Con hijos menores de edad",
      "Monoparental con hijos",
      "Multigeneracional / adulto mayor a cargo"
    ]
  },
  {
    "code": "V6",
    "label": "Tipo de vivienda",
    "categorias": [
      "Propia pagada",
      "Propia financiada (hipoteca)",
      "Arrendada"
    ]
  },
  {
    "code": "V7",
    "label": "¿Es propietario que arrienda un inmueble a terceros?",
    "categorias": [
      "Sí",
      "No"
    ]
  },
  {
    "code": "V8",
    "label": "Tenencia de vehículo",
    "categorias": [
      "Carro",
      "Moto",
      "No tiene"
    ]
  },
  {
    "code": "V9",
    "label": "¿Tiene mascota (perro o gato)?",
    "categorias": [
      "Sí",
      "No"
    ]
  },
  {
    "code": "V10",
    "label": "¿Usa bicicleta o patineta eléctrica como transporte o deporte habitual?",
    "categorias": [
      "Sí",
      "No"
    ]
  },
  {
    "code": "V11",
    "label": "¿Es jefatura de hogar femenina sin pareja?",
    "categorias": [
      "Sí",
      "No"
    ]
  }
]

AFILIADO_EN_SISTEMA = ["V1", "V2", "V3", "V4", "V5"]
SIEMPRE_PREGUNTAR = ["V6", "V7", "V8", "V9", "V10", "V11"]

WEIGHTS: Dict[str, List[int]] = {
  "V1|18-25 años": [
    1,
    3,
    1,
    0,
    2,
    1,
    3,
    1,
    1,
    4,
    1,
    1
  ],
  "V1|26-35 años": [
    3,
    3,
    2,
    1,
    3,
    1,
    4,
    3,
    2,
    3,
    3,
    3
  ],
  "V1|36-45 años": [
    5,
    2,
    3,
    2,
    3,
    2,
    3,
    4,
    4,
    2,
    3,
    5
  ],
  "V1|46-55 años": [
    4,
    2,
    4,
    4,
    4,
    3,
    2,
    4,
    4,
    1,
    2,
    3
  ],
  "V1|56-65 años": [
    2,
    2,
    5,
    5,
    4,
    4,
    1,
    3,
    3,
    1,
    1,
    1
  ],
  "V1|66+ años": [
    1,
    2,
    5,
    5,
    3,
    5,
    1,
    1,
    2,
    0,
    0,
    0
  ],
  "V2|Masculino": [
    3,
    3,
    2,
    3,
    2,
    2,
    2,
    3,
    2,
    3,
    2,
    2
  ],
  "V2|Femenino": [
    4,
    2,
    3,
    4,
    3,
    3,
    4,
    2,
    2,
    2,
    2,
    3
  ],
  "V3|Formal dependiente": [
    2,
    1,
    1,
    2,
    3,
    2,
    2,
    3,
    3,
    2,
    2,
    3
  ],
  "V3|Formal independiente / profesional": [
    5,
    4,
    4,
    3,
    4,
    2,
    2,
    3,
    3,
    2,
    3,
    4
  ],
  "V3|Informal / cuenta propia sin cotización": [
    3,
    5,
    3,
    1,
    1,
    4,
    1,
    1,
    1,
    1,
    1,
    2
  ],
  "V4|Bajo (< $1.3M)": [
    1,
    3,
    1,
    1,
    0,
    4,
    1,
    0,
    0,
    2,
    0,
    1
  ],
  "V4|Medio ($1.3M - $4.6M)": [
    3,
    3,
    3,
    3,
    3,
    2,
    3,
    3,
    3,
    2,
    2,
    3
  ],
  "V4|Alto (> $4.6M)": [
    4,
    2,
    3,
    3,
    5,
    1,
    4,
    5,
    5,
    1,
    4,
    4
  ],
  "V5|Soltero(a) sin hijos": [
    1,
    3,
    1,
    1,
    2,
    1,
    4,
    2,
    1,
    4,
    1,
    0
  ],
  "V5|Pareja sin hijos": [
    2,
    2,
    2,
    2,
    3,
    2,
    4,
    3,
    4,
    2,
    2,
    0
  ],
  "V5|Con hijos menores de edad": [
    5,
    3,
    4,
    3,
    5,
    3,
    2,
    3,
    4,
    1,
    1,
    5
  ],
  "V5|Monoparental con hijos": [
    5,
    3,
    3,
    2,
    3,
    4,
    1,
    1,
    2,
    1,
    1,
    4
  ],
  "V5|Multigeneracional / adulto mayor a cargo": [
    3,
    2,
    5,
    4,
    3,
    5,
    1,
    1,
    2,
    0,
    0,
    2
  ],
  "V6|Propia pagada": [
    2,
    1,
    1,
    1,
    2,
    1,
    2,
    2,
    5,
    1,
    1,
    1
  ],
  "V6|Propia financiada (hipoteca)": [
    3,
    1,
    1,
    1,
    2,
    1,
    1,
    2,
    5,
    1,
    1,
    1
  ],
  "V6|Arrendada": [
    1,
    1,
    1,
    1,
    1,
    1,
    2,
    1,
    1,
    1,
    0,
    1
  ],
  "V7|Sí": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    5,
    0
  ],
  "V7|No": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "V8|Carro": [
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    5,
    0,
    0,
    0,
    0
  ],
  "V8|Moto": [
    2,
    3,
    1,
    0,
    0,
    0,
    0,
    3,
    0,
    0,
    0,
    0
  ],
  "V8|No tiene": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "V9|Sí": [
    0,
    0,
    0,
    0,
    0,
    0,
    5,
    0,
    0,
    0,
    0,
    0
  ],
  "V9|No": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "V10|Sí": [
    0,
    2,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    5,
    0,
    0
  ],
  "V10|No": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "V11|Sí": [
    3,
    1,
    1,
    1,
    1,
    2,
    0,
    0,
    0,
    0,
    0,
    3
  ],
  "V11|No": [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ]
}

RATIONALE: Dict[str, str] = {
  "V1|18-25 años": "Prioridad en bicicleta/patineta eléctrica y mascota (perfil joven urbano); vida y cáncer casi irrelevantes a esta edad.",
  "V1|26-35 años": "Edad pico de tenencia de mascota (30-50 años, SURA) y de arriendo (DANE); comienza a evaluar vida y autos.",
  "V1|36-45 años": "Pico de compra de vivienda y auto propio; arranca la lógica HLV/DIME de vida por responsabilidades familiares.",
  "V1|46-55 años": "21,7% de casos de cáncer ocurre en 55-64 años, el riesgo ya es relevante desde los 46; renta por hospitalización sube.",
  "V1|56-65 años": "Cáncer y renta hospitalización en niveles altos; exequial empieza a ganar peso.",
  "V1|66+ años": "53,2% de los casos de cáncer en hombres ocurre en 65+ años (INC); exequial es prioridad máxima.",
  "V2|Masculino": "Mayor peso relativo en autos/motos y cáncer de próstata/estómago.",
  "V2|Femenino": "76% de clientes de seguros de mascotas son mujeres (SURA); mayor probabilidad de jefatura de hogar.",
  "V3|Formal dependiente": "Ya cuenta con EPS, ARL y pensión vía empleador; prioridad en complementarios por mayor estabilidad de ingreso.",
  "V3|Formal independiente / profesional": "Sin seguro de vida grupal ni ARL automática; el 84% de la PEA no tiene vida individual (Fasecolda).",
  "V3|Informal / cuenta propia sin cotización": "55,4% de la población ocupada (DANE); sin ARL ni pensión, accidentes y exequial son la protección más accesible.",
  "V4|Bajo (< $1.3M)": "Capacidad de pago limitada a prima baja; exequial tiene fuerte arraigo cultural en estratos bajos.",
  "V4|Medio ($1.3M - $4.6M)": "Segmento de clase media (32-34% de la población, DANE) — el segmento con mayor potencial de conversión.",
  "V4|Alto (> $4.6M)": "Mayor probabilidad de vivienda y vehículo propios; foco en salud complementaria y patrimonio.",
  "V5|Soltero(a) sin hijos": "Sin dependientes económicos; prioridad en mascota, bicicleta/patineta eléctrica y accidentes personales sobre vida.",
  "V5|Pareja sin hijos": "Enfoque en patrimonio compartido (hogar, auto) y mascota.",
  "V5|Con hijos menores de edad": "Máxima prioridad en vida y salud familiar (lógica HLV/DIME); sube renta por hospitalización y educación.",
  "V5|Monoparental con hijos": "24,3% de los hogares (DANE); único proveedor, vida, exequial y educación son críticos.",
  "V5|Multigeneracional / adulto mayor a cargo": "Mayor probabilidad de necesitar renta por hospitalización, cáncer y exequial para el adulto mayor.",
  "V6|Propia pagada": "Activo consolidado sin deuda; el seguro de hogar es decisión 100% voluntaria.",
  "V6|Propia financiada (hipoteca)": "+70% de pólizas de hogar atadas a crédito hipotecario (Fasecolda) — casi obligatorio en la práctica.",
  "V6|Arrendada": "Menor necesidad de seguro de hogar; puede necesitar seguro de contenidos básico.",
  "V7|Sí": "Oportunidad de venta cruzada específica de Arrendamiento (garantía a terceros).",
  "V7|No": "Sin relevancia en esta variable.",
  "V8|Carro": "Solo 12,2% del parque automotor tiene todo riesgo (Fasecolda) — alta oportunidad.",
  "V8|Moto": "Motos son 61-63% del parque pero solo 2,8-3% tiene todo riesgo — brecha grande; sube accidentes personales.",
  "V8|No tiene": "Sin relevancia para productos de vehículo.",
  "V9|Sí": "Oportunidad de venta cruzada directa de Mascotas.",
  "V9|No": "Sin relevancia en esta variable.",
  "V10|Sí": "Oportunidad de venta cruzada directa de Bicicletas y patinetas eléctricas (hurto cada 2,5h en Bogotá, 2025).",
  "V10|No": "Sin relevancia en esta variable.",
  "V11|Sí": "46,5% jefatura femenina, 68,8% sin pareja (DANE) — foco especial del ICP de soycaropinzón; también sube educación por ser único proveedor.",
  "V11|No": "Sin relevancia en esta variable."
}

CHECKLIST: Dict[str, Dict[str, Any]] = {
  "vida": {
    "modo": "Con intermediario",
    "items": [
      "Cédula",
      "Fecha de nacimiento",
      "Género",
      "¿Conduce moto? Sí/No",
      "¿Actividades de alto riesgo? Sí/No",
      "Valor a asegurar",
      "Ocupación o profesión",
      "— Vida oneroso: valor del crédito",
      "— Vida ahorro: valor de la póliza + ahorro mensual deseado"
    ]
  },
  "salud": {
    "modo": "Con intermediario",
    "items": [
      "Cédula",
      "Fecha de nacimiento",
      "Ciudad",
      "Preexistencias (diabetes, cáncer, VIH, etc.)",
      "Coberturas preferidas (maternidad, cáncer, alto costo)",
      "Ocupación"
    ]
  },
  "educacion": {
    "modo": "Con intermediario",
    "items": [
      "Cédula del asegurado (quien compra el seguro)",
      "Fecha de nacimiento del asegurado",
      "Ocupación",
      "Ciudad de residencia",
      "Fecha de nacimiento del hijo",
      "Grado de escolaridad",
      "Valor mensual o anual que está dispuesto a invertir en la educación del hijo, o valor que desea asegurar para sus estudios"
    ]
  },
  "exequial": {
    "modo": "Sin intermediario",
    "items": [
      "Cédula del afiliado principal",
      "Grupo familiar (padres, hijos, tíos, hermanos, primos)",
      "Edades de cada uno"
    ]
  },
  "mascotas": {
    "modo": "Sin intermediario",
    "items": [
      "Cédula del propietario",
      "Género del propietario",
      "Fecha de nacimiento",
      "Tipo de mascota (perro/gato)",
      "Edad de la mascota",
      "Raza (define si es de alta peligrosidad)",
      "Género de la mascota"
    ]
  },
  "autos": {
    "modo": "Sin intermediario",
    "items": [
      "Placa",
      "Si es 0 km: marca, referencia y modelo",
      "Cédula del propietario",
      "Género",
      "Fecha de nacimiento",
      "Ciudad de circulación"
    ]
  },
  "hogar": {
    "modo": "Sin intermediario",
    "items": [
      "Cédula del propietario",
      "¿Vivienda propia o arrendada?",
      "Estrato (dirección)",
      "Valor comercial del inmueble",
      "Tipo: casa, apto o finca recreo",
      "Sector rural o urbano",
      "Ciudad"
    ]
  },
  "bicicletas": {
    "modo": "Sin intermediario",
    "items": [
      "Cédula",
      "Fecha de nacimiento",
      "Ciudad de residencia",
      "Valor del equipo (bicicleta o patineta eléctrica)"
    ]
  },
  "accidentes": {
    "modo": "Sin intermediario",
    "items": None
  },
  "renta": {
    "modo": "Con intermediario",
    "items": None
  },
  "cancer": {
    "modo": "Con intermediario",
    "items": None
  },
  "arrendamiento": {
    "modo": "Sin intermediario",
    "items": None
  }
}

SOURCES: List[Dict[str, str]] = [
  [
    "Penetración del seguro",
    "Colombia cerró 2024 en 3,29% primas/PIB vs. 6,2% OCDE.",
    "Fasecolda / La República, feb-2025"
  ],
  [
    "Informalidad laboral",
    "55,4% de la población ocupada es informal (57,8% hombres, 51,9% mujeres).",
    "DANE, GEIH sep-nov 2025"
  ],
  [
    "Composición de hogares",
    "Hogar promedio 2,86 personas; 46,5% jefatura femenina, 68,8% de ellas sin pareja.",
    "DANE, ECV 2024"
  ],
  [
    "Vivienda",
    "40,4% en arriendo; 36% propia pagada; 3,5% pagándola.",
    "DANE, ECV 2024"
  ],
  [
    "Vida individual",
    "Solo ~16% de la PEA tiene vida individual; consumo per cápita ~$370.000/año.",
    "Fasecolda, dic-2024"
  ],
  [
    "Salud voluntaria",
    "~4,25M colombianos con esquema de salud voluntario adicional.",
    "Fasecolda / Acemi / Proesa, 2024"
  ],
  [
    "Cáncer por edad",
    "53,2% casos en hombres y 38,3% en mujeres ocurren en 65+ años.",
    "INC, 2022-2024"
  ],
  [
    "Exequial",
    "47,5% de hogares con algún esquema; solo 2,7% con póliza fúnebre formal.",
    "Superfinanciera / Fasecolda, 2018-2021"
  ],
  [
    "Autos y motos",
    "Solo 12,2% del parque tiene todo riesgo (27% carros, 2,8-3% motos).",
    "Fasecolda, 2024-2025"
  ],
  [
    "Hogar",
    "Solo 9,3% de hogares con seguro de vivienda voluntario; +70% atadas a hipoteca.",
    "Fasecolda / Semana, mar-2026"
  ],
  [
    "Mascotas",
    "60-70% de hogares tiene mascota; mercado crece 40% anual.",
    "DANE / Kantar / SURA, 2024-2026"
  ],
  [
    "Bicicletas y patinetas eléctricas",
    "Hurto de una bicicleta cada 2,5h en Bogotá (2025); el parque de patinetas eléctricas crece rápido y sin cifra de aseguramiento consolidada.",
    "Secretaría de Seguridad Bogotá, 2024-2026"
  ],
  [
    "Arrendamiento",
    "Costo típico 40-75% de un canon; 1 de cada 4 contratos termina en conflicto.",
    "Coriesgos / Inmobiliare Latam, 2026"
  ],
  [
    "Estratos e ingreso",
    "Clase media $853.608-$4.596.352 (32-34% de la población).",
    "DANE, GEIH 2024"
  ],
  [
    "Representatividad Colsubsidio",
    "Afilia principalmente trabajadores dependientes formales — mayor formalidad que el promedio nacional.",
    "Supuesto de trabajo — no público"
  ]
]

CASE_PRESETS: List[Dict[str, Any]] = [
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
      "V11": "Sí"
    }
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
      "V11": "No"
    }
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
      "V11": "No"
    }
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
      "V11": "No"
    }
  }
]


@dataclass
class ResultadoProducto:
    key: str
    nombre: str
    linea: str
    score: int
    max_score: int
    pct: float
    modo_cierre: str
    rank: int = 0
    forced_explicit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "nombre": self.nombre,
            "linea": self.linea,
            "score": self.score,
            "max_score": self.max_score,
            "pct": self.pct,
            "modo_cierre": self.modo_cierre,
            "rank": self.rank,
            "forced_explicit": self.forced_explicit,
        }


@dataclass
class DesgloseVariable:
    code: str
    variable: str
    categoria: str
    pesos: List[int]
    rationale: str


@dataclass
class ResultadoScoring:
    perfil: Dict[str, str]
    producto_explicito: Optional[str]
    ranking: List[ResultadoProducto]
    desglose: List[DesgloseVariable]

    @property
    def top(self) -> ResultadoProducto:
        return self.ranking[0]

    @property
    def top_3(self) -> List[ResultadoProducto]:
        return self.ranking[:3]


class MotorScoring:
    def __init__(self):
        self.products = PRODUCTS
        self.maxs = MAXS
        self.variables = VARIABLES
        self.weights = WEIGHTS
        self.rationale = RATIONALE
        self.checklist = CHECKLIST
        self.sources = SOURCES
        self.case_presets = CASE_PRESETS
        self._product_index = {p["key"]: i for i, p in enumerate(self.products)}
        self._variable_by_code = {v["code"]: v for v in self.variables}

    def _pesos_para(self, code: str, categoria: str) -> List[int]:
        clave = f"{code}|{categoria}"
        return self.weights.get(clave, [0] * len(self.products))

    def modo_cierre(self, product_key: str) -> str:
        modo = self.checklist.get(product_key, {}).get("modo", "")
        return "auto" if str(modo).strip().lower() == "sin intermediario" else "asesoria"

    def calcular_scores(self, perfil: Dict[str, str], producto_explicito: Optional[str] = None) -> ResultadoScoring:
        faltantes = [v["code"] for v in self.variables if v["code"] not in perfil]
        if faltantes:
            raise ValueError(f"Faltan variables en el perfil: {', '.join(faltantes)}")

        totales = [0] * len(self.products)
        desglose: List[DesgloseVariable] = []

        for var in self.variables:
            code = var["code"]
            categoria = perfil[code]
            if categoria not in var["categorias"]:
                raise ValueError(f"Categoría inválida para {code}: {categoria!r}")
            pesos = self._pesos_para(code, categoria)
            for i, p in enumerate(pesos):
                totales[i] += p
            desglose.append(DesgloseVariable(
                code=code,
                variable=var["label"],
                categoria=categoria,
                pesos=pesos,
                rationale=self.rationale.get(f"{code}|{categoria}", ""),
            ))

        resultados: List[ResultadoProducto] = []
        for i, prod in enumerate(self.products):
            maximo = self.maxs[i]
            score = totales[i]
            resultados.append(ResultadoProducto(
                key=prod["key"],
                nombre=prod["nombre"],
                linea=prod["linea"],
                score=score,
                max_score=maximo,
                pct=round(score / maximo * 100, 1) if maximo else 0.0,
                modo_cierre=self.modo_cierre(prod["key"]),
            ))

        resultados.sort(key=lambda r: (r.score, r.pct), reverse=True)
        resultados = self._reordenar_por_explicito(resultados, producto_explicito)
        for i, r in enumerate(resultados, start=1):
            r.rank = i

        return ResultadoScoring(
            perfil=perfil,
            producto_explicito=producto_explicito,
            ranking=resultados,
            desglose=desglose,
        )

    def _reordenar_por_explicito(self, resultados: List[ResultadoProducto], product_key: Optional[str]) -> List[ResultadoProducto]:
        if not product_key:
            return resultados
        idx = next((i for i, r in enumerate(resultados) if r.key == product_key), None)
        if idx is None or idx == 0:
            return resultados
        elegido = resultados[idx]
        elegido.forced_explicit = True
        resto = [r for r in resultados if r.key != product_key]
        return [elegido] + resto

    def influencia_variables(self) -> List[Dict[str, Any]]:
        salida = []
        for var in self.variables:
            pesos_por_categoria = [self._pesos_para(var["code"], c) for c in var["categorias"]]
            rangos_por_producto = []
            total = 0
            for i in range(len(self.products)):
                vals = [pesos[i] for pesos in pesos_por_categoria]
                rango = max(vals) - min(vals)
                rangos_por_producto.append(rango)
                total += rango
            salida.append({
                "code": var["code"],
                "label": var["label"],
                "influence": total,
                "por_producto": rangos_por_producto,
            })
        salida.sort(key=lambda x: x["influence"], reverse=True)
        return salida

    def top_variables_influyentes(self, n: int = 6) -> List[str]:
        return [v["code"] for v in self.influencia_variables()[:n]]

    def reglas_de_producto(self, product_key: str, n: int = 6) -> List[Dict[str, Any]]:
        if product_key not in self._product_index:
            raise KeyError(f"Producto desconocido: {product_key}")
        idx = self._product_index[product_key]
        reglas = []
        for var in self.variables:
            mejor_cat, mejor_peso, mejor_rat = None, -1, ""
            for cat in var["categorias"]:
                peso = self._pesos_para(var["code"], cat)[idx]
                if peso > mejor_peso:
                    mejor_cat, mejor_peso = cat, peso
                    mejor_rat = self.rationale.get(f"{var['code']}|{cat}", "")
            reglas.append({
                "code": var["code"],
                "label": var["label"],
                "categoria": mejor_cat,
                "peso": mejor_peso,
                "rationale": mejor_rat,
            })
        reglas.sort(key=lambda x: x["peso"], reverse=True)
        return reglas[:n]

    def checklist_producto(self, product_key: str) -> Dict[str, Any]:
        return self.checklist.get(product_key, {"modo": None, "items": None})

    def ficha_texto(self, perfil: Dict[str, str], producto_explicito: Optional[str] = None, afiliado: Optional[bool] = None) -> str:
        resultado = self.calcular_scores(perfil, producto_explicito)
        top = resultado.top
        modo = top.modo_cierre
        checklist = self.checklist_producto(top.key)

        perfil_lineas = "\n".join(
            f"- {d.code} {d.variable}: {d.categoria}" for d in resultado.desglose
        )

        idx_top = self._product_index[top.key]
        racional_top = [
            f"- {d.rationale}" for d in resultado.desglose
            if d.pesos[idx_top] >= 3 and d.rationale
        ]
        racional_txt = "\n".join(racional_top) if racional_top else "(sin racional destacado)"

        if checklist.get("items"):
            checklist_txt = "\n".join(f"- {item}" for item in checklist["items"])
        else:
            checklist_txt = "(sin checklist documentado — usar datos base y validar con Colsubsidio)"

        header = (
            f"FICHA DE CIERRE AUTOMATIZADO — {top.nombre}" if modo == "auto"
            else f"RESUMEN PARA ASESOR — {top.nombre}"
        )
        afiliado_txt = "N/D" if afiliado is None else ("Sí" if afiliado else "No")
        siguiente_paso = (
            "Siguiente paso: pasar esta ficha a cotización y pago en línea."
            if modo == "auto" else
            "Siguiente paso: enviar este resumen al asesor para agendar la llamada."
        )

        return (
            f"{header}\n"
            f"Perfilador Colsubsidio — motor de reglas\n\n"
            f"Cliente afiliado a Colsubsidio: {afiliado_txt}\n"
            f"Producto recomendado: {top.nombre} ({top.linea}) — {top.pct}% de afinidad, score {top.score}/{top.max_score}\n"
            f"Modo de cierre: {'Sin intermediario — cierre automatizado' if modo == 'auto' else 'Con intermediario — asesoría personalizada'}\n\n"
            f"Perfil capturado:\n{perfil_lineas}\n\n"
            f"Por qué este producto:\n{racional_txt}\n\n"
            f"Datos para cotizar:\n{checklist_txt}\n\n"
            f"{siguiente_paso}"
        )

    def resumen_ranking_texto(self, resultado: ResultadoScoring, top_n: int = 3) -> str:
        lineas = []
        for r in resultado.ranking[:top_n]:
            etiqueta = "★ solicitado por el cliente" if r.forced_explicit else ""
            lineas.append(
                f"#{r.rank} {r.nombre} ({r.linea}) — {r.pct}% afinidad, score {r.score}/{r.max_score}, modo: {r.modo_cierre} {etiqueta}".strip()
            )
        return "\n".join(lineas)


def _demo():
    motor = MotorScoring()
    print("=" * 78)
    print("MOTOR DE SCORING DE SEGUROS — COLSUBSIDIO (motor de reglas en Python)")
    print("=" * 78)

    for caso in motor.case_presets:
        print(f"\n--- Caso: {caso['label']} (afiliado: {'Sí' if caso['afiliado'] else 'No'}) ---")
        resultado = motor.calcular_scores(caso["profile"])
        print(motor.resumen_ranking_texto(resultado, top_n=3))

    print("\n" + "=" * 78)
    print("Ficha de cierre para el primer caso:")
    print("=" * 78)
    primero = motor.case_presets[0]
    print(motor.ficha_texto(primero["profile"], afiliado=primero["afiliado"]))

    print("\n" + "=" * 78)
    print("Variables más influyentes en el score (top 5):")
    print("=" * 78)
    for v in motor.influencia_variables()[:5]:
        print(f"- {v['code']}: {v['label']} -> influencia {v['influence']}")

    print("\n" + "=" * 78)
    print("Motor de reglas leído por producto — Autos y motos (top 5 variables):")
    print("=" * 78)
    for r in motor.reglas_de_producto("autos", n=5):
        print(f"- {r['code']} {r['label']}: {r['categoria']} (peso {r['peso']}) — {r['rationale']}")


if __name__ == "__main__":
    _demo()
