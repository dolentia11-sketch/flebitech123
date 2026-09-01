# -*- coding: utf-8 -*-
"""
Suite de pruebas completas de Flebitech v1.1
Verifica: RAG Engine, Groq Client, Metrics, FastAPI Endpoints y Guardrails.
"""

import os
import sys
import json
import time

# Fix encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup paths
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

passed = 0
failed = 0
total = 0


def test(name, condition, detail=""):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


print("=" * 70)
print("  FLEBITECH v1.1 - SUITE DE PRUEBAS COMPLETAS")
print("=" * 70)

# ===== 1. KNOWLEDGE BASE FILES =====
print("\n--- 1. Integridad de la Base de Conocimiento ---")

kb_path = os.path.join(ROOT, "knowledge_base")
test("Directorio knowledge_base/ existe", os.path.isdir(kb_path))

med_file = os.path.join(kb_path, "medicamentos.json")
test("medicamentos.json existe", os.path.isfile(med_file))

with open(med_file, 'r', encoding='utf-8') as f:
    meds = json.load(f)
test("medicamentos.json contiene 15 farmacos", len(meds) == 15, f"Encontrados: {len(meds)}")

required_fields = ['nombre', 'grupo', 'ph', 'osmolaridad', 'via_recomendada',
                   'riesgo_flebitis', 'diluyente_recomendado', 'observaciones_enfermeria']
for med in meds:
    for field in required_fields:
        test(f"  {med['nombre']} tiene campo '{field}'", field in med and med[field])

test("escalas.md existe", os.path.isfile(os.path.join(kb_path, "escalas.md")))
test("protocolo_basico.md existe", os.path.isfile(os.path.join(kb_path, "protocolo_basico.md")))
test("casos_clinicos.md existe", os.path.isfile(os.path.join(kb_path, "casos_clinicos.md")))

# ===== 2. RAG ENGINE =====
print("\n--- 2. Motor RAG ---")

from backend.rag_engine import RAGEngine

rag = RAGEngine(knowledge_base_path=kb_path)
test("RAG inicializado correctamente", rag is not None)
test(f"RAG indexo chunks (>20)", len(rag.chunks) > 20, f"Chunks: {len(rag.chunks)}")
test(f"RAG cargo 15 medicamentos", len(rag.medications) == 15, f"Meds: {len(rag.medications)}")
test("Vocabulario TF-IDF construido", len(rag.idf) > 100, f"Terminos: {len(rag.idf)}")

# Test: Busqueda de farmaco exacto
ctx, srcs, match = rag.search("Vancomicina", top_k=3)
test("Busqueda 'Vancomicina' - match encontrado", match)
test("Busqueda 'Vancomicina' - contexto contiene farmaco", "vancomicina" in ctx.lower())
test("Busqueda 'Vancomicina' - fuente incluye medicamentos.json", "medicamentos.json" in srcs)

# Test: Busqueda escala DIVA
ctx, srcs, match = rag.search("¿Qué es la valoración DIVA?", top_k=3)
test("Busqueda 'DIVA' - match encontrado", match)
test("Busqueda 'DIVA' - contexto relevante", "diva" in ctx.lower())

# Test: Busqueda escala INS
ctx, srcs, match = rag.search("escala de flebitis INS grados", top_k=3)
test("Busqueda 'INS' - match encontrado", match)

# Test: Busqueda KCl
ctx, srcs, match = rag.search("cloruro de potasio KCl periférico", top_k=3)
test("Busqueda 'KCl' - match encontrado", match)
test("Busqueda 'KCl' - contexto relevante", "potasio" in ctx.lower() or "kcl" in ctx.lower())

# Test: Consulta fuera de dominio NO debe matchear
ctx, srcs, match = rag.search("¿Cuál es la capital de Francia?", top_k=3)
test("Consulta fuera de dominio NO matchea", not match)

# Test: Busqueda protocolo
ctx, srcs, match = rag.search("protocolo de antisepsia clorhexidina", top_k=3)
test("Busqueda protocolo - match encontrado", match)

# Test: NPT via central
ctx, srcs, match = rag.search("nutricion parenteral total vía central", top_k=3)
test("Busqueda 'NPT' - match encontrado", match)

