# -*- coding: utf-8 -*-
"""Stress test con 100 perfiles aleatorios válidos para motor-colsubsidio.py"""

import importlib.util
import random
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("motor-colsubsidio.py")
spec = importlib.util.spec_from_file_location("motor_colsubsidio_mod", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"No se pudo cargar el módulo desde {MODULE_PATH}")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

MotorScoring = mod.MotorScoring
VARIABLES = mod.VARIABLES

RANDOM_SEED = 20260724
TOTAL_PERFILES = 100


def random_profile(rng):
    return {v["code"]: rng.choice(v["categorias"]) for v in VARIABLES}


def main():
    rng = random.Random(RANDOM_SEED)
    motor = MotorScoring()
    errores = []
    muestras = []

    for i in range(1, TOTAL_PERFILES + 1):
        perfil = random_profile(rng)
        try:
            resultado = motor.calcular_scores(perfil)
            if len(resultado.ranking) != len(motor.products):
                errores.append((i, "ranking incompleto", perfil))
                continue
            if resultado.top is None:
                errores.append((i, "sin top", perfil))
                continue
            if any(not r.nombre for r in resultado.ranking):
                errores.append((i, "producto vacío", perfil))
                continue
            if any(resultado.ranking[j].score < resultado.ranking[j+1].score for j in range(len(resultado.ranking)-1)):
                errores.append((i, "ranking desordenado por score", perfil))
                continue
            if i <= 5:
                top3 = [(r.rank, r.nombre, r.score, r.pct) for r in resultado.ranking[:3]]
                muestras.append((i, perfil, top3))
        except Exception as e:
            errores.append((i, f"{type(e).__name__}: {e}", perfil))

    print("=" * 78)
    print("STRESS TEST — 100 PERFILES ALEATORIOS VÁLIDOS")
    print("=" * 78)
    print(f"Seed usada: {RANDOM_SEED}")
    print(f"Perfiles probados: {TOTAL_PERFILES}")
    print(f"Errores encontrados: {len(errores)}")
    print(f"Perfiles exitosos: {TOTAL_PERFILES - len(errores)}")

    print("Muestras de salida (primeros 5 casos):")
    for i, perfil, top3 in muestras:
        print(f"Caso #{i}")
        print(perfil)
        for rank, nombre, score, pct in top3:
            print(f"  #{rank} {nombre} — score {score}, afinidad {pct}%")

    if errores:
        print("Errores detectados:")
        for i, motivo, perfil in errores[:10]:
            print(f"- Caso #{i}: {motivo}")
            print(f"  Perfil: {perfil}")
        raise SystemExit(1)

    print("Resultado final: 100/100 perfiles OK")


if __name__ == "__main__":
    main()
