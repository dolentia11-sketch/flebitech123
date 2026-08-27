"""Ordenamiento del ranking (*Strategy*) y ajustes posteriores (*Chain*).

El motor calcula scores; este módulo decide cómo se ordenan y qué reglas de
negocio pueden alterar ese orden. Separarlos permite cambiar la política de
ranking sin tocar la aritmética, y probar cada regla en aislamiento.

Pipeline
--------
1. Una :class:`RankingStrategy` ordena los 12 productos.
2. Cada :class:`RankingPostProcessor` reordena en cadena, en el orden en que
   fueron registrados.
3. El motor asigna ``rank`` al resultado final.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from scoring_engine.models import ResultadoProducto


class RankingStrategy(Protocol):
    """Contrato de una política de ordenamiento."""

    def ordenar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Ordena los productos de mejor a peor.

        Args:
            resultados: Productos ya puntuados, en orden de catálogo.

        Returns:
            Los mismos productos, reordenados.
        """
        ...


class LiftRanking:
    """Ordena por ``lift`` (default).

    Responde "¿este cliente encaja más que el cliente promedio?". Corrige a la
    vez el techo desigual (vía ``pct``) y el piso desigual (vía ``baseline``).
    """

    def ordenar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Ordena por lift descendente, desempatando por ``pct`` y ``score``.

        Args:
            resultados: Productos ya puntuados.

        Returns:
            Los productos ordenados por lift.
        """
        return tuple(
            sorted(resultados, key=lambda r: (r.lift, r.pct, r.score), reverse=True)
        )


class PctRanking:
    """Ordena por ``pct``. Corrige el techo desigual pero no el piso.

    Se conserva para comparar contra :class:`LiftRanking` en los tests y en
    análisis de regresión.
    """

    def ordenar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Ordena por porcentaje de afinidad descendente.

        Args:
            resultados: Productos ya puntuados.

        Returns:
            Los productos ordenados por ``pct``.
        """
        return tuple(sorted(resultados, key=lambda r: (r.pct, r.score), reverse=True))


class ScoreRanking:
    """Ordena por score crudo. Es el comportamiento del motor original.

    Sesga hacia productos con máximo teórico alto. Solo se mantiene para
    demostrar la regresión en los tests.
    """

    def ordenar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Ordena por puntos crudos descendente.

        Args:
            resultados: Productos ya puntuados.

        Returns:
            Los productos ordenados por ``score``.
        """
        return tuple(sorted(resultados, key=lambda r: (r.score, r.pct), reverse=True))


class RankingPostProcessor(Protocol):
    """Contrato de una regla que puede reordenar el ranking ya ordenado."""

    def aplicar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Reordena aplicando una regla de negocio.

        Args:
            resultados: Ranking producido por la etapa anterior.

        Returns:
            El ranking ajustado.
        """
        ...


class TriggerGate:
    """Baja los productos que exigen un disparador que no se activó.

    Es la mitad simétrica de :class:`TriggerPromoter`. Sin ella, Arrendamiento
    puede quedar alto por peso demográfico aunque el cliente haya respondido
    que no arrienda ningún inmueble: el lift sería real pero el producto,
    irrelevante. La regla de negocio es que un seguro sobre un objeto solo
    compite si el cliente declaró tener ese objeto.

    No elimina el producto: lo manda al final conservando su orden relativo,
    para que siga siendo visible y auditable.
    """

    def aplicar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Separa los productos bloqueados y los envía al final.

        Args:
            resultados: Ranking producido por la etapa anterior.

        Returns:
            El ranking con los bloqueados relegados.
        """
        elegibles = [r for r in resultados if not r.bloqueado]
        bloqueados = [r for r in resultados if r.bloqueado]
        return tuple(elegibles + bloqueados)


class TriggerPromoter:
    """Sube al top-N los productos cuyo disparador se activó.

    Un disparador es un hecho verificable ("tiene mascota"), no una
    propensión. Un score continuo lo diluye entre once sumandos, así que la
    promoción se resuelve fuera de la aritmética.
    """

    def __init__(self, top_n: int = 3) -> None:
        """Fija cuántas posiciones se reservan para disparadores.

        Args:
            top_n: Tamaño de la ventana de promoción.

        Raises:
            ValueError: Si ``top_n`` es menor que 1.
        """
        if top_n < 1:
            raise ValueError("top_n debe ser >= 1")
        self._top_n = top_n

    def aplicar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Mueve los productos disparados dentro de la ventana top-N.

        Los disparados conservan entre sí el orden que traían; el resto se
        desplaza hacia abajo sin alterar su orden relativo.

        Args:
            resultados: Ranking producido por la etapa anterior.

        Returns:
            El ranking con los disparados adelante.
        """
        disparados = [r for r in resultados if r.triggered_by]
        if not disparados:
            return resultados

        promovidos = disparados[: self._top_n]
        claves = {r.key for r in promovidos}
        resto = [r for r in resultados if r.key not in claves]
        return tuple(promovidos + resto)


class ExplicitProductPromoter:
    """Fuerza al primer puesto el producto que el cliente pidió por nombre.

    La intención declarada gana sobre cualquier inferencia del modelo.
    """

    def __init__(self, product_key: str | None) -> None:
        """Registra el producto solicitado.

        Args:
            product_key: Identificador del producto, o ``None`` si el cliente
                no pidió ninguno en particular.
        """
        self._product_key = product_key

    def aplicar(
        self, resultados: tuple[ResultadoProducto, ...]
    ) -> tuple[ResultadoProducto, ...]:
        """Mueve el producto solicitado a la posición 1 y lo marca.

        Args:
            resultados: Ranking producido por la etapa anterior.

        Returns:
            El ranking con el producto solicitado al frente. Si no se pidió
            ninguno o no existe, devuelve la entrada sin cambios.
        """
        if not self._product_key:
            return resultados

        elegido = next((r for r in resultados if r.key == self._product_key), None)
        if elegido is None:
            return resultados

        marcado = replace(elegido, forced_explicit=True)
        resto = [r for r in resultados if r.key != self._product_key]
        return (marcado, *resto)
