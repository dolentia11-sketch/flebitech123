"""Motor de scoring: orquesta catálogo, piso, aritmética y ranking.

Entradas
--------
``MotorScoring.calcular(perfil, producto_explicito=None)``

* ``perfil``: ``dict[str, str]`` con las 11 claves ``V1``..``V11``. El valor de
  cada una debe ser **exactamente** una de las categorías declaradas en el
  catálogo. V1..V5 provienen del sistema de afiliados; V6..V11 del formulario.
* ``producto_explicito``: ``str | None``. Clave del producto que el cliente
  pidió por nombre. Si se entrega, ese producto se fuerza al puesto 1.

Salidas
-------
Un :class:`~scoring_engine.models.ResultadoScoring` con:

* ``ranking``: los 12 productos ordenados, cada uno con ``score``, ``pct``,
  ``baseline_pct``, ``lift``, ``modo_cierre``, ``triggered_by`` y ``rank``.
* ``aportes``: desglose por variable (pesos y justificación) para auditoría.
* ``top`` / ``top_3``: atajos de lectura.

Flujo de ejecución
------------------
::

    perfil
      |
      v
    [1] validar          -> faltantes y categorías inválidas -> ValueError
      |
      v
    [2] acumular         -> score[p] = suma de pesos de las 11 respuestas
      |
      v
    [3] normalizar       -> pct[p] = score[p] / MAXS[p] * 100
      |
      v
    [4] descontar piso   -> lift[p] = pct[p] - baseline_pct[p]
      |
      v
    [5] detectar triggers-> hechos declarados (mascota, carro, moto, ...)
      |
      v
    [6] ordenar          -> RankingStrategy (LiftRanking por defecto)
      |
      v
    [7] post-procesar    -> TriggerPromoter -> ExplicitProductPromoter
      |
      v
    [8] asignar rank     -> ResultadoScoring

Los pasos 1-5 son aritmética pura y determinista. Los pasos 6-7 son política de
negocio inyectable: se cambian por constructor sin tocar el cálculo.

El piso (``baseline_pct``) se calcula una sola vez al construir el motor, no
por cada perfil.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from functools import cached_property

from scoring_engine import catalog
from scoring_engine.baseline import BaselineProvider, UniformBaseline, es_estructural
from scoring_engine.models import (
    AporteVariable,
    Baseline,
    ChecklistDef,
    ProductDef,
    ResultadoProducto,
    ResultadoScoring,
    TriggerDef,
    VariableDef,
)
from scoring_engine.ranking import (
    ExplicitProductPromoter,
    LiftRanking,
    RankingPostProcessor,
    RankingStrategy,
    TriggerGate,
    TriggerPromoter,
)


class ScoringCatalog:
    """Acceso de solo lectura a los datos de negocio (*Repository*).

    Encapsula productos, variables, pesos y disparadores, y deriva de ellos el
    máximo teórico y la clasificación estructural/condicional. El motor nunca
    toca el módulo de datos directamente: así se puede sustituir esta clase por
    una que lea de Excel o de base de datos.
    """

    def __init__(
        self,
        products: Sequence[ProductDef] = catalog.PRODUCTS,
        variables: Sequence[VariableDef] = catalog.VARIABLES,
        weights: Mapping[str, tuple[int, ...]] = catalog.WEIGHTS,
        rationale: Mapping[str, str] = catalog.RATIONALE,
        checklist: Mapping[str, ChecklistDef] = catalog.CHECKLIST,
        triggers: Sequence[TriggerDef] = catalog.TRIGGERS,
    ) -> None:
        """Carga y valida el catálogo.

        Args:
            products: Catálogo de pólizas, en el orden que define los índices.
            variables: Preguntas del cuestionario.
            weights: Matriz de pesos.
            rationale: Justificación por fila de la matriz.
            checklist: Requisitos de cotización por producto.
            triggers: Disparadores duros declarados.

        Raises:
            ValueError: Si algún vector de pesos no tiene la longitud del
                catálogo de productos, o si un disparador referencia un
                producto, variable o categoría inexistente.
        """
        self.products = tuple(products)
        self.variables = tuple(variables)
        self.weights = dict(weights)
        self.rationale = dict(rationale)
        self.checklist = dict(checklist)
        self.triggers = tuple(triggers)
        self._indice_producto = {p.key: i for i, p in enumerate(self.products)}
        self._indice_variable = {v.code: v for v in self.variables}
        self._validar()

    def _validar(self) -> None:
        """Comprueba la coherencia interna del catálogo.

        Raises:
            ValueError: Si hay vectores de largo incorrecto o disparadores
                que apuntan a entidades inexistentes.
        """
        esperado = len(self.products)
        for clave, vector in self.weights.items():
            if len(vector) != esperado:
                raise ValueError(
                    f"El vector {clave!r} tiene {len(vector)} pesos; "
                    f"se esperaban {esperado}"
                )

        for trigger in self.triggers:
            if trigger.product_key not in self._indice_producto:
                raise ValueError(
                    f"Trigger a producto inexistente: {trigger.product_key}"
                )
            variable = self._indice_variable.get(trigger.code)
            if variable is None:
                raise ValueError(f"Trigger a variable inexistente: {trigger.code}")
            if trigger.categoria not in variable.categorias:
                raise ValueError(
                    f"Trigger a categoría inexistente: "
                    f"{trigger.code}|{trigger.categoria}"
                )

    @cached_property
    def maxs(self) -> tuple[int, ...]:
        """Score máximo teórico por producto.

        Se deriva de la matriz sumando, por variable, el peso más alto entre
        sus categorías. Es calculado y no declarado para que no pueda quedar
        desactualizado respecto de los pesos.

        Returns:
            Tupla de máximos, en orden de catálogo.
        """
        return tuple(
            sum(
                max(self.pesos(v.code, c)[i] for c in v.categorias)
                for v in self.variables
            )
            for i in range(len(self.products))
        )

    @cached_property
    def variables_estructurales(self) -> frozenset[str]:
        """Códigos de las variables que entran al cálculo del piso.

        Returns:
            Conjunto de códigos sin categoría "no aplica".
        """
        return frozenset(
            v.code for v in self.variables if es_estructural(v, self.weights)
        )

    def pesos(self, code: str, categoria: str) -> tuple[int, ...]:
        """Devuelve el vector de pesos de una respuesta.

        Args:
            code: Código de la variable.
            categoria: Respuesta del cliente.

        Returns:
            El vector declarado, o un vector de ceros si la combinación no
            está en la matriz.
        """
        return self.weights.get(f"{code}|{categoria}", (0,) * len(self.products))

    def indice(self, product_key: str) -> int:
        """Traduce una clave de producto a su índice en los vectores.

        Args:
            product_key: Identificador del producto.

        Returns:
            La posición del producto en el catálogo.

        Raises:
            KeyError: Si el producto no existe.
        """
        try:
            return self._indice_producto[product_key]
        except KeyError as exc:
            raise KeyError(f"Producto desconocido: {product_key}") from exc

    def variable(self, code: str) -> VariableDef:
        """Recupera la definición de una variable.

        Args:
            code: Código de la variable.

        Returns:
            La definición correspondiente.

        Raises:
            KeyError: Si la variable no existe.
        """
        try:
            return self._indice_variable[code]
        except KeyError as exc:
            raise KeyError(f"Variable desconocida: {code}") from exc

    def modo_cierre(self, product_key: str) -> str:
        """Indica si el producto cierra en autoservicio o requiere asesor.

        Args:
            product_key: Identificador del producto.

        Returns:
            ``"auto"`` o ``"asesoria"``. Por prudencia, un producto sin
            checklist documentado se marca como ``"asesoria"``.
        """
        ficha = self.checklist.get(product_key)
        return ficha.modo_cierre if ficha else "asesoria"


class MotorScoring:
    """Calcula y ordena recomendaciones de seguros para un perfil.

    El motor es inmutable y sin estado por perfil: puede compartirse entre
    peticiones concurrentes.
    """

    def __init__(
        self,
        catalogo: ScoringCatalog | None = None,
        baseline_provider: BaselineProvider | None = None,
        strategy: RankingStrategy | None = None,
        post_processors: Sequence[RankingPostProcessor] | None = None,
        top_n_triggers: int = 3,
    ) -> None:
        """Construye el motor y precalcula el piso de cada producto.

        Args:
            catalogo: Fuente de datos de negocio. Por defecto, el catálogo
                Colsubsidio embebido.
            baseline_provider: Estrategia de cálculo del piso. Por defecto,
                :class:`~scoring_engine.baseline.UniformBaseline`.
            strategy: Política de ordenamiento. Por defecto,
                :class:`~scoring_engine.ranking.LiftRanking`.
            post_processors: Reglas que ajustan el ranking, en orden de
                aplicación. Por defecto, bloqueo y promoción por disparador.
                Pasar ``()`` deja el orden crudo de la estrategia, útil para
                comparar políticas en los tests.
            top_n_triggers: Cuántas posiciones se reservan para productos con
                disparador activo. Se ignora si se pasa ``post_processors``.
        """
        self.catalogo = catalogo or ScoringCatalog()
        self.strategy = strategy or LiftRanking()
        self.post_processors: tuple[RankingPostProcessor, ...] = (
            tuple(post_processors)
            if post_processors is not None
            else (TriggerGate(), TriggerPromoter(top_n=top_n_triggers))
        )
        provider = baseline_provider or UniformBaseline()
        self.baselines: dict[str, Baseline] = provider.calcular(
            products=self.catalogo.products,
            variables=self.catalogo.variables,
            weights=self.catalogo.weights,
            maxs=self.catalogo.maxs,
            triggers=self.catalogo.triggers,
        )

    def validar_perfil(self, perfil: Mapping[str, str]) -> None:
        """Verifica que el perfil esté completo y con categorías válidas.

        Args:
            perfil: Respuestas del cliente.

        Raises:
            ValueError: Si falta alguna variable o si una respuesta no
                pertenece a las categorías declaradas.
        """
        faltantes = [v.code for v in self.catalogo.variables if v.code not in perfil]
        if faltantes:
            raise ValueError(f"Faltan variables en el perfil: {', '.join(faltantes)}")

        for variable in self.catalogo.variables:
            categoria = perfil[variable.code]
            if categoria not in variable.categorias:
                raise ValueError(
                    f"Categoría inválida para {variable.code}: {categoria!r}. "
                    f"Válidas: {', '.join(variable.categorias)}"
                )

    def _aportes(self, perfil: Mapping[str, str]) -> tuple[AporteVariable, ...]:
        """Construye el desglose auditable del perfil.

        Args:
            perfil: Respuestas ya validadas.

        Returns:
            Un aporte por variable, en orden de cuestionario.
        """
        estructurales = self.catalogo.variables_estructurales
        return tuple(
            AporteVariable(
                code=variable.code,
                label=variable.label,
                categoria=perfil[variable.code],
                estructural=variable.code in estructurales,
                pesos=self.catalogo.pesos(variable.code, perfil[variable.code]),
                rationale=self.catalogo.rationale.get(
                    variable.clave(perfil[variable.code]), ""
                ),
            )
            for variable in self.catalogo.variables
        )

    def _triggers_activos(
        self, perfil: Mapping[str, str]
    ) -> dict[str, tuple[TriggerDef, ...]]:
        """Detecta qué disparadores activó el perfil.

        Args:
            perfil: Respuestas ya validadas.

        Returns:
            Mapa ``product_key -> disparadores activados``.
        """
        activos: dict[str, tuple[TriggerDef, ...]] = {}
        for trigger in self.catalogo.triggers:
            if perfil.get(trigger.code) == trigger.categoria:
                activos.setdefault(trigger.product_key, ())
                activos[trigger.product_key] += (trigger,)
        return activos

    def _puntuar(
        self,
        aportes: Iterable[AporteVariable],
        triggers: Mapping[str, tuple[TriggerDef, ...]],
    ) -> tuple[ResultadoProducto, ...]:
        """Acumula pesos y arma un resultado por producto.

        Args:
            aportes: Desglose del perfil.
            triggers: Disparadores activados, por producto.

        Returns:
            Los 12 productos puntuados, en orden de catálogo.
        """
        totales = [0] * len(self.catalogo.products)
        for aporte in aportes:
            for indice, peso in enumerate(aporte.pesos):
                totales[indice] += peso

        resultados = []
        for indice, producto in enumerate(self.catalogo.products):
            maximo = self.catalogo.maxs[indice]
            score = totales[indice]
            pct = round(score / maximo * 100, 1) if maximo else 0.0
            baseline = self.baselines[producto.key]
            resultados.append(
                ResultadoProducto(
                    key=producto.key,
                    nombre=producto.nombre,
                    linea=producto.linea,
                    score=score,
                    max_score=maximo,
                    pct=pct,
                    baseline_pct=baseline.expected_pct,
                    lift=round(pct - baseline.expected_pct, 2),
                    modo_cierre=self.catalogo.modo_cierre(producto.key),
                    requiere_trigger=baseline.tiene_trigger,
                    triggered_by=triggers.get(producto.key, ()),
                )
            )
        return tuple(resultados)

    def _post_procesadores(
        self, producto_explicito: str | None
    ) -> tuple[RankingPostProcessor, ...]:
        """Arma la cadena de reglas que ajustan el ranking.

        El orden importa: primero se baja lo que exige un disparador que no se
        activó, luego suben los disparados, y de último se fuerza el producto
        pedido por el cliente, que debe quedar de primero.

        Args:
            producto_explicito: Producto solicitado, o ``None``.

        Returns:
            Los post-procesadores en orden de aplicación.
        """
        return (
            *self.post_processors,
            ExplicitProductPromoter(producto_explicito),
        )

    def calcular(
        self,
        perfil: Mapping[str, str],
        producto_explicito: str | None = None,
    ) -> ResultadoScoring:
        """Ejecuta el pipeline completo sobre un perfil.

        Args:
            perfil: Respuestas a las 11 variables del cuestionario.
            producto_explicito: Clave del producto que el cliente pidió por
                nombre, si lo hubo.

        Returns:
            El resultado con ranking ordenado y desglose auditable.

        Raises:
            ValueError: Si el perfil está incompleto o tiene categorías
                inválidas.
            KeyError: Si ``producto_explicito`` no existe en el catálogo.
        """
        self.validar_perfil(perfil)
        if producto_explicito:
            self.catalogo.indice(producto_explicito)

        aportes = self._aportes(perfil)
        triggers = self._triggers_activos(perfil)
        resultados = self._puntuar(aportes, triggers)

        ordenados = self.strategy.ordenar(resultados)
        for procesador in self._post_procesadores(producto_explicito):
            ordenados = procesador.aplicar(ordenados)

        return ResultadoScoring(
            perfil=dict(perfil),
            producto_explicito=producto_explicito,
            ranking=tuple(r.con_rank(i) for i, r in enumerate(ordenados, start=1)),
            aportes=aportes,
        )

    def influencia_variables(self) -> tuple[dict[str, object], ...]:
        """Mide cuánto puede mover el ranking cada variable.

        La influencia es la suma, sobre los productos, del rango
        ``max(peso) - min(peso)`` entre las categorías de la variable. Sirve
        para priorizar qué preguntas conservar si hay que acortar el
        formulario.

        Returns:
            Una entrada por variable, ordenada de mayor a menor influencia.
        """
        salida = []
        for variable in self.catalogo.variables:
            vectores = [
                self.catalogo.pesos(variable.code, c) for c in variable.categorias
            ]
            rangos = [
                max(v[i] for v in vectores) - min(v[i] for v in vectores)
                for i in range(len(self.catalogo.products))
            ]
            salida.append(
                {
                    "code": variable.code,
                    "label": variable.label,
                    "estructural": variable.code
                    in self.catalogo.variables_estructurales,
                    "influence": sum(rangos),
                    "por_producto": tuple(rangos),
                }
            )
        salida.sort(key=lambda x: x["influence"], reverse=True)
        return tuple(salida)

    def reglas_de_producto(self, product_key: str, n: int = 6) -> tuple[dict, ...]:
        """Explica qué perfil favorece a un producto.

        Para cada variable devuelve la categoría que más aporta a ese
        producto. Es la lectura inversa de la matriz: en lugar de "qué le
        recomiendo a este cliente", responde "a quién le sirve este seguro".

        Args:
            product_key: Producto a explicar.
            n: Cuántas variables devolver, de mayor a menor peso.

        Returns:
            Las ``n`` reglas más fuertes del producto.

        Raises:
            KeyError: Si el producto no existe.
        """
        indice = self.catalogo.indice(product_key)
        reglas = []
        for variable in self.catalogo.variables:
            mejor = max(
                variable.categorias,
                key=lambda c: self.catalogo.pesos(variable.code, c)[indice],
            )
            reglas.append(
                {
                    "code": variable.code,
                    "label": variable.label,
                    "categoria": mejor,
                    "peso": self.catalogo.pesos(variable.code, mejor)[indice],
                    "rationale": self.catalogo.rationale.get(variable.clave(mejor), ""),
                }
            )
        reglas.sort(key=lambda x: x["peso"], reverse=True)
        return tuple(reglas[:n])
