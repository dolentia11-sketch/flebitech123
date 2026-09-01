import os
import json
from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator

rag = RAGEngine(knowledge_base_path="C:\\Users\\anglo\\OneDrive\\Escritorio\\FLEBITECH\\knowledge_base")
client = GroqClient()
orchestrator = ConversationalOrchestrator(rag_engine=rag, groq_client=client)

tests = [
    "¿Qué es DIVA?",
    "¿Cuáles son los criterios de DIVA en adultos?",
    "Explícame DIVA completa.",
    "¿Y cómo se interpreta?",
    "¿Qué pasa con 4 puntos?",
    "Escala INS completa.",
    "¿Qué es grado 2?",
    "Amplía el grado 2.",
    "Catéter.",
    "¿Cuál es elegible?",
    "¿Y si tiene DIVA alto?",
    "¿Cuál es el pH de la vancomicina?",
    "¿Y la dilución?",
    "¿Y los cuidados?",
    "Compárala con otra."
]

history = []

for q in tests:
    print(f"\n--- USER: {q} ---")
    resp, sources, has_resp, lat = orchestrator.chat(q, history=history)
    print(f"FLEBITECH: {resp}")
    history.append({"role": "user", "content": q})
    history.append({"role": "assistant", "content": resp})
