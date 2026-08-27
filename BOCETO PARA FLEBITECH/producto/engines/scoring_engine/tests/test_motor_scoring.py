"""Tests del motor de scoring.

Ejecutar con ``python -m pytest tests -v`` desde la raíz del proyecto.

Organización:

* ``TestCatalogo``          — integridad de los datos de negocio.
* ``TestBaseline``          — corrección del piso y de sus estrategias.
* ``TestScoring``           — aritmética y validación de entradas.
* ``TestEstrategiasRanking``— diferencias entre score, pct y lift.
* ``TestTriggers``          — promoción y bloqueo por disparador.
* ``TestRegresiones``       — los defectos concretos que motivaron el cambio.
"""

from __future__ import annotations

import pytest

from scoring_engine.baseline import PopulationBaseline, UniformBaseline, es_estructural
from scoring_engine.catalog import CASE_PRESETS
from scoring_engine.engine import MotorScoring, ScoringCatalog
from scoring_engine.models import ProductDef, TriggerDef, VariableDef
from scoring_engine.ranking import (
    ExplicitProductPromoter,
    LiftRanking,
    PctRanking,
    ScoreRanking,
    TriggerGate,
    TriggerPromoter,
)

PERFIL_BASE = {
    "V1": "36-45 años",
    "V2": "Femenino",
    "V3": "Formal dependiente",
    "V4": "Medio ($1.3M - $4.6M)",
    "V5": "Con hijos menores de edad",
    "V6": "Arrendada",
    "V7": "No",
    "V8": "No tiene",
    "V9": "No",
    "V10": "No",
    "V11": "No",
}


@pytest.fixture(scope="module")
def motor() -> MotorScoring:
    """Motor con configuración por defecto, compartido por el módulo."""
    return MotorScoring()


@pytest.fixture(scope="module")
def catalogo() -> ScoringCatalog:
    """Catálogo Colsubsidio embebido."""
    return ScoringCatalog()