# Test: Fenitoina
ctx, srcs, match = rag.search("Fenitoína pH alcalino", top_k=3)
test("Busqueda 'Fenitoina' - match encontrado", match)
test("Busqueda 'Fenitoina' - contexto relevante", "fenitoina" in ctx.lower() or "fenitoína" in ctx.lower() or "difenilhidantoina" in ctx.lower() or "difenilhidantoína" in ctx.lower())

# Test: Normalización de acentos (sin tildes busca bien)
ctx_sin_tilde, _, match_sin_tilde = rag.search("fenitoina sodica ph", top_k=3)
test("Busqueda sin tildes 'fenitoina' funciona", match_sin_tilde)

# Test: Alias de farmacos (ej. difenilhidantoina, kcl)
ctx_alias, _, match_alias = rag.search("difenilhidantoina dosis y ph", top_k=3)
test("Busqueda por alias 'difenilhidantoina' funciona", match_alias)

ctx_kcl, _, match_kcl = rag.search("infusion kcl via periferica", top_k=3)
test("Busqueda por alias 'kcl' funciona", match_kcl)

# ===== 3. GROQ CLIENT (modo determinista) =====
print("\n--- 3. Groq Client (Motor Determinista) ---")

from backend.groq_client import GroqClient

groq = GroqClient(api_key="")  # Sin API key = motor local
test("GroqClient inicializado sin API key", groq.client is None)

# Con contenido relevante => debe dar respuesta local
ctx_vanc = "### [Fuente: medicamentos.json | Vancomicina]\nMEDICAMENTO: Vancomicina\n- pH: 2.5 - 4.5\n- Riesgo: Alto"
response, latency = groq.ask("¿Qué pH tiene la Vancomicina?", ctx_vanc, has_relevant_content=True)
test("Respuesta local con contexto - no vacia", len(response) > 10)
test("Respuesta local contiene info de contexto", "vancomicina" in response.lower() or "2.5" in response)
test("Latencia calculada (>0)", latency > 0)

# Con historial conversacional
history_sample = [
    {"role": "user", "content": "Quiero saber sobre la Vancomicina"},
    {"role": "assistant", "content": "La Vancomicina es un antibiótico glucopéptido."}
]
response_hist, _ = groq.ask("¿Y cuál es su pH?", ctx_vanc, has_relevant_content=True, history=history_sample)
test("Respuesta con historial soportada", len(response_hist) > 10)

# Sin contenido relevante => debe dar FALLBACK exacto
response_gap, latency_gap = groq.ask("¿Cuánto cuesta un pasaje a Madrid?", "", has_relevant_content=False)
test("Respuesta FALLBACK para consulta sin contexto", "no está disponible" in response_gap)

# ===== 4. METRICS MODULE =====
print("\n--- 4. Modulo de Metricas ---")

# Forzar modo no-Vercel para probar archivo
os.environ.pop("VERCEL", None)
os.environ.pop("VERCEL_ENV", None)

from backend.metrics import detect_topic, log_question, get_session_stats, get_recent_interactions, get_knowledge_gaps

# Topic detection
test("Topic: DIVA detectado", detect_topic("DIVA difícil acceso") == "Valoración DIVA")
test("Topic: INS detectado", detect_topic("escala INS grado 3") == "Escalas de Flebitis (INS/VHP)")
test("Topic: Cateter detectado", detect_topic("catéter calibre 22G") == "Selección de Catéter")
test("Topic: Medicamentos detectado", detect_topic("vancomicina dilución") == "Medicamentos Específicos")
test("Topic: pH/Osmolaridad detectado", detect_topic("osmolaridad mayor a 600") == "Parámetros Fisicoquímicos (pH/Osmolaridad)")
test("Topic: Caso clínico detectado", detect_topic("caso clínico simulación") == "Casos Clínicos / Escenarios")
test("Topic: Protocolo detectado", detect_topic("protocolo clorhexidina punción") == "Protocolos Institucionales")
test("Topic: General para desconocido", detect_topic("hola buenos dias") == "Consulta General / Otra")

# Log questions
test_session = "test_" + str(int(time.time()))
row1 = log_question("¿Qué pH tiene la vancomicina?", "pH 2.5-4.5", session_id=test_session, had_answer=True, latency_ms=123.4)
test("Log pregunta respondida (row_id > 0)", row1 > 0)

