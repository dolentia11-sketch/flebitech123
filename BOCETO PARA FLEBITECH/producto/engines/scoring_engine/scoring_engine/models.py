"""Objetos de valor del dominio.

Todos son ``dataclass`` congelados (inmutables). El motor nunca muta un
resultado: cada etapa del pipeline produce objetos nuevos. Eso hace que el
orden de las etapas sea explícito y que los tests puedan comparar por igualdad.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

Origen = Literal["sistema", "formulario"]
ModoCierre = Literal["auto", "asesoria"]


@dataclass(frozen=True, slots=True)
class ProductDef:
    """Una póliza del catálogo.

    Args:
        key: Identificador estable usado en diccionarios y APIs.
        nombre: Nombre comercial mostrado al cliente.
        linea: Línea de negocio (``Familia`` o ``Patrimonio``).
    """

    key: str
    nombre: str
    linea: str


@dataclass(frozen=True, slots=True)
class VariableDef:
    """Una pregunta del cuestionario de perfilamiento.

    Args:
        code: Código corto (``V1``..``V11``).
        label: Texto de la pregunta.
        origen: ``sistema`` si se lee de la base de afiliados, ``formulario``
            si hay que preguntarla explícitamente.
        categorias: Respuestas válidas, en orden de presentación.
    """

    code: str
    label: str
    origen: Origen
    categorias: tuple[str, ...]

    def clave(self, categoria: str) -> str:
        """Construye la clave compuesta usada en la matriz de pesos.

        Args:
            categoria: Una de las respuestas válidas de la variable.

        Returns:
            La cadena ``"<code>|<categoria>"``.
        """
        return f"{self.code}|{categoria}"


@dataclass(frozen=True, slots=True)
class TriggerDef:
    """Regla dura que fuerza la entrada de un producto al top-N.

    Args:
        code: Código de la variable que dispara.
        categoria: Respuesta exacta que activa el disparador.
        product_key: Producto que se promueve.
        motivo: Justificación auditable, mostrada al cliente y al asesor.
    """

    code: str
    categoria: str
    product_key: str
    motivo: str


@dataclass(frozen=True, slots=True)
class ChecklistDef:
    """Requisitos de cotización de un producto.

    Args:
        modo: Texto de negocio (``"Sin intermediario"`` / ``"Con intermediario"``).
        items: Datos que hay que recolectar, o ``None`` si aún no se documentan.
    """

    modo: str
    items: tuple[str, ...] | None

    @property
    def modo_cierre(self) -> ModoCierre:
        """Traduce el modo de negocio a la bandera de flujo del producto.

        Returns:
            ``"auto"`` si el cierre es autoservicio, ``"asesoria"`` si requiere
            intervención de un asesor.
        """
        return (
            "auto" if self.modo.strip().lower() == "sin intermediario" else "asesoria"
        )


@dataclass(frozen=True, slots=True)
class Baseline:
    """Piso de referencia de un producto sobre el universo de perfiles.

    Args:
        product_key: Producto al que corresponde el piso.
        expected_score: Score esperado por las variables estructurales.
        max_score: Score máximo teórico del producto.
        expected_pct: ``expected_score / max_score * 100``.
        triggers: Disparadores que pueden promover este producto. Vacío si el
            producto solo compite por afinidad.
    """

    product_key: str
    expected_score: float
    max_score: int
    expected_pct: float
    triggers: tuple[TriggerDef, ...] = ()

    @property
    def tiene_trigger(self) -> bool:
        """Indica si el producto tiene al menos un disparador declarado."""
        return bool(self.triggers)


@dataclass(frozen=True, slots=True)
class AporteVariable:
    """Contribución de una variable al score, para auditoría.

    Args:
        code: Código de la variable.
        label: Texto de la pregunta.
        categoria: Respuesta del cliente.
        estructural: ``True`` si la variable entra al cálculo del piso.
        pesos: Vector de 12 enteros aportado por esta respuesta.
        rationale: Justificación documental de la fila.
    """

    code: str
    label: str
    categoria: str
    estructural: bool
    pesos: tuple[int, ...]
    rationale: str


@dataclass(frozen=True, slots=True)
class ResultadoProducto:
    """Score de un producto para un perfil concreto.

    Args:
        key: Identificador del producto.
        nombre: Nombre comercial.
        linea: Línea de negocio.
        score: Puntos crudos acumulados.
        max_score: Máximo teórico alcanzable.
        pct: Porcentaje del máximo alcanzado.
        baseline_pct: Piso del producto sobre el universo de perfiles.
        lift: ``pct - baseline_pct``. Métrica de ordenamiento por defecto.
        modo_cierre: ``"auto"`` o ``"asesoria"``.
        requiere_trigger: ``True`` si el producto declara disparadores. En ese
            caso solo compite por afinidad cuando alguno se activa.
        rank: Posición final, asignada al cierre del pipeline.
        triggered_by: Disparadores activados por este perfil.
        forced_explicit: ``True`` si el cliente pidió el producto por nombre.
    """

    key: str
    nombre: str
    linea: str
    score: int
    max_score: int
    pct: float
    baseline_pct: float
    lift: float
    modo_cierre: ModoCierre
    requiere_trigger: bool = False
    rank: int = 0
    triggered_by: tuple[TriggerDef, ...] = ()
    forced_explicit: bool = False

    @property
    def bloqueado(self) -> bool:
        """Indica que el producto exige un disparador y ninguno se activó."""
        return self.requiere_trigger and not self.triggered_by

    def con_rank(self, rank: int) -> ResultadoProducto:
        """Devuelve una copia con la posición asignada.

        Args:
            rank: Posición 1-indexada en el ranking final.

        Returns:
            Una nueva instancia; la original queda intacta.
        """
        return replace(self, rank=rank)


@dataclass(frozen=True, slots=True)
class ResultadoScoring:
    """Salida completa del motor para un perfil.

    Args:
        perfil: Respuestas recibidas, tal cual entraron.
        producto_explicito: Producto solicitado por el cliente, si lo hubo.
        ranking: Los 12 productos ordenados por la estrategia activa.
        aportes: Desglose por variable, en orden de cuestionario.
    """

    perfil: dict[str, str]
    producto_explicito: str | None
    ranking: tuple[ResultadoProducto, ...]
    aportes: tuple[AporteVariable, ...]

    @property
    def top(self) -> ResultadoProducto:
        """Producto recomendado en primera posición."""
        return self.ranking[0]

    @property
    def top_3(self) -> tuple[ResultadoProducto, ...]:
        """Las tres primeras recomendaciones."""
        return self.ranking[:3]
