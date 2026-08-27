"""
Reto 02 — Motor de recomendación y cotización de seguros
Hackathon Colsubsidio 2026 · Scala Labs

Qué hace (MVP): a partir de pocas respuestas del afiliado (edad, dependientes,
vivienda, principal preocupación, ingreso), detecta la necesidad, recomienda un
producto del catálogo Colsubsidio/MetLife, calcula la prima y arma la cotización
con una nota de idoneidad. Cubre el paso de "no sé qué seguro necesito" a una
oferta concreta lista para cerrar.

El agente conversacional (Gemini) hace las preguntas y explica; este motor pone
los números. Así el modelo no inventa primas: las calcula el motor.

Corre solo con librería estándar:  python3 quote_engine.py
"""
from __future__ import annotations
from dataclasses import dataclass
import json

# --- Catálogo (parámetros editables; tarifas base ilustrativas para el MVP) ---
CATALOGO = {
    "vida": {
        "nombre": "Seguro de Vida",
        "prima_base": 18000,          # mensual, cobertura base
        "cobertura_base": 50_000_000,
        "atiende": "proteger a quien depende de ti si faltas",
    },
    "accidentes": {
        "nombre": "Accidentes Personales",
        "prima_base": 9000,
        "cobertura_base": 30_000_000,
        "atiende": "un accidente que te deje sin ingresos",
    },
    "exequial": {
        "nombre": "Seguro Exequial Familiar",
        "prima_base": 12000,
        "cobertura_base": 8_000_000,
        "atiende": "no dejarle a tu familia el gasto de un funeral",
    },
    "hogar": {
        "nombre": "Seguro de Hogar",
        "prima_base": 22000,
        "cobertura_base": 80_000_000,
        "atiende": "proteger tu vivienda y lo que hay dentro",
    },
    "desempleo": {
        "nombre": "Protección Desempleo",
        "prima_base": 15000,
        "cobertura_base": 6_000_000,
        "atiende": "cubrir tus cuotas si pierdes el empleo",
    },
}

# Mapa preocupación -> producto principal
PREOCUPACION_A_PRODUCTO = {
    "familia": "vida",
    "salud": "accidentes",
    "muerte": "exequial",
    "casa": "hogar",
    "empleo": "desempleo",
}


@dataclass
class Respuestas:
    nombre: str
    edad: int
    dependientes: int
    tiene_vivienda: bool
    ingreso_mensual: int
    preocupacion: str        # familia | salud | muerte | casa | empleo


def recomendar(r: Respuestas) -> str:
    """Detecta la necesidad. La preocupación manda; si no hay match, usa reglas."""
    if r.preocupacion in PREOCUPACION_A_PRODUCTO:
        return PREOCUPACION_A_PRODUCTO[r.preocupacion]
    if r.dependientes >= 1:
        return "vida"
    if r.tiene_vivienda:
        return "hogar"
    return "accidentes"


def factor_edad(edad: int) -> float:
    if edad < 30:
        return 0.85
    if edad < 45:
        return 1.0
    if edad < 60:
        return 1.35
    return 1.8


def cotizar(r: Respuestas) -> dict:
    key = recomendar(r)
    p = CATALOGO[key]

    # Cobertura sugerida: escala con dependientes e ingreso (con tope del producto x3)
    escala = 1 + 0.4 * r.dependientes + min(r.ingreso_mensual / 3_000_000, 2)
    cobertura = int(min(p["cobertura_base"] * escala, p["cobertura_base"] * 3))
    prima = round(p["prima_base"] * factor_edad(r.edad) * (cobertura / p["cobertura_base"]))

    # Nota de idoneidad (responde a la objeción regulatoria: venta adecuada)
    idoneidad = (
        f"Te recomendamos {p['nombre']} porque tu principal preocupación es "
        f"{p['atiende']}. Con {r.dependientes} persona(s) que dependen de ti y "
        f"tu perfil, esta cobertura se ajusta a tu situación."
    )
    return {
        "afiliado": r.nombre,
        "producto": p["nombre"],
        "producto_key": key,
        "cobertura": cobertura,
        "prima_mensual": prima,
        "vigencia": "12 meses renovable",
        "idoneidad": idoneidad,
        "requiere_consentimiento": True,
        "estado": "cotizada",
    }


def emitir(cotizacion: dict, acepta: bool, consentimiento: bool) -> dict:
    """Cierre instantáneo: solo emite si hay aceptación Y consentimiento."""
    if not (acepta and consentimiento):
        return {**cotizacion, "estado": "no_emitida",
                "motivo": "Falta aceptación o consentimiento."}
    numero = "POL-" + str(abs(hash(cotizacion["afiliado"])) % 1_000_000).zfill(6)
    return {**cotizacion, "estado": "emitida", "numero_poliza": numero,
            "mensaje": f"Quedaste asegurado. Póliza {numero}, "
                       f"prima ${cotizacion['prima_mensual']:,}/mes."}


# --- Perfiles demo para el pitch ---
DEMO = [
    Respuestas("Laura Mendoza", 34, 2, True, 5_200_000, "familia"),
    Respuestas("Diego Ruiz", 27, 0, False, 1_900_000, "salud"),
    Respuestas("Marta Gómez", 45, 1, False, 1_500_000, "empleo"),
]

if __name__ == "__main__":
    for r in DEMO:
        c = cotizar(r)
        poliza = emitir(c, acepta=True, consentimiento=True)
        print(json.dumps(poliza, ensure_ascii=False, indent=2))
        print("-" * 60)