row2 = log_question("¿Cuánto cuesta un avión?", "info no disponible", session_id=test_session, had_answer=False, latency_ms=5.0)
test("Log pregunta brecha (row_id > 0)", row2 > 0)

stats = get_session_stats(test_session)
test("Stats session: total = 2", stats['total_preguntas'] == 2, f"Got: {stats['total_preguntas']}")
test("Stats session: respondidas = 1", stats['respondidas'] == 1, f"Got: {stats['respondidas']}")
test("Stats session: brechas = 1", stats['brechas_detectadas'] == 1, f"Got: {stats['brechas_detectadas']}")
test("Stats session: tasa = 50%", stats['tasa_resolucion'] == 50.0, f"Got: {stats['tasa_resolucion']}")

recent = get_recent_interactions(limit=5)
test("Recent interactions devuelve lista", isinstance(recent, list) and len(recent) > 0)

gaps = get_knowledge_gaps(limit=5)
test("Knowledge gaps devuelve lista", isinstance(gaps, list) and len(gaps) > 0)

# ===== 5. FASTAPI ENDPOINTS =====
print("\n--- 5. FastAPI Endpoints ---")

# Add api dir to path
api_dir = os.path.join(ROOT, 'api')
sys.path.insert(0, api_dir)

from fastapi.testclient import TestClient
from api.index import app as fastapi_app

client = TestClient(fastapi_app)

# GET /
res = client.get("/")
test("GET / - status 200", res.status_code == 200)
data = res.json()
test("GET / - status online", data.get('status') == 'online')
test("GET / - tiene chunks indexados", data.get('indexed_chunks', 0) > 0)
test("GET / - tiene medicamentos", data.get('medications_count', 0) == 15)

# GET /api/health
res = client.get("/api/health")
test("GET /api/health - status 200", res.status_code == 200)
test("GET /api/health - healthy", res.json().get('status') == 'healthy')

# POST /api/chat - Pregunta valida
res = client.post("/api/chat", json={"query": "¿Qué pH tiene la Vancomicina?", "session_id": "test"})
test("POST /api/chat Vancomicina - status 200", res.status_code == 200)
chat_data = res.json()
test("POST /api/chat - response no vacia", len(chat_data.get('response', '')) > 10)
test("POST /api/chat - had_answer true", chat_data.get('had_answer') == True)
test("POST /api/chat - topic detectado", len(chat_data.get('topic', '')) > 0)
test("POST /api/chat - latency >= 0", chat_data.get('latency_ms', -1) >= 0)

# POST /api/chat - Consulta vacia
res = client.post("/api/chat", json={"query": "", "session_id": "test"})
test("POST /api/chat vacia - status 400", res.status_code == 400)

# POST /api/chat - Consulta muy larga
res = client.post("/api/chat", json={"query": "x" * 501, "session_id": "test"})
test("POST /api/chat muy larga - status 400", res.status_code == 400)

# POST /api/chat - Consulta fuera de dominio
res = client.post("/api/chat", json={"query": "¿Cuál es la capital de Francia?", "session_id": "test"})
test("POST /api/chat fuera de dominio - status 200", res.status_code == 200)
gap_data = res.json()
test("POST /api/chat fuera de dominio - had_answer false", gap_data.get('had_answer') == False)
test("POST /api/chat fuera de dominio - respuesta FALLBACK", "no está disponible" in gap_data.get('response', ''))

# GET /api/medications
res = client.get("/api/medications")
test("GET /api/medications - status 200", res.status_code == 200)
med_list = res.json()
test("GET /api/medications - 15 farmacos", len(med_list) == 15)
test("GET /api/medications - primer farmaco tiene 'nombre'", 'nombre' in med_list[0])

# GET /api/suggested
res = client.get("/api/suggested")
test("GET /api/suggested - status 200", res.status_code == 200)
suggestions = res.json()
test("GET /api/suggested - >= 6 sugerencias", len(suggestions) >= 6)

# GET /api/metrics
res = client.get("/api/metrics")
test("GET /api/metrics - status 200", res.status_code == 200)
metrics = res.json()
test("GET /api/metrics - tiene stats", 'stats' in metrics)
test("GET /api/metrics - tiene recent", 'recent' in metrics)
test("GET /api/metrics - tiene gaps", 'gaps' in metrics)

