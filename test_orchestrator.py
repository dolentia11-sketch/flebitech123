import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Agregamos la ruta
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator

rag = RAGEngine(knowledge_base_path=os.path.join(current_dir, "knowledge_base"))
groq = GroqClient(api_key="")
orchestrator = ConversationalOrchestrator(rag_engine=rag, groq_client=groq)

def run_test(query: str, history: list = None):
    print(f"--- QUERY: {query} ---")
    response_text, sources, had_answer, latency = orchestrator.chat(query, history=history)
    print(f"Had Answer: {had_answer}")
    print(f"Latency: {latency:.1f} ms")
    print(f"Sources: {sources}")
    print(f"RESPONSE:\n{response_text}\n")
    print("="*60)
    return response_text

history_diva = []

print("TEST 1: ¿Qué es DIVA?")
resp1 = run_test("¿Qué es DIVA?", history_diva)
history_diva.extend([{"role": "user", "content": "¿Qué es DIVA?"}, {"role": "assistant", "content": resp1}])

print("TEST 2: ¿Cuáles son los criterios de DIVA en adultos?")
resp2 = run_test("¿Cuáles son los criterios de DIVA en adultos?", history_diva)
history_diva.extend([{"role": "user", "content": "¿Cuáles son los criterios de DIVA en adultos?"}, {"role": "assistant", "content": resp2}])

print("TEST 3: Explícame DIVA completa")
run_test("Explícame DIVA completa", [])

print("TEST 4: Tengo un paciente pediátrico, ¿qué criterios aplico? (Usando historial)")
run_test("Tengo un paciente pediátrico, ¿qué criterios aplico?", history_diva)

print("TEST 5: pH de vancomicina")
history_meds = []
resp5 = run_test("pH de vancomicina", history_meds)
history_meds.extend([{"role": "user", "content": "pH de vancomicina"}, {"role": "assistant", "content": resp5}])

print("TEST 6: ¿Y amiodarona? (Usando historial)")
run_test("¿Y amiodarona?", history_meds)

print("TEST 7: Escala INS completa")
run_test("Escala INS completa", [])

print("TEST 8: ¿Qué grado es si hay cordón palpable?")
run_test("¿Qué grado es si hay cordón palpable?", [])

print("TEST 9: catéter")
run_test("catéter", [])

print("TEST 10: Hola")
run_test("Hola", [])

print("TEST 11: Dame los medicamentos")
run_test("Dame los medicamentos", [])

print("TEST 12: Tengo un paciente con flebitis química por potasio, ¿qué hago?")
run_test("Tengo un paciente con flebitis química por potasio, ¿qué hago?", [])

print("TEST 13: ¿Cuándo uso Midline?")
run_test("¿Cuándo uso Midline?", [])

print("TEST 14: Criterios VHP")
history_vhp = []
resp14 = run_test("Criterios VHP", history_vhp)
history_vhp.extend([{"role": "user", "content": "Criterios VHP"}, {"role": "assistant", "content": resp14}])

print("TEST 15: ¿Y qué hago si tiene VHP 3?")
run_test("¿Y qué hago si tiene VHP 3?", history_vhp)
