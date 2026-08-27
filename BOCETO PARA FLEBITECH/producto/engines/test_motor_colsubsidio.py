# -*- coding: utf-8 -*-
"""Batería de pruebas para motor-colsubsidio.py"""

import importlib.util
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


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def run_case(nombre, fn):
    try:
        fn()
        print(f"[OK] {nombre}")
        return True
    except Exception as e:
        print(f"[FAIL] {nombre}: {type(e).__name__}: {e}")
        return False


def perfil_base():
    return {
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
    }


def test_caso_valido_afiliado():
    motor = MotorScoring()
    resultado = motor.calcular_scores(perfil_base())
    assert_true(len(resultado.ranking) == len(motor.products), "El ranking no contiene todos los productos")
    assert_true(resultado.top is not None, "No hay top producto")
    assert_true(all(r.rank >= 1 for r in resultado.ranking), "Hay ranks inválidos")
    assert_true(
        all(
            resultado.ranking[i].score >= resultado.ranking[i + 1].score
            or (
                resultado.ranking[i].score == resultado.ranking[i + 1].score
                and resultado.ranking[i].pct >= resultado.ranking[i + 1].pct
            )
            for i in range(len(resultado.ranking) - 1)
        ),
        "El ranking quedó desordenado",
    )


def test_caso_valido_no_afiliado():
    motor = MotorScoring()
    perfil = {
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
    }
    resultado = motor.calcular_scores(perfil)
    assert_true(resultado.top.nombre != "", "Top sin nombre")
    assert_true(resultado.top.score >= 0, "Score negativo inesperado")


def test_variable_faltante():
    motor = MotorScoring()
    perfil = perfil_base()
    perfil.pop("V11")
    try:
        motor.calcular_scores(perfil)
        raise AssertionError("Debió fallar por variable faltante")
    except ValueError as e:
        assert_true("Faltan variables" in str(e), "Mensaje inesperado para variable faltante")


def test_categoria_invalida():
    motor = MotorScoring()
    perfil = perfil_base()
    perfil["V2"] = "Mujer"
    try:
        motor.calcular_scores(perfil)
        raise AssertionError("Debió fallar por categoría inválida")
    except ValueError as e:
        assert_true("Categoría inválida" in str(e), "Mensaje inesperado para categoría inválida")


def generar_perfiles_extremos():
    categorias = {v["code"]: v["categorias"] for v in VARIABLES}
    extremos = []
    extremos.append({code: vals[0] for code, vals in categorias.items()})
    extremos.append({code: vals[-1] for code, vals in categorias.items()})
    extremos.append({
        "V1": "66+ años", "V2": "Femenino", "V3": "Formal independiente / profesional",
        "V4": "Alto (> $4.6M)", "V5": "Multigeneracional / adulto mayor a cargo",
        "V6": "Propia financiada (hipoteca)", "V7": "Sí", "V8": "Carro",
        "V9": "Sí", "V10": "Sí", "V11": "Sí",
    })
    extremos.append({
        "V1": "18-25 años", "V2": "Masculino", "V3": "Informal / cuenta propia sin cotización",
        "V4": "Bajo (< $1.3M)", "V5": "Soltero(a) sin hijos",
        "V6": "Arrendada", "V7": "No", "V8": "No tiene",
        "V9": "No", "V10": "No", "V11": "No",
    })
    return extremos


def test_perfiles_extremos():
    motor = MotorScoring()
    for i, perfil in enumerate(generar_perfiles_extremos(), start=1):
        resultado = motor.calcular_scores(perfil)
        assert_true(len(resultado.ranking) == len(motor.products), f"Caso extremo {i} sin ranking completo")
        assert_true(resultado.top is not None, f"Caso extremo {i} sin top")
        assert_true(resultado.ranking[0].score >= resultado.ranking[-1].score, f"Caso extremo {i} con ranking invertido")
        assert_true(all(r.nombre for r in resultado.ranking), f"Caso extremo {i} con producto vacío")


def test_producto_explicito():
    motor = MotorScoring()
    resultado = motor.calcular_scores(perfil_base(), producto_explicito="hogar")
    assert_true(resultado.ranking[0].key == "hogar", "No priorizó el producto explícito")
    assert_true(resultado.ranking[0].forced_explicit is True, "No marcó forced_explicit")


def main():
    pruebas = [
        ("Caso válido afiliado", test_caso_valido_afiliado),
        ("Caso válido no afiliado", test_caso_valido_no_afiliado),
        ("Variable faltante", test_variable_faltante),
        ("Categoría inválida", test_categoria_invalida),
        ("Perfiles extremos", test_perfiles_extremos),
        ("Producto explícito", test_producto_explicito),
    ]
    resultados = [run_case(nombre, fn) for nombre, fn in pruebas]
    total = len(resultados)
    ok = sum(resultados)
    print(f"Resultado final: {ok}/{total} pruebas OK")
    if ok != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
