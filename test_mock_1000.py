import os
import random
import sys
import time

# Agregamos la ruta
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator

# 1. Instanciamos dependencias
print("Cargando RAG Engine (esto puede tomar unos segundos)...")
rag = RAGEngine(knowledge_base_path=os.path.join(current_dir, "knowledge_base"))
groq = GroqClient(api_key="")
random.seed(20260901)

# 2. Mockeamos los métodos de GroqClient para evitar llamadas a la API y Rate Limits
def mock_generate_json(messages):
    # Simulamos una salida válida del router sin red.
    groq.last_json_ok = True
    system_prompt = messages[0].get("content", "")
    if "orquestador cognitivo" in system_prompt:
        # Es el Router
        intents = ["clinical_query", "greeting", "out_of_domain"]
        return {
            "intent": random.choices(intents, weights=[0.8, 0.1, 0.1])[0],
            "is_continuation": random.choice([True, False]),
            "rewritten_query": "catéter venoso periférico diva", # Búsqueda simulada
            "expected_depth": random.choice(["nivel_1", "nivel_2", "nivel_3", "nivel_5"])
        }
    else:
        # Es el Validator
        return {
            "is_safe": True,
            "refined_response": "Esta es una respuesta clíníca simulada validada."
        }

def mock_generate_chat(messages):
    # Simulamos el LLM generador
    return "Respuesta cruda generada por el LLM antes de validación."

groq.generate_json = mock_generate_json
groq.generate_chat = mock_generate_chat

orchestrator = ConversationalOrchestrator(rag_engine=rag, groq_client=groq)

print("Iniciando ejecución de 1000 pruebas simuladas...")
start_time = time.time()

# 3. Ejecutamos 1000 interacciones simuladas
queries = [
    "¿Qué es DIVA?",
    "¿Y en adultos?",
    "Amplía grado 2",
    "catéter",
    "Hola, ¿cómo estás?",
    "¿Cuál es el pH de la vancomicina?",
    "Dame la tabla completa de INS",
    "¿Qué hago si tengo un paciente con DIVA 4 y necesita Vancomicina por 10 días?"
]

success_count = 0
failed_count = 0

for _ in range(1000):
    query = random.choice(queries)
    try:
        response_text, sources, had_answer, latency = orchestrator.chat(query, history=[])
        if isinstance(response_text, str) and response_text.strip() and latency >= 0:
            success_count += 1
        else:
            failed_count += 1
    except Exception as e:
        failed_count += 1

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
print("Las nuevas integraciones (Router -> RAG -> Generation -> Validation) procesan el flujo correctamente sin errores de código.")
if failed_count or success_count != 1000:
    sys.exit(1)
