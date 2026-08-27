"""Cálculo del piso de referencia por producto (patrón *Strategy*).

Problema que resuelve
---------------------
El ``pct`` de un producto no arranca en cero. Variables genéricas como edad o
ingreso reparten puntos a casi todos los productos, así que cada póliza tiene
un piso propio que no significa afinidad, sino ruido acumulado. Comparar el
``pct`` de dos productos distintos sin descontar ese piso es comparar peras con
manzanas.

Variables estructurales vs. condicionales
-----------------------------------------
Una variable es **estructural** si todas sus categorías tienen algún peso
distinto de cero: parte a la población en estados que siempre informan algo
(V1..V6). Es **condicional** si alguna categoría tiene el vector completamente
en cero (V7..V11): esa categoría es un "no aplica" y los pesos modelan un bono
sobre el piso, no una distribución.

El piso se calcula solo con las estructurales. Así, poseer un carro o una
mascota se lee como una ventaja real sobre el promedio en lugar de diluirse.

Fórmula
-------
Como el score es una suma de aportes independientes por variable, la esperanza
tiene forma cerrada y no requiere simular perfiles::

    E[score_p] = sum_v  sum_c  P(c) * peso[v|c][p]

Con distribución uniforme, ``P(c) = 1 / len(categorias)``. Esto es idéntico a
enumerar las 77.760 combinaciones posibles, pero en 33 operaciones.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from scoring_engine.models import Baseline, ProductDef, TriggerDef, VariableDef

#: Distribución por variable: ``{code: {categoria: probabilidad}}``.
Prior = Mapping[str, Mapping[str, float]]


def es_estructural(
    variable: VariableDef, weights: Mapping[str, tuple[int, ...]]
) -> bool:
    """Determina si una variable entra al cálculo del piso.

    Args:
        variable: Variable a clasificar.
        weights: Matriz de pesos completa.

    Returns:
        ``True`` si ninguna categoría tiene el vector de pesos en cero.
    """
    for categoria in variable.categorias:
        vector = weights.get(variable.clave(categoria))
        if vector is None or not any(vector):
            return False
    return True


class BaselineProvider(Protocol):
    """Contrato de una estrategia de cálculo de piso."""

    def calcular(
        self,
        products: tuple[ProductDef, ...],
        variables: tuple[VariableDef, ...],
        weights: Mapping[str, tuple[int, ...]],
        maxs: tuple[int, ...],
        triggers: tuple[TriggerDef, ...],
    ) -> dict[str, Baseline]:
        """Calcula el piso de cada producto.

        Args:
            products: Catálogo de productos, en orden de índice.
            variables: Variables del cuestionario.
            weights: Matriz de pesos.
            maxs: Score máximo teórico por producto.
            triggers: Disparadores declarados, para marcarlos en la salida.

        Returns:
            Un ``Baseline`` por ``product_key``.
        """
        ...


class _BaselineBase:
    """Implementación común: solo cambia de dónde salen las probabilidades."""

    def _probabilidades(self, variable: VariableDef) -> dict[str, float]:
        """Devuelve la distribución de categorías de una variable.

        Args:
            variable: Variable a distribuir.

        Returns:
            Mapa ``categoria -> probabilidad``, que suma 1.
        """
        raise NotImplementedError

    def calcular(
        self,
        products: tuple[ProductDef, ...],
        variables: tuple[VariableDef, ...],
        weights: Mapping[str, tuple[int, ...]],
        maxs: tuple[int, ...],
        triggers: tuple[TriggerDef, ...],
    ) -> dict[str, Baseline]:
        """Acumula la esperanza del score sobre las variables estructurales.

        Args:
            products: Catálogo de productos, en orden de índice.
            variables: Variables del cuestionario.
            weights: Matriz de pesos.
            maxs: Score máximo teórico por producto.
            triggers: Disparadores declarados, para marcarlos en la salida.

        Returns:
            Un ``Baseline`` por ``product_key``, con sus disparadores adjuntos.
        """
        esperado = [0.0] * len(products)

        for variable in variables:
            if not es_estructural(variable, weights):
                continue
            for categoria, probabilidad in self._probabilidades(variable).items():
                vector = weights[variable.clave(categoria)]
                for indice, peso in enumerate(vector):
                    esperado[indice] += peso * probabilidad

        por_producto: dict[str, tuple[TriggerDef, ...]] = {}
        for trigger in triggers:
            por_producto.setdefault(trigger.product_key, ())
            por_producto[trigger.product_key] += (trigger,)

        return {
            producto.key: Baseline(
                product_key=producto.key,
                expected_score=round(esperado[indice], 4),
                max_score=maxs[indice],
                expected_pct=round(esperado[indice] / maxs[indice] * 100, 2),
                triggers=por_producto.get(producto.key, ()),
            )
            for indice, producto in enumerate(products)
        }


class UniformBaseline(_BaselineBase):
    """Piso asumiendo que todas las categorías son igual de frecuentes.

    Es el default: no requiere datos y es reproducible. Sirve como referencia
    neutra mientras no haya una distribución poblacional validada.
    """

    def _probabilidades(self, variable: VariableDef) -> dict[str, float]:
        """Reparte probabilidad uniforme entre las categorías.

        Args:
            variable: Variable a distribuir.

        Returns:
            Mapa ``categoria -> 1/n``.
        """
        n = len(variable.categorias)
        return {categoria: 1.0 / n for categoria in variable.categorias}


class PopulationBaseline(_BaselineBase):
    """Piso ponderado por la distribución real de afiliados.

    Es la versión que debe usarse en producción una vez exista un censo
    confiable. Las variables sin distribución declarada caen a uniforme.
    """

    def __init__(self, prior: Prior) -> None:
        """Guarda la distribución poblacional.

        Args:
            prior: Mapa ``{code: {categoria: probabilidad}}``. No hace falta
                que cubra todas las variables ni que sume exactamente 1: se
                normaliza internamente.
        """
        self._prior = prior

    def _probabilidades(self, variable: VariableDef) -> dict[str, float]:
        """Usa la distribución declarada, o uniforme si la variable no está.

        Args:
            variable: Variable a distribuir.

        Returns:
            Mapa ``categoria -> probabilidad`` normalizado a 1.

        Raises:
            ValueError: Si la distribución declarada suma cero.
        """
        crudo = self._prior.get(variable.code)
        if not crudo:
            n = len(variable.categorias)
            return {categoria: 1.0 / n for categoria in variable.categorias}

        filtrado = {c: float(crudo.get(c, 0.0)) for c in variable.categorias}
        total = sum(filtrado.values())
        if total <= 0:
            raise ValueError(f"Distribución vacía para {variable.code}")
        return {c: v / total for c, v in filtrado.items()}
