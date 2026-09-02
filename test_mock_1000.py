import os
import random
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator

print("Cargando RAG Engine (esto puede tomar unos segundos)...")
rag = RAGEngine(knowledge_base_path=os.path.join(current_dir, "knowledge_base"))
groq = GroqClient(api_key="")
random.seed(20260901)

def mock_generate_json(messages):
    groq.last_json_ok = True
    system_prompt = messages[0].get("content", "")
    if "orquestador cognitivo" in system_prompt:
        return {
            "intent": "clinical_query",
            "is_continuation": False,
            "rewritten_query": "",
            "expected_depth": "nivel_3"
        }
    else:
        return {
            "is_safe": True,
            "refined_response": "Simulated."
        }

def mock_generate_chat(messages):
    raise Exception("Simulated offline Groq")

groq.generate_json = mock_generate_json
groq.generate_chat = mock_generate_chat

orchestrator = ConversationalOrchestrator(rag_engine=rag, groq_client=groq)

print("Iniciando ejecución de 1000 pruebas simuladas...")
start_time = time.time()

CASES = [
    ("¿Cuál es el pH de la vancomicina?", True, "2.5 - 4.5"),
    ("¿Cuál es la capital de Francia?", False, "no especifica"),
    ("¿Cuándo uso Midline?", True, "7 a 29 días"),
]

success_count = 0
failed_count = 0

for _ in range(1000):
    query, expected_had_answer, expected_snippet = random.choice(CASES)
    try:
        response_text, sources, had_answer, latency = orchestrator.chat(query, history=[])
        if had_answer == expected_had_answer and expected_snippet.lower() in response_text.lower() and latency >= 0:
            success_count += 1
        else:
            failed_count += 1
            print(f"FAILED: {query} -> {response_text}")
    except Exception as e:
        failed_count += 1
        print(f"EXCEPTION: {e}")

total_time = time.time() - start_time

print("="*50)
print("RESULTADOS DE 1000 TESTS (MOCKED API)")
print("="*50)
print(f"Total pruebas ejecutadas: 1000")
print(f"Éxitos: {success_count}")
print(f"Fallos: {failed_count}")
print(f"Tiempo total: {total_time:.2f} segundos")
print(f"Tiempo promedio por turno: {(total_time/1000)*1000:.2f} ms")
print("="*50)

if failed_count > 0 or success_count != 1000:
    sys.exit(1)
