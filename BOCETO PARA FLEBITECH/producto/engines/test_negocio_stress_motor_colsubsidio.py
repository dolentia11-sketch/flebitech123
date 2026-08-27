# -*- coding: utf-8 -*-
"""Tests de negocio + 100 pruebas aleatorias para motor-colsubsidio.py"""

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


def rank_of(resultado, product_key):
    for r in resultado.ranking:
        if r.key == product_key:
            return r.rank, r
    raise AssertionError(f"No se encontró el producto {product_key}")


def test_caso_valido_afiliado():
    motor = MotorScoring()
    resultado = motor.calcular_scores(perfil_base())
    assert_true(len(resultado.ranking) == len(motor.products), "El ranking no contiene todos los productos")
    assert_true(resultado.top is not None, "No hay top producto")



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



def test_regla_autos_top3_si_carro_ingreso_alto():
    motor = MotorScoring()
    perfil = {
        "V1": "36-45 años",
        "V2": "Masculino",
        "V3": "Formal independiente / profesional",
        "V4": "Alto (> $4.6M)",
        "V5": "Pareja sin hijos",
        "V6": "Propia financiada (hipoteca)",
        "V7": "No",
        "V8": "Carro",
        "V9": "No",
        "V10": "No",
        "V11": "No",
    }
    resultado = motor.calcular_scores(perfil)
    rank, _ = rank_of(resultado, "autos")
    assert_true(rank <= 3, f"Autos debería quedar en top 3 y quedó en #{rank}")



def test_regla_mascotas_no_irrelevante_si_tiene_mascota():
    motor = MotorScoring()
    perfil = {
        "V1": "26-35 años",
        "V2": "Femenino",
        "V3": "Formal dependiente",
        "V4": "Medio ($1.3M - $4.6M)",
        "V5": "Pareja sin hijos",
        "V6": "Arrendada",
        "V7": "No",
        "V8": "No tiene",
        "V9": "Sí",
        "V10": "No",
        "V11": "No",
    }
    resultado = motor.calcular_scores(perfil)
    rank, prod = rank_of(resultado, "mascotas")
    assert_true(rank <= 5, f"Mascotas no debería ser irrelevante y quedó en #{rank}")
    assert_true(prod.score > 0, "Mascotas debería tener score positivo")



def test_regla_arrendamiento_top5_si_es_arrendador():
    motor = MotorScoring()
    perfil = {
        "V1": "36-45 años",
        "V2": "Masculino",
        "V3": "Formal independiente / profesional",
        "V4": "Alto (> $4.6M)",
        "V5": "Pareja sin hijos",
        "V6": "Propia pagada",
        "V7": "Sí",
        "V8": "Carro",
        "V9": "No",
        "V10": "No",
        "V11": "No",
    }
    resultado = motor.calcular_scores(perfil)
    rank, prod = rank_of(resultado, "arrendamiento")
    assert_true(rank <= 5, f"Arrendamiento debería quedar visible y quedó en #{rank}")
    assert_true(prod.score > 0, "Arrendamiento debería tener score positivo")



def test_regla_bicicletas_visible_si_usa_bici():
    motor = MotorScoring()
    perfil = {
        "V1": "18-25 años",
        "V2": "Masculino",
        "V3": "Informal / cuenta propia sin cotización",
        "V4": "Medio ($1.3M - $4.6M)",
        "V5": "Soltero(a) sin hijos",
        "V6": "Arrendada",
        "V7": "No",
        "V8": "No tiene",
        "V9": "No",
        "V10": "Sí",
        "V11": "No",
    }
    resultado = motor.calcular_scores(perfil)
    rank, prod = rank_of(resultado, "bicicletas")
    assert_true(rank <= 5, f"Bicicletas debería quedar visible y quedó en #{rank}")
    assert_true(prod.score > 0, "Bicicletas debería tener score positivo")



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



def test_100_perfiles_aleatorios():
    rng = random.Random(RANDOM_SEED)
    motor = MotorScoring()
    for i in range(1, TOTAL_PERFILES + 1):
        perfil = {v["code"]: rng.choice(v["categorias"]) for v in VARIABLES}
        resultado = motor.calcular_scores(perfil)
        assert_true(len(resultado.ranking) == len(motor.products), f"Caso aleatorio {i} con ranking incompleto")
        assert_true(resultado.top is not None, f"Caso aleatorio {i} sin top")
        assert_true(all(r.nombre for r in resultado.ranking), f"Caso aleatorio {i} con producto vacío")
        assert_true(
            all(resultado.ranking[j].score >= resultado.ranking[j + 1].score for j in range(len(resultado.ranking) - 1)),
            f"Caso aleatorio {i} con ranking desordenado",
        )



def main():
    pruebas = [
        ("Caso válido afiliado", test_caso_valido_afiliado),
        ("Caso válido no afiliado", test_caso_valido_no_afiliado),
        ("Variable faltante", test_variable_faltante),
        ("Categoría inválida", test_categoria_invalida),
        ("Regla negocio autos top 3", test_regla_autos_top3_si_carro_ingreso_alto),
        ("Regla negocio mascotas visible", test_regla_mascotas_no_irrelevante_si_tiene_mascota),
        ("Regla negocio arrendamiento visible", test_regla_arrendamiento_top5_si_es_arrendador),
        ("Regla negocio bicicletas visible", test_regla_bicicletas_visible_si_usa_bici),
        ("Perfiles extremos", test_perfiles_extremos),
        ("Producto explícito", test_producto_explicito),
        ("100 perfiles aleatorios", test_100_perfiles_aleatorios),
    ]
    resultados = [run_case(nombre, fn) for nombre, fn in pruebas]
    total = len(resultados)
    ok = sum(resultados)
    print(f"Resultado final: {ok}/{total} pruebas OK")
    if ok != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