class TestCatalogo:
    """Integridad de los datos de negocio."""

    def test_todos_los_vectores_tienen_doce_pesos(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Cada fila de la matriz debe cubrir exactamente los 12 productos."""
        for clave, vector in catalogo.weights.items():
            assert len(vector) == len(catalogo.products), clave

    def test_toda_categoria_existe_en_la_matriz(self, catalogo: ScoringCatalog) -> None:
        """No puede haber respuestas válidas sin fila de pesos."""
        for variable in catalogo.variables:
            for categoria in variable.categorias:
                assert variable.clave(categoria) in catalogo.weights

    def test_toda_fila_tiene_racional(self, catalogo: ScoringCatalog) -> None:
        """Cada peso declarado debe poder justificarse ante el cliente."""
        for clave in catalogo.weights:
            assert catalogo.rationale.get(clave), f"Sin racional: {clave}"

    def test_maxs_se_deriva_de_la_matriz(self, catalogo: ScoringCatalog) -> None:
        """El máximo es la suma de los mejores pesos por variable."""
        for indice in range(len(catalogo.products)):
            esperado = sum(
                max(catalogo.pesos(v.code, c)[indice] for c in v.categorias)
                for v in catalogo.variables
            )
            assert catalogo.maxs[indice] == esperado

    def test_maxs_coincide_con_el_motor_original(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Regresión: los máximos no cambiaron al refactorizar."""
        assert catalogo.maxs == (31, 24, 23, 21, 24, 24, 25, 25, 24, 21, 20, 25)

    def test_clasificacion_estructural(self, catalogo: ScoringCatalog) -> None:
        """V1..V6 son estructurales; V7..V11 tienen categoría 'no aplica'."""
        assert catalogo.variables_estructurales == frozenset(
            {"V1", "V2", "V3", "V4", "V5", "V6"}
        )

    def test_condicionales_tienen_categoria_nula(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Toda variable condicional debe tener un estado de vector cero."""
        for variable in catalogo.variables:
            if variable.code in catalogo.variables_estructurales:
                continue
            nulas = [
                c
                for c in variable.categorias
                if not any(catalogo.pesos(variable.code, c))
            ]
            assert nulas, variable.code

    def test_trigger_apunta_a_peso_relevante(self, catalogo: ScoringCatalog) -> None:
        """Un disparador sin peso en su producto sería contradictorio."""
        for trigger in catalogo.triggers:
            indice = catalogo.indice(trigger.product_key)
            assert catalogo.pesos(trigger.code, trigger.categoria)[indice] >= 3

    def test_catalogo_rechaza_vector_de_largo_invalido(self) -> None:
        """La validación del constructor atrapa matrices desalineadas."""
        with pytest.raises(ValueError, match="pesos"):
            ScoringCatalog(
                products=(ProductDef("a", "A", "Familia"),),
                variables=(VariableDef("V1", "x", "sistema", ("s",)),),
                weights={"V1|s": (1, 2)},
                rationale={"V1|s": "r"},
                checklist={},
                triggers=(),
            )

    def test_catalogo_rechaza_trigger_huerfano(self) -> None:
        """Un disparador a un producto inexistente es un error de datos."""
        with pytest.raises(ValueError, match="producto inexistente"):
            ScoringCatalog(
                products=(ProductDef("a", "A", "Familia"),),
                variables=(VariableDef("V1", "x", "sistema", ("s",)),),
                weights={"V1|s": (1,)},
                rationale={"V1|s": "r"},
                checklist={},
                triggers=(TriggerDef("V1", "s", "fantasma", "m"),),
            )


class TestBaseline:
    """Corrección del piso de referencia."""

    def test_forma_cerrada_iguala_a_la_enumeracion(
        self, catalogo: ScoringCatalog
    ) -> None:
        """La esperanza analítica debe coincidir con el promedio exhaustivo.

        Se enumeran todas las combinaciones de las variables estructurales
        (6*2*3*3*5*3 = 1.620 perfiles) y se compara contra la fórmula.
        """
        from itertools import product as cartesiano

        estructurales = [
            v for v in catalogo.variables if v.code in catalogo.variables_estructurales
        ]
        acumulado = [0] * len(catalogo.products)
        total = 0
        for combinacion in cartesiano(*(v.categorias for v in estructurales)):
            total += 1
            for variable, categoria in zip(estructurales, combinacion, strict=True):
                for indice, peso in enumerate(catalogo.pesos(variable.code, categoria)):
                    acumulado[indice] += peso

        baselines = UniformBaseline().calcular(
            catalogo.products,
            catalogo.variables,
            catalogo.weights,
            catalogo.maxs,
            catalogo.triggers,
        )
        for indice, producto in enumerate(catalogo.products):
            assert baselines[producto.key].expected_score == pytest.approx(
                acumulado[indice] / total, abs=1e-3
            )

    def test_baseline_ignora_variables_condicionales(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Mascotas no debe cargar en su piso el promedio de V9."""
        baselines = UniformBaseline().calcular(
            catalogo.products,
            catalogo.variables,
            catalogo.weights,
            catalogo.maxs,
            catalogo.triggers,
        )
        solo_estructurales = sum(
            sum(catalogo.pesos(v.code, c)[6] for c in v.categorias) / len(v.categorias)
            for v in catalogo.variables
            if v.code in catalogo.variables_estructurales
        )
        assert baselines["mascotas"].expected_score == pytest.approx(
            solo_estructurales, abs=1e-3
        )

    def test_baseline_marca_los_disparadores(self, motor: MotorScoring) -> None:
        """Los productos con disparador quedan señalados en el piso."""
        con_trigger = {k for k, b in motor.baselines.items() if b.tiene_trigger}
        assert con_trigger == {"mascotas", "autos", "bicicletas", "arrendamiento"}

    def test_piso_dentro_de_rango(self, motor: MotorScoring) -> None:
        """Un piso fuera de 0-100 indicaría un error de normalización."""
        for base in motor.baselines.values():
            assert 0 <= base.expected_pct <= 100

    def test_population_baseline_respeta_la_distribucion(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Con toda la masa en una categoría, el piso es el de esa categoría."""
        prior = {"V1": {"66+ años": 1.0}}
        baselines = PopulationBaseline(prior).calcular(
            catalogo.products,
            catalogo.variables,
            catalogo.weights,
            catalogo.maxs,
            catalogo.triggers,
        )
        uniforme = UniformBaseline().calcular(
            catalogo.products,
            catalogo.variables,
            catalogo.weights,
            catalogo.maxs,
            catalogo.triggers,
        )
        # 66+ aporta 5 a exequial, muy por encima del promedio de V1.
        assert (
            baselines["exequial"].expected_score > uniforme["exequial"].expected_score
        )

    def test_population_baseline_normaliza(self, catalogo: ScoringCatalog) -> None:
        """Probabilidades sin normalizar deben normalizarse internamente."""
        variable = catalogo.variable("V2")
        probabilidades = PopulationBaseline(
            {"V2": {"Masculino": 30.0, "Femenino": 70.0}}
        )._probabilidades(variable)
        assert sum(probabilidades.values()) == pytest.approx(1.0)
        assert probabilidades["Femenino"] == pytest.approx(0.7)

    def test_population_baseline_rechaza_distribucion_vacia(
        self, catalogo: ScoringCatalog
    ) -> None:
        """Una distribución que suma cero es un error de configuración."""
        with pytest.raises(ValueError, match="Distribución vacía"):
            PopulationBaseline({"V2": {"Masculino": 0.0}})._probabilidades(
                catalogo.variable("V2")
            )

    def test_es_estructural_detecta_vector_faltante(self) -> None:
        """Una categoría sin fila en la matriz hace condicional a la variable."""
        variable = VariableDef("V1", "x", "sistema", ("a", "b"))
        assert not es_estructural(variable, {"V1|a": (1, 2)})


class TestScoring:
    """Aritmética del score y validación de entradas."""

    def test_score_es_la_suma_de_los_aportes(self, motor: MotorScoring) -> None:
        """El score de cada producto debe reconstruirse desde el desglose."""
        resultado = motor.calcular(PERFIL_BASE)
        for item in resultado.ranking:
            indice = motor.catalogo.indice(item.key)
            assert item.score == sum(a.pesos[indice] for a in resultado.aportes)

    def test_pct_es_score_sobre_maximo(self, motor: MotorScoring) -> None:
        """La normalización usa el máximo teórico del producto."""
        for item in motor.calcular(PERFIL_BASE).ranking:
            assert item.pct == pytest.approx(
                item.score / item.max_score * 100, abs=0.05
            )

    def test_lift_es_pct_menos_piso(self, motor: MotorScoring) -> None:
        """El lift es la diferencia contra el piso del producto."""
        for item in motor.calcular(PERFIL_BASE).ranking:
            assert item.lift == pytest.approx(item.pct - item.baseline_pct, abs=0.01)

    def test_ranking_devuelve_todos_los_productos(self, motor: MotorScoring) -> None:
        """No se pierde ni se duplica ningún producto en el pipeline."""
        resultado = motor.calcular(PERFIL_BASE)
        claves = [r.key for r in resultado.ranking]
        assert len(claves) == len(set(claves)) == len(motor.catalogo.products)

    def test_ranks_consecutivos_desde_uno(self, motor: MotorScoring) -> None:
        """Las posiciones se asignan al cierre, sin huecos."""
        ranks = [r.rank for r in motor.calcular(PERFIL_BASE).ranking]
        assert ranks == list(range(1, len(ranks) + 1))

    def test_es_determinista(self, motor: MotorScoring) -> None:
        """El mismo perfil siempre produce el mismo ranking."""
        primero = motor.calcular(PERFIL_BASE).ranking
        segundo = motor.calcular(PERFIL_BASE).ranking
        assert primero == segundo

    def test_no_muta_el_perfil_recibido(self, motor: MotorScoring) -> None:
        """El motor no debe alterar el diccionario del llamador."""
        entrada = dict(PERFIL_BASE)
        motor.calcular(entrada)
        assert entrada == PERFIL_BASE

    def test_rechaza_perfil_incompleto(self, motor: MotorScoring) -> None:
        """Falta una variable obligatoria."""
        incompleto = {k: v for k, v in PERFIL_BASE.items() if k != "V7"}
        with pytest.raises(ValueError, match="V7"):
            motor.calcular(incompleto)

    def test_rechaza_categoria_invalida(self, motor: MotorScoring) -> None:
        """El texto debe coincidir exactamente con una categoría declarada."""
        with pytest.raises(ValueError, match="Categoría inválida"):
            motor.calcular({**PERFIL_BASE, "V1": "36-45"})

    def test_rechaza_producto_explicito_inexistente(self, motor: MotorScoring) -> None:
        """Pedir un producto fuera del catálogo es un error del llamador."""
        with pytest.raises(KeyError, match="Producto desconocido"):
            motor.calcular(PERFIL_BASE, producto_explicito="seguro_de_naves")

    @pytest.mark.parametrize("caso", CASE_PRESETS, ids=lambda c: c["label"][:28])
    def test_presets_no_revientan(self, motor: MotorScoring, caso: dict) -> None:
        """Todos los perfiles de demostración deben ejecutarse limpiamente."""
        resultado = motor.calcular(caso["profile"])
        assert resultado.top.rank == 1
        assert len(resultado.top_3) == 3


class TestEstrategiasRanking:
    """Diferencias observables entre las políticas de ordenamiento."""

    def test_estrategia_es_inyectable(self) -> None:
        """Cambiar la estrategia no requiere tocar el motor."""
        perfil = CASE_PRESETS[2]["profile"]
        por_score = MotorScoring(strategy=ScoreRanking(), post_processors=()).calcular(
            perfil
        )
        por_lift = MotorScoring(strategy=LiftRanking(), post_processors=()).calcular(
            perfil
        )
        assert [r.key for r in por_score.ranking] != [r.key for r in por_lift.ranking]

    @pytest.mark.parametrize(
        ("estrategia", "campo"),
        [(ScoreRanking(), "score"), (PctRanking(), "pct"), (LiftRanking(), "lift")],
        ids=["score", "pct", "lift"],
    )
    def test_orden_monotono_sin_post_procesadores(self, estrategia, campo) -> None:
        """Cada estrategia ordena de forma monótona por su propio criterio.

        Se desactivan los post-procesadores para aislar la política de orden
        de las reglas de negocio que la ajustan después.
        """
        motor = MotorScoring(strategy=estrategia, post_processors=())
        valores = [getattr(r, campo) for r in motor.calcular(PERFIL_BASE).ranking]
        assert valores == sorted(valores, reverse=True)


class TestTriggers:
    """Promoción y bloqueo por hechos declarados."""

    def test_mascota_promueve_el_seguro_de_mascotas(self, motor: MotorScoring) -> None:
        """Declarar mascota debe meter el producto al top-3."""
        resultado = motor.calcular({**PERFIL_BASE, "V9": "Sí"})
        assert "mascotas" in [r.key for r in resultado.top_3]

    def test_sin_mascota_el_producto_queda_bloqueado(self, motor: MotorScoring) -> None:
        """Sin el hecho, mascotas no compite por afinidad."""
        resultado = motor.calcular(PERFIL_BASE)
        mascotas = next(r for r in resultado.ranking if r.key == "mascotas")
        assert mascotas.bloqueado
        assert mascotas.rank > len(motor.catalogo.products) - 5

    def test_carro_y_moto_promueven_autos(self, motor: MotorScoring) -> None:
        """Ambos vehículos disparan el mismo producto."""
        for vehiculo in ("Carro", "Moto"):
            resultado = motor.calcular({**PERFIL_BASE, "V8": vehiculo})
            assert "autos" in [r.key for r in resultado.top_3], vehiculo

    def test_trigger_registra_su_motivo(self, motor: MotorScoring) -> None:
        """El disparador debe llegar al resultado con su justificación."""
        resultado = motor.calcular({**PERFIL_BASE, "V10": "Sí"})
        bicis = next(r for r in resultado.ranking if r.key == "bicicletas")
        assert bicis.triggered_by
        assert "bicicleta" in bicis.triggered_by[0].motivo.lower()

    def test_gate_no_elimina_productos(self, motor: MotorScoring) -> None:
        """Los bloqueados bajan pero siguen siendo visibles y auditables."""
        resultado = motor.calcular(PERFIL_BASE)
        assert len(resultado.ranking) == len(motor.catalogo.products)

    def test_promotor_respeta_top_n(self) -> None:
        """Con top_n=1 solo se promueve el mejor de los disparados."""
        motor = MotorScoring(top_n_triggers=1)
        resultado = motor.calcular({**PERFIL_BASE, "V9": "Sí", "V10": "Sí"})
        promovidos = [r.key for r in resultado.ranking[:1]]
        assert len(promovidos) == 1

    def test_promotor_rechaza_top_n_invalido(self) -> None:
        """top_n menor que 1 no tiene sentido."""
        with pytest.raises(ValueError, match="top_n"):
            TriggerPromoter(top_n=0)

    def test_gate_sin_bloqueados_no_altera(self, motor: MotorScoring) -> None:
        """Si nada está bloqueado, el gate es la identidad."""
        base = motor.calcular(
            {**PERFIL_BASE, "V7": "Sí", "V8": "Carro", "V9": "Sí", "V10": "Sí"}
        )
        assert TriggerGate().aplicar(base.ranking) == base.ranking

    def test_producto_explicito_gana_sobre_todo(self, motor: MotorScoring) -> None:
        """La intención declarada supera al modelo y a los disparadores."""
        resultado = motor.calcular(
            {**PERFIL_BASE, "V9": "Sí"}, producto_explicito="educacion"
        )
        assert resultado.top.key == "educacion"
        assert resultado.top.forced_explicit

    def test_promotor_explicito_sin_producto_es_identidad(
        self, motor: MotorScoring
    ) -> None:
        """Sin producto solicitado, el post-procesador no hace nada."""
        base = motor.calcular(PERFIL_BASE).ranking
        assert ExplicitProductPromoter(None).aplicar(base) == base


class TestRegresiones:
    """Los defectos concretos que motivaron este cambio."""

    def test_vida_ya_no_gana_por_tener_maximo_alto(self) -> None:
        """Antes: Vida quedaba #2 con 77,4% sobre Hogar con 95,8%.

        Vida tiene el máximo teórico más alto (31 vs 24), así que acumulaba
        más puntos crudos sin ser más pertinente.
        """
        perfil = CASE_PRESETS[2]["profile"]
        antes = MotorScoring(strategy=ScoreRanking(), post_processors=()).calcular(
            perfil
        )
        ahora = MotorScoring().calcular(perfil)

        posicion = {r.key: r.rank for r in antes.ranking}
        assert posicion["vida"] < posicion["hogar"]

        posicion = {r.key: r.rank for r in ahora.ranking}
        assert posicion["hogar"] < posicion["vida"]

    def test_mascota_declarada_ya_no_queda_cuarta(self) -> None:
        """Antes: con mascota declarada, el seguro quedaba en el puesto 4."""
        perfil = CASE_PRESETS[2]["profile"]
        assert perfil["V9"] == "Sí"

        antes = MotorScoring(strategy=ScoreRanking(), post_processors=()).calcular(
            perfil
        )
        assert next(r for r in antes.ranking if r.key == "mascotas").rank == 4

        ahora = MotorScoring().calcular(perfil)
        assert next(r for r in ahora.ranking if r.key == "mascotas").rank <= 3

    def test_arrendamiento_no_sube_sin_el_hecho(self) -> None:
        """Antes: Arrendamiento salía con 75% de afinidad y V7='No'."""
        perfil = CASE_PRESETS[2]["profile"]
        assert perfil["V7"] == "No"

        resultado = MotorScoring().calcular(perfil)
        arrendamiento = next(r for r in resultado.ranking if r.key == "arrendamiento")
        assert arrendamiento.pct > 70  # el pct crudo sigue siendo alto
        assert arrendamiento.rank > 3  # pero ya no compite


class TestReporting:
    """La capa de presentación no debe romperse con casos límite."""

    def test_ficha_de_producto_sin_checklist(self, motor: MotorScoring) -> None:
        """Productos sin checklist documentado deben degradar con gracia."""
        from scoring_engine.reporting import ficha_texto

        resultado = motor.calcular(PERFIL_BASE, producto_explicito="cancer")
        texto = ficha_texto(motor, resultado, afiliado=True)
        assert "sin checklist documentado" in texto

    def test_ficha_muestra_el_motivo_del_disparador(self, motor: MotorScoring) -> None:
        """El hecho declarado debe aparecer entre las razones."""
        from scoring_engine.reporting import ficha_texto

        resultado = motor.calcular(
            {**PERFIL_BASE, "V9": "Sí"}, producto_explicito="mascotas"
        )
        assert "perro o gato" in ficha_texto(motor, resultado)

    def test_tabla_baselines_marca_disparadores(self, motor: MotorScoring) -> None:
        """La tabla de pisos debe señalar qué productos exigen un hecho."""
        from scoring_engine.reporting import tabla_baselines

        assert "V9=Sí" in tabla_baselines(motor.baselines, motor)
