"""
Reto 01 — Motor de segmentación y oferta de crédito hiperpersonalizada
Hackathon Colsubsidio 2026 · Scala Labs

Qué hace (MVP): recibe el perfil de un afiliado, lo segmenta, calcula un score
de propensión/capacidad, y genera una oferta de crédito personalizada (monto,
tasa, plazo, canal y mensaje) CON la justificación de por qué esa oferta. La
transparencia es el diferenciador: no es una caja negra.

No inventa nada del afiliado: opera sobre los datos que recibe. La tasa por
categoría (A/B/C) refleja el modelo real de Colsubsidio (tasa preferencial según
categoría de afiliado); los números exactos son parámetros editables en TASA_BASE.

Corre solo con librería estándar:  python3 scoring_engine.py
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json

# --- Parámetros del negocio (editables) ---
SMMLV = 1_423_500  # salario mínimo 2025 (Col). Editar cada año.
TASA_BASE = {"A": 0.0165, "B": 0.0195, "C": 0.0225}  # tasa mensual por categoría de afiliado
CUOTA_MAX_INGRESO = 0.30  # la cuota no debe superar 30% del ingreso (capacidad de pago)
CANALES = ["WhatsApp", "App Colsubsidio", "Email", "Oficina"]


@dataclass
class Afiliado:
    id: str
    nombre: str
    categoria: str            # A / B / C
    ingreso_mensual: int
    edad: int
    antiguedad_meses: int      # antigüedad como afiliado
    productos_activos: int     # cuántos productos ya tiene
    mora_ultimos_12m: int      # veces en mora último año
    canal_preferido: str       # canal por el que más interactúa
    interes_declarado: str     # "vivienda" | "educacion" | "libre" | "vehiculo" ...


def segmentar(a: Afiliado) -> str:
    """Segmento simple y explicable a partir de comportamiento y capacidad."""
    if a.mora_ultimos_12m >= 2:
        return "Reconstrucción"           # historial a cuidar
    if a.ingreso_mensual >= 4 * SMMLV and a.antiguedad_meses >= 24:
        return "Consolidado"              # alta capacidad, relación larga
    if a.antiguedad_meses < 12:
        return "Nuevo por activar"
    return "Crecimiento"                  # base estable con recorrido


def score(a: Afiliado) -> int:
    """Score 0-100 de idoneidad de oferta. Reglas transparentes, sin caja negra."""
    s = 50
    s += min(a.ingreso_mensual / SMMLV, 6) * 5        # capacidad (hasta +30)
    s += min(a.antiguedad_meses / 12, 4) * 3          # relación (hasta +12)
    s -= a.mora_ultimos_12m * 12                       # riesgo (penaliza fuerte)
    s += 4 if a.productos_activos >= 2 else 0          # vinculación
    s += 3 if 25 <= a.edad <= 55 else 0                # ventana de vida activa
    return max(0, min(100, round(s)))


def oferta(a: Afiliado) -> dict:
    """Genera la oferta y su justificación. Devuelve dict listo para el agente Gemini."""
    seg = segmentar(a)
    sc = score(a)
    tasa = TASA_BASE.get(a.categoria, 0.0225)

    # Monto: función de ingreso, score y segmento (cap por capacidad de pago)
    factor_seg = {"Consolidado": 12, "Crecimiento": 8, "Nuevo por activar": 5,
                  "Reconstrucción": 3}[seg]
    monto_sugerido = int(a.ingreso_mensual * factor_seg * (sc / 100))
    monto_sugerido = max(SMMLV, min(monto_sugerido, 150_000_000))  # 1 SMMLV .. $150M

    # Plazo que mantiene la cuota <= 30% del ingreso
    plazo = 12
    for p in (12, 24, 36, 48, 60):
        cuota = monto_sugerido * (tasa * (1 + tasa) ** p) / ((1 + tasa) ** p - 1)
        if cuota <= a.ingreso_mensual * CUOTA_MAX_INGRESO:
            plazo = p
            break
    cuota = round(monto_sugerido * (tasa * (1 + tasa) ** plazo) /
                  ((1 + tasa) ** plazo - 1))

    canal = a.canal_preferido if a.canal_preferido in CANALES else "WhatsApp"
    producto = {"vivienda": "Crédito Vivienda", "educacion": "Crédito Educativo",
                "vehiculo": "Crédito Vehículo"}.get(a.interes_declarado,
                                                    "Crédito Libre Inversión")

    justificacion = [
        f"Categoría {a.categoria}: tasa preferencial {tasa*100:.2f}% mensual.",
        f"Segmento {seg} (score {sc}/100) por ingreso, antigüedad y comportamiento.",
        f"Plazo {plazo} meses para que la cuota (${cuota:,}) no pase del "
        f"{int(CUOTA_MAX_INGRESO*100)}% de tu ingreso.",
        f"Alineado a tu interés declarado: {producto}.",
    ]
    return {
        "afiliado": a.nombre,
        "segmento": seg,
        "score": sc,
        "producto": producto,
        "monto": monto_sugerido,
        "tasa_mensual": round(tasa, 4),
        "plazo_meses": plazo,
        "cuota_estimada": cuota,
        "canal_recomendado": canal,
        "justificacion": justificacion,
    }


# --- Perfiles demo para el pitch (editables/sustituibles por datos reales) ---
DEMO = [
    Afiliado("AF-1001", "Laura Mendoza", "A", 5_200_000, 34, 40, 3, 0, "App Colsubsidio", "vivienda"),
    Afiliado("AF-1002", "Diego Ruiz", "B", 1_900_000, 27, 8, 1, 0, "WhatsApp", "educacion"),
    Afiliado("AF-1003", "Marta Gómez", "C", 1_500_000, 45, 30, 2, 2, "Email", "libre"),
]

if __name__ == "__main__":
    for af in DEMO:
        print(json.dumps(oferta(af), ensure_ascii=False, indent=2))
        print("-" * 60)
