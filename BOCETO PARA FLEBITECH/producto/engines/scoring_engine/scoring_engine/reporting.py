"""Formateo de resultados a texto plano.

Se mantiene separado del motor porque la presentación cambia mucho más rápido
que el cálculo, y porque una capa de salida distinta (JSON para el frontend,
PDF para el asesor) no debería obligar a tocar la aritmética.
"""

from __future__ import annotations

from scoring_engine.engine import MotorScoring
from scoring_engine.models import Baseline, ResultadoScoring

#: Umbral de peso a partir del cual un racional se considera determinante y se
#: muestra al cliente en la ficha.
UMBRAL_RACIONAL = 3


def tabla_baselines(baselines: dict[str, Baseline], motor: MotorScoring) -> str:
    """Rinde la tabla de pisos por producto, marcando los disparadores.

    Args:
        baselines: Pisos calculados, por clave de producto.
        motor: Motor del que se toman los nombres comerciales.

    Returns:
        Una tabla de ancho fijo lista para imprimir en consola.
    """
    lineas = [
        f"{'Producto':<34}{'E[score]':>10}{'Máx':>6}{'Piso %':>9}  Disparador",
        "-" * 96,
    ]
    for producto in motor.catalogo.products:
        base = baselines[producto.key]
        if base.tiene_trigger:
            marca = "⚑ " + ", ".join(f"{t.code}={t.categoria}" for t in base.triggers)
        else:
            marca = "—"
        lineas.append(
            f"{producto.nombre[:33]:<34}"
            f"{base.expected_score:>10.2f}"
            f"{base.max_score:>6}"
            f"{base.expected_pct:>9.2f}  "
            f"{marca}"
        )
    return "\n".join(lineas)


def tabla_ranking(resultado: ResultadoScoring, top_n: int | None = None) -> str:
    """Rinde el ranking de un perfil con score, pct, piso y lift.

    Args:
        resultado: Salida del motor.
        top_n: Cuántas posiciones mostrar. ``None`` muestra todas.

    Returns:
        Una tabla de ancho fijo lista para imprimir en consola.
    """
    filas = resultado.ranking if top_n is None else resultado.ranking[:top_n]
    lineas = [
        f"{'#':>3} {'Producto':<34}{'Score':>8}{'Pct':>8}{'Piso':>8}"
        f"{'Lift':>8}  {'Cierre':<9} Nota",
        "-" * 104,
    ]
    for item in filas:
        notas = []
        if item.forced_explicit:
            notas.append("★ solicitado")
        if item.triggered_by:
            notas.append("⚑ " + ", ".join(t.code for t in item.triggered_by))
        lineas.append(
            f"{item.rank:>3} {item.nombre[:33]:<34}"
            f"{f'{item.score}/{item.max_score}':>8}"
            f"{item.pct:>8.1f}"
            f"{item.baseline_pct:>8.2f}"
            f"{item.lift:>+8.2f}  "
            f"{item.modo_cierre:<9} "
            f"{' '.join(notas)}"
        )
    return "\n".join(lineas)


def ficha_texto(
    motor: MotorScoring,
    resultado: ResultadoScoring,
    afiliado: bool | None = None,
) -> str:
    """Genera la ficha de cierre o el resumen para el asesor.

    El encabezado y el paso siguiente dependen del ``modo_cierre`` del producto
    recomendado: autoservicio termina en pago en línea, asesoría termina en
    agendamiento de llamada.

    Args:
        motor: Motor que produjo el resultado, usado para leer el checklist.
        resultado: Salida del motor para el perfil.
        afiliado: Si el cliente es afiliado a Colsubsidio. Es informativo y no
            afecta el cálculo.

    Returns:
        La ficha completa en texto plano.
    """
    top = resultado.top
    checklist = motor.catalogo.checklist.get(top.key)
    indice = motor.catalogo.indice(top.key)

    perfil_txt = "\n".join(
        f"- {a.code} {a.label}: {a.categoria}" for a in resultado.aportes
    )

    motivos = [f"- {t.motivo}" for t in top.triggered_by]
    motivos += [
        f"- {a.rationale}"
        for a in resultado.aportes
        if a.pesos[indice] >= UMBRAL_RACIONAL and a.rationale
    ]
    motivos_txt = "\n".join(motivos) if motivos else "(sin racional destacado)"

    if checklist and checklist.items:
        checklist_txt = "\n".join(f"- {item}" for item in checklist.items)
    else:
        checklist_txt = "(sin checklist documentado — validar con Colsubsidio)"

    if top.modo_cierre == "auto":
        header = f"FICHA DE CIERRE AUTOMATIZADO — {top.nombre}"
        cierre = "Sin intermediario — cierre automatizado"
        paso = "Siguiente paso: pasar esta ficha a cotización y pago en línea."
    else:
        header = f"RESUMEN PARA ASESOR — {top.nombre}"
        cierre = "Con intermediario — asesoría personalizada"
        paso = "Siguiente paso: enviar este resumen al asesor para agendar la llamada."

    afiliado_txt = "N/D" if afiliado is None else ("Sí" if afiliado else "No")

    return (
        f"{header}\n"
        f"Perfilador Colsubsidio — motor de reglas\n\n"
        f"Cliente afiliado a Colsubsidio: {afiliado_txt}\n"
        f"Producto recomendado: {top.nombre} ({top.linea})\n"
        f"Afinidad: {top.pct}% | Piso del producto: {top.baseline_pct}% | "
        f"Lift: {top.lift:+.2f} pp\n"
        f"Modo de cierre: {cierre}\n\n"
        f"Perfil capturado:\n{perfil_txt}\n\n"
        f"Por qué este producto:\n{motivos_txt}\n\n"
        f"Datos para cotizar:\n{checklist_txt}\n\n"
        f"{paso}"
    )
