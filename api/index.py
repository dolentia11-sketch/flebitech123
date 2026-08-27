# -*- coding: utf-8 -*-
"""
Punto de entrada Serverless para Vercel (FastAPI).
Gestiona los endpoints de la API de Flebitech.
"""

import os
import sys

# Agregar la raíz del proyecto al sys.path para importaciones de backend
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.metrics import log_question, get_session_stats, get_recent_interactions, get_knowledge_gaps

# Inicializar FastAPI
app = FastAPI(
    title="Flebitech API",
    description="API Educativa sobre Flebitis Química para Enfermería (laCardio & Universidad de La Sabana)",
    version="1.0.0"
)

# Habilitar CORS para integración web y widget embebible
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar motores
kb_path = os.path.join(root_dir, "knowledge_base")
rag = RAGEngine(knowledge_base_path=kb_path)
groq = GroqClient()

# Modelos Pydantic
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "web_session"

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    had_answer: bool
    topic: str
    latency_ms: float

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Flebitech API",
        "institution": "laCardio & Universidad de La Sabana",
        "indexed_chunks": len(rag.chunks),
        "medications_count": len(rag.medications)
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    # 1. Búsqueda RAG
    context, sources, has_match = rag.search(query, top_k=3)

    # 2. Consulta a Groq / Motor de Respaldo
    response_text, latency = groq.ask(query, context, has_relevant_content=has_match)

    is_gap = "Esa información no está disponible en el material de Flebitech" in response_text or not has_match
    had_answer = not is_gap

    # 3. Registro en métricas SQLite
    from backend.metrics import detect_topic
    topic = detect_topic(query)
    
    try:
        log_question(
            query=query,
            response=response_text,
            session_id=req.session_id,
            had_answer=had_answer,
            source_docs=",".join(sources),
            latency_ms=latency
        )
    except Exception as e:
        print(f"Aviso al guardar métrica: {e}")

    return ChatResponse(
        response=response_text,
        sources=sources if had_answer else [],
        had_answer=had_answer,
        topic=topic,
        latency_ms=round(latency, 1)
    )

@app.get("/api/medications")
def get_medications():
    return rag.medications

@app.get("/api/suggested")
def get_suggested():
    return [
        "¿Qué es la valoración DIVA y cuándo usarla?",
        "¿Qué medicamentos requieren vía central obligatoria?",
        "¿Cómo se clasifica la flebitis según la escala INS?",
        "¿Cuáles son los cuidados con la Vancomicina e infusión?",
        "¿Qué riesgos tiene el Cloruro de Potasio (KCl) periférico?",
        "¿Cuáles son los criterios de pH y osmolaridad críticos?"
    ]

@app.get("/api/metrics")
def get_metrics(session_id: Optional[str] = None):
    stats = get_session_stats(session_id)
    recent = get_recent_interactions(limit=10)
    gaps = get_knowledge_gaps(limit=10)
    return {
        "stats": stats,
        "recent": recent,
        "gaps": gaps
    }
