"""CRM simulado — stub del MVP.

En producción (insight de Emmy, 25-jul): el número de WhatsApp se cruza con
Salesforce al entrar. En el MVP (chat web): la cédula del flujo de Caro se
consulta aquí y devuelve el registro del afiliado.

Este módulo es el placeholder de lo que después se conecta al Salesforce real.
La cédula NO se persiste — quien reciba el dict debe hashearla con
`trazabilidad.hash_id()` antes de guardar cualquier cosa (Ley 1581).
"""

_AFILIADOS = {
    "1010101010": {
        "nombre": "Ana",
        "edad": 34,
        "genero": "F",
        "ocupacion": "empleada",
        "ciudad": "Bogotá",
        "tiene_seguro_previo": False,
        "afiliado_activo": True,
    },
    "2020202020": {
        "nombre": "Carlos",
        "edad": 52,
        "genero": "M",
        "ocupacion": "independiente",
        "ciudad": "Medellín",
        "tiene_seguro_previo": True,
        "afiliado_activo": True,
    },
    "3030303030": {
        "nombre": "Luisa",
        "edad": 27,
        "genero": "F",
        "ocupacion": "estudiante",
        "ciudad": "Cali",
        "tiene_seguro_previo": False,
        "afiliado_activo": False,
    },
}


def consultar(cedula: str) -> dict | None:
    """Devuelve el registro del afiliado o None si no aparece."""
    return _AFILIADOS.get(cedula)
