"""
Punto de entrada Serverless para Vercel (FastAPI).
Gestiona los endpoints de la API de Flebitech.
"""

import os
import re
import sys

# Agregar la raíz del proyecto al sys.path para importaciones de backend
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dotenv import load_dotenv

load_dotenv(override=True)

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.groq_client import GroqClient
from backend.metrics import (
    detect_topic,
    get_knowledge_gaps,
    get_recent_interactions,
    get_session_stats,
    log_question,
)
from backend.orchestrator import ConversationalOrchestrator
from backend.rag_engine import RAGEngine

# Inicializar FastAPI
app = FastAPI(
    title="Flebitech API",
    description="API Educativa sobre Flebitis Química para Enfermería (laCardio & Universidad de La Sabana)",
    version="1.3.0"
)

# Habilitar CORS para integración web y widget embebible
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "FLEBITECH_CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Inicializar motores
kb_path = os.path.join(root_dir, "knowledge_base")
rag = RAGEngine(knowledge_base_path=kb_path)
groq = GroqClient()
orchestrator = ConversationalOrchestrator(rag_engine=rag, groq_client=groq)


# Modelos Pydantic
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

    class Config:
        extra = "forbid"

class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="web_session", min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    history: list[ChatMessage] | None = None

    class Config:
        extra = "forbid"


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    had_answer: bool
    topic: str
    latency_ms: float


# ----- ENDPOINTS -----

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Flebitech API v1.3",
        "institution": "laCardio & Universidad de La Sabana",
        "indexed_chunks": len(rag.chunks),
        "medications_count": len(rag.medications)
    }


@app.get("/api/health")
def health_check():
    """Endpoint de health check para Vercel y monitoreo."""
    return {
        "status": "healthy",
        "rag_chunks": len(rag.chunks),
        "medications": len(rag.medications),
        "groq_configured": groq.client is not None,
        "llm": groq.status()
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    if len(query) > 500:
        raise HTTPException(status_code=400, detail="La consulta es demasiado larga (máx. 500 caracteres).")

    # Utilizar el Orquestador Conversacional Pipeline
    history_items = (req.history or [])[-8:]
    history = [
        {"role": item.role, "content": item.content.strip()}
        for item in history_items
        if item.content.strip()
    ]
    response_text, sources, had_answer, latency = orchestrator.chat(original_query=query, history=history)

    # Clasificación temática
    topic = detect_topic(query)

    # Registro en métricas
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
        "¿Cuáles son los criterios de pH y osmolaridad críticos?",
        "¿Qué calibre de catéter debo elegir según el tratamiento?",
        "¿Cuál es el protocolo de antisepsia con Clorhexidina?"
    ]


@app.get("/api/metrics")
def get_metrics(session_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,64}", session_id):
        raise HTTPException(status_code=400, detail="session_id inválido")
    stats = get_session_stats(session_id)
    recent = get_recent_interactions(limit=10, session_id=session_id)
    gaps = get_knowledge_gaps(limit=10, session_id=session_id)
    return {
        "stats": stats,
        "recent": recent,
        "gaps": gaps
    }
