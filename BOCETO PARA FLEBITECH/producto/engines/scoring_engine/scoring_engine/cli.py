"""Demostración por consola del motor.

Ejecutar con ``python -m scoring_engine.cli``.
"""

from __future__ import annotations

from scoring_engine.catalog import CASE_PRESETS
from scoring_engine.engine import MotorScoring
from scoring_engine.reporting import ficha_texto, tabla_baselines, tabla_ranking

ANCHO = 104


def _titulo(texto: str) -> None:
    """Imprime un encabezado de sección.

    Args:
        texto: Título a mostrar.
    """
    print("\n" + "=" * ANCHO)
    print(texto)
    print("=" * ANCHO)


def main() -> None:
    """Corre la demo completa: pisos, rankings, ficha e influencia."""
    motor = MotorScoring()

    _titulo("PISO (BASELINE) POR PRODUCTO — distribución uniforme")
    print(tabla_baselines(motor.baselines, motor))

    for caso in CASE_PRESETS:
        _titulo(f"CASO: {caso['label']}")
        resultado = motor.calcular(caso["profile"])
        print(tabla_ranking(resultado, top_n=5))

    _titulo("FICHA DE CIERRE — primer caso")
    primero = CASE_PRESETS[0]
    print(ficha_texto(motor, motor.calcular(primero["profile"]), primero["afiliado"]))

    _titulo("INFLUENCIA DE VARIABLES")
    for item in motor.influencia_variables():
        tipo = "estructural" if item["estructural"] else "condicional"
        print(
            f"{item['code']:>4} {item['label'][:48]:<50} "
            f"{tipo:<12} {item['influence']:>3}"
        )


if __name__ == "__main__":
    main()
