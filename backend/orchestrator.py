# -*- coding: utf-8 -*-
"""
Orquestador Conversacional de Flebitech.
Implementa el pipeline: Router -> Rewrite -> RAG -> Context Ranking -> Generation -> Validation.
"""

import time
from typing import Tuple, List

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.prompt_system import (
    ROUTER_SYSTEM_PROMPT, 
    build_router_prompt, 
    build_generation_prompt,
    build_validator_prompt,
    FALLBACK_MESSAGE
)

class ConversationalOrchestrator:
    def __init__(self, rag_engine: RAGEngine, groq_client: GroqClient):
        self.rag = rag_engine
        self.groq = groq_client

    def chat(self, original_query: str, history: list = None) -> Tuple[str, List[str], bool, float]:
        """
        Ejecuta el pipeline conversacional completo.
        Retorna: (Respuesta, Fuentes, Tuvo_Respuesta, Latencia_ms)
        """
        start_time = time.time()
        
        # PASO 1: Router & Query Rewriter & Depth Decision
        router_messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": build_router_prompt(original_query, history)}
        ]
        
        router_result = self.groq.generate_json(router_messages)
        intent = router_result.get("intent", "clinical_query")
        rewritten_query = router_result.get("rewritten_query", original_query)
        expected_depth = router_result.get("expected_depth", "nivel_2")
        
        # Fallback si no generó rewritten_query
        if not rewritten_query or rewritten_query.strip() == "":
            rewritten_query = original_query

        # PASO 2 & 3: Recuperación Híbrida (RAG) & Context Ranking
        has_match = False
        context = ""
        sources = []
        
        if intent == "out_of_domain":
            latency = (time.time() - start_time) * 1000
            msg = "Lo siento, como asistente clínico-educativo de Flebitech, solo puedo responder preguntas relacionadas con accesos venosos, terapia intravenosa, medicamentos y protocolos institucionales."
            return msg, [], True, latency
            
        if intent != "greeting":
            # Usar un top_k más alto para consultas complejas o completas
            top_k = 8 if expected_depth in ["nivel_3", "nivel_5"] else 5
            context, sources, has_match = self.rag.search(rewritten_query, top_k=top_k)
            
        # Si es un saludo, no necesitamos contexto
        if intent == "greeting":
            has_match = True
            
        if not has_match and intent != "greeting":
            latency = (time.time() - start_time) * 1000
            return FALLBACK_MESSAGE, [], False, latency
            
        # PASO 4: Generación de Respuesta
        generation_messages = build_generation_prompt(
            query=original_query, # Se usa la original para la respuesta natural
            context=context,
            expected_depth=expected_depth,
            history=history
        )
        
        generated_response = self.groq.generate_chat(generation_messages)
        
        # PASO 5: Validación de la Respuesta
        validator_messages = build_validator_prompt(generated_response)
        validator_result = self.groq.generate_json(validator_messages)
        final_response = validator_result.get("refined_response", generated_response)
        
        # Si el validador falló o retornó vacío, nos quedamos con la original
        if not final_response or final_response.strip() == "":
            final_response = generated_response
        
        latency = (time.time() - start_time) * 1000
        return final_response, sources, True, latency
