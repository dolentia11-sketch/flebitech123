# -*- coding: utf-8 -*-
"""Pruebas semánticas del flujo conversacional sin consumir la API de Groq."""

import os
import sys

from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator
from backend.rag_engine import RAGEngine


ROOT = os.path.dirname(os.path.abspath(__file__))
rag = RAGEngine(os.path.join(ROOT, "knowledge_base"))
orchestrator = ConversationalOrchestrator(rag, GroqClient(api_key=""))

passed = 0
failed = 0


def check(name, query, expected=(), history=None, had_answer=True, forbidden=()):
    global passed, failed
    response, sources, actual_had_answer, latency = orchestrator.chat(query, history or [])
    normalized = response.lower()
    ok = (
        actual_had_answer is had_answer
        and bool(response.strip())
        and all(term.lower() in normalized for term in expected)
        and all(term.lower() not in normalized for term in forbidden)
        and latency >= 0
    )
    if ok:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}\n  query={query!r}\n  had_answer={actual_had_answer}\n  sources={sources}\n  response={response[:800]!r}")
    return response


def turn(user, assistant):
    return [
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]


check("DIVA breve", "¿Qué es DIVA?", ("herramienta predictiva", "acceso venoso difícil"))
check("DIVA adulto completo", "¿Cuáles son los criterios DIVA en adultos?", ("historial de acceso", "imposibilidad de palpar", "urgencia"))
check("P-DIVA pediátrico", "Tengo un paciente pediátrico, ¿qué criterios DIVA aplico?", ("prematuridad", "edad menor a 1 año", "2 intentos fallidos"))

ins_history = turn("Escala INS completa", "La escala INS clasifica la flebitis de grado 0 a 4.")
check("INS grado 2 contextual", "¿Qué es grado 2?", ("grado 2", "dolor", "retirar el catéter"), ins_history)
check("INS grado 2 ampliado", "Amplía el grado 2", ("permeabilidad capilar", "documentar fecha"), ins_history)
check("Cordón palpable", "¿Qué grado es si hay cordón palpable?", ("grado 3", "trombo mural", "retirar el catéter"))

vhp_history = turn("Criterios VHP", "La escala VHP clasifica signos de flebitis.")
check("VHP 3 contextual", "¿Y qué hago si tiene VHP 3?", ("vhp 3", "retirar el catéter", "documentar"), vhp_history)

catheter_history = turn("catéter", "La base aborda selección, elegibilidad y calibres de catéter.")
check("Elegibilidad contextual", "¿Cuál es elegible?", ("catéter periférico corto", "midline", "picc"), catheter_history)
check("Midline puntual", "¿Cuándo uso Midline?", ("7 a 29 días", "osmolaridad", "ultrasonido"))

check("Catálogo farmacológico", "Dame los medicamentos", ("vancomicina", "amiodarona", "metronidazol", "nutrición parenteral"))
check("Catálogo farmacológico en forma de pregunta", "¿Cuáles son los medicamentos?", ("medicamentos documentados (15)", "claritromicina iv", "dad 50%"))

# Cada medicamento de la fuente debe funcionar sin depender de una lista manual
# del router ni de la disponibilidad del proveedor LLM.
for medication in rag.medications:
    medication_name = medication["nombre"]
    check(
        f"Ficha farmacológica: {medication_name}",
        medication_name,
        (medication_name.split(" (")[0], "vía recomendada", "riesgo de flebitis"),
    )

vancomycin = check("pH de vancomicina", "¿Cuál es el pH de la vancomicina?", ("2.5 - 4.5",), forbidden=("osmolaridad", "tiempo de infusión"))
check(
    "Cambio explícito de medicamento",
    "¿Y amiodarona?",
    ("amiodarona", "exclusivamente dad 5%"),
    turn("¿Cuál es el pH de la vancomicina?", vancomycin),
    forbidden=("síndrome del hombre rojo",),
)
check("Dilución contextual", "¿Y la dilución?", ("5 mg/ml", "1000 mg en 200-250 ml"), turn("¿Cuál es el pH de la vancomicina?", vancomycin))
check(
    "Dilución contextual con turno actual duplicado por cliente web",
    "¿Y la dilución?",
    ("5 mg/ml", "1000 mg en 200-250 ml"),
    turn("¿Cuál es el pH de la vancomicina?", vancomycin)
    + [{"role": "user", "content": "¿Y la dilución?"}],
    forbidden=("Exclusivamente DAD 5%", "Bolsa premezclada", "2 mg/ml"),
)
check("Conducta KCl", "Tengo un paciente con flebitis química por potasio, ¿qué hago?", ("nunca administrar directo", "10 meq/hora", "dolor intenso"))
check(
    "Filtro farmacológico de vía central",
    "¿Qué medicamentos requieren vía central obligatoria?",
    ("nutrición parenteral total", "cloruro de potasio", "condición exacta"),
)
check(
    "Comparación de medicamentos",
    "Compara vancomicina y amiodarona",
    ("comparación farmacológica", "2.5 - 4.5", "exclusivamente dad 5%"),
)

furosemide = check(
    "Dilución de furosemida",
    "¿Cuál es la dilución de la furosemida?",
    ("ssn 0.9%", "50-100 ml"),
    forbidden=("vancomicina", "amiodarona"),
)
check(
    "Continuación farmacológica puntual",
    "¿Y el tiempo de infusión?",
    ("4 mg/min",),
    turn("¿Cuál es la dilución de la furosemida?", furosemide),
    forbidden=("osmolaridad", "vía recomendada"),
)

check("Agradecimiento natural", "Gracias", ("con gusto", "mantengo el contexto"))
check("Explicación de capacidades", "¿En qué me puedes ayudar?", ("medicamentos", "diva", "selección de catéteres"))

diva_history = turn("¿Qué es DIVA?", "DIVA estratifica el acceso venoso difícil.")
check("Interpretación DIVA", "¿Y cómo se interpreta?", ("bajo riesgo", "riesgo moderado", "alto riesgo"), diva_history)

check("Fuera de dominio", "¿Cuál es la capital de Francia?", ("no especifica",), had_answer=False)

print(f"\nRESULTADO CONVERSACIONAL: {passed}/{passed + failed} pruebas pasaron")
if failed:
    sys.exit(1)