# POST /api/chat - Con historial de conversacion
res_hist = client.post("/api/chat", json={
    "query": "¿Y qué cuidados debo tener?",
    "session_id": "test",
    "history": [
        {"role": "user", "content": "Hablemos de Vancomicina"},
        {"role": "assistant", "content": "La Vancomicina tiene pH de 2.5 a 4.5."}
    ]
})
test("POST /api/chat con historial - status 200", res_hist.status_code == 200)

# ===== 6. GUARDRAILS CLINICOS =====
print("\n--- 6. Guardrails Clinicos ---")

from backend.prompt_system import SYSTEM_PROMPT, FALLBACK_MESSAGE, build_user_prompt, is_knowledge_gap

test("SYSTEM_PROMPT no vacio", len(SYSTEM_PROMPT) > 100)
test("SYSTEM_PROMPT menciona 'nunca inventes'", "nunca inventes" in SYSTEM_PROMPT.lower() or "nunca invent" in SYSTEM_PROMPT.lower())
test("SYSTEM_PROMPT menciona pH y osmolaridad", "ph" in SYSTEM_PROMPT.lower() and "osmolaridad" in SYSTEM_PROMPT.lower())
test("FALLBACK_MESSAGE contiene frase estandar", "no está disponible" in FALLBACK_MESSAGE)
test("is_knowledge_gap detecta fallback estandar", is_knowledge_gap(FALLBACK_MESSAGE))
test("is_knowledge_gap detecta respuesta valida", not is_knowledge_gap("El pH de la vancomicina es 2.5 a 4.5."))

prompt = build_user_prompt("¿pH de Vancomicina?", "Vancomicina pH 2.5-4.5")
test("build_user_prompt incluye contexto", "vancomicina" in prompt.lower())
test("build_user_prompt incluye pregunta", "ph" in prompt.lower())

# ===== 7. VERCEL CONFIGURATION =====
print("\n--- 7. Configuracion de Vercel ---")

vercel_file = os.path.join(ROOT, "vercel.json")
test("vercel.json existe", os.path.isfile(vercel_file))

with open(vercel_file, 'r', encoding='utf-8') as f:
    vercel_cfg = json.load(f)

test("vercel.json version 2", vercel_cfg.get('version') == 2)
test("vercel.json tiene builds", len(vercel_cfg.get('builds', [])) >= 2)
test("vercel.json tiene routes", len(vercel_cfg.get('routes', [])) >= 3)

# Check Python build
py_build = [b for b in vercel_cfg['builds'] if 'python' in b.get('use', '')]
test("Build Python configurado", len(py_build) > 0)

# Check static build
static_build = [b for b in vercel_cfg['builds'] if 'static' in b.get('use', '')]
test("Build Static configurado", len(static_build) > 0)

# ===== 8. FILE STRUCTURE =====
print("\n--- 8. Estructura de Archivos ---")

required_files = [
    'api/index.py',
    'public/index.html',
    'public/widget.js',
    'backend/__init__.py',
    'backend/rag_engine.py',
    'backend/groq_client.py',
    'backend/prompt_system.py',
    'backend/metrics.py',
    'knowledge_base/medicamentos.json',
    'knowledge_base/escalas.md',
    'knowledge_base/protocolo_basico.md',
    'knowledge_base/casos_clinicos.md',
    'vercel.json',
    'requirements.txt',
    '.gitignore',
]

for f in required_files:
    test(f"Archivo {f} existe", os.path.isfile(os.path.join(ROOT, f)))

# Check requirements.txt doesn't include streamlit (bloats Vercel)
with open(os.path.join(ROOT, 'requirements.txt'), 'r') as f:
    reqs = f.read()
test("requirements.txt NO incluye streamlit (Vercel)", 'streamlit' not in reqs)
test("requirements.txt incluye fastapi", 'fastapi' in reqs)
test("requirements.txt incluye groq", 'groq' in reqs)

# ===== RESUMEN FINAL =====
print("\n" + "=" * 70)
print(f"  RESULTADOS: {passed}/{total} pruebas pasaron")
if failed > 0:
    print(f"  FALLIDAS: {failed} prueba(s)")
else:
    print("  ESTADO: 100% FUNCIONAL - LISTO PARA DESPLIEGUE EN VERCEL")
print("=" * 70)
