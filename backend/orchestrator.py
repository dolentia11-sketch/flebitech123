# -*- coding: utf-8 -*-
"""Pipeline conversacional de Flebitech con degradación segura."""

import time
from typing import List, Tuple

from backend.groq_client import GroqClient
from backend.prompt_system import (
    FALLBACK_MESSAGE,
    ROUTER_SYSTEM_PROMPT,
    build_generation_prompt,
    build_router_prompt,
    deterministic_route,
    normalize_route,
)
from backend.rag_engine import RAGEngine
from backend.response_builder import build_local_response, clean_generated_response


class ConversationalOrchestrator:
    def __init__(self, rag_engine: RAGEngine, groq_client: GroqClient):
        self.rag = rag_engine
        self.groq = groq_client

    def chat(self, original_query: str, history: list = None) -> Tuple[str, List[str], bool, float]:
        """Ejecuta router, rewrite, RAG, generación y validación local.

        La respuesta nunca depende exclusivamente del LLM: si la API falla, el
        contexto recuperado se presenta con formato didáctico y fuentes reales.
        """
        started = time.perf_counter()
        query = (original_query or "").strip()
        # Algunos clientes agregan el turno actual al historial antes de llamar
        # al API. Excluirlo evita que desplace el turno previo que contiene la
        # entidad clínica necesaria para reescribir continuaciones como
        # "¿Y la dilución?".
        history = list(history or [])
        if history:
            last = history[-1]
            if (
                isinstance(last, dict)
                and last.get("role") == "user"
                and str(last.get("content", "")).strip() == query
            ):
                history = history[:-1]
        fallback_route = deterministic_route(query, history)

        router_result = {}
        try:
            router_result = self.groq.generate_json([
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": build_router_prompt(query, history)},
            ])
        except Exception:
            router_result = {}

        # Si la llamada falló, el cliente marca last_json_ok=False y no se usa el
        # JSON neutro como si fuera una clasificación válida.
        if getattr(self.groq, "last_json_ok", True):
            route = normalize_route(router_result, fallback_route)
        else:
            route = fallback_route

        intent = route["intent"]
        depth = route["expected_depth"]
        rewritten_query = route["rewritten_query"] or query

        if intent == "greeting":
            response = build_local_response(query, "### [Fuente: protocolo_basico.md | Bienvenida]\nFlebitech", ["protocolo_basico.md"], intent)
            return response, ["protocolo_basico.md"], True, self._latency(started)

        if intent == "out_of_domain":
            response = "La documentación de Flebitech no especifica esa información. Puedo ayudarte únicamente con flebitis química, terapia intravenosa, medicamentos y accesos vasculares documentados."
            return response, [], False, self._latency(started)

        try:
            asks_medication_list = "medicamentos" in query.lower() and any(
                word in query.lower() for word in ("dame", "lista", "cuáles", "cuales", "todos")
            )
            if asks_medication_list and hasattr(self.rag, "medication_catalog_context"):
                context, sources, has_match = self.rag.medication_catalog_context()
            else:
                top_k = 8 if depth in {"nivel_3", "nivel_4", "nivel_5"} else 5
                context, sources, has_match = self.rag.search(rewritten_query, top_k=top_k)
        except Exception:
            context, sources, has_match = "", [], False

        if not has_match:
            return FALLBACK_MESSAGE, [], False, self._latency(started)

        response = ""
        try:
            response = self.groq.generate_chat(build_generation_prompt(
                query=query,
                context=context,
                expected_depth=depth,
                history=history,
            ))
        except Exception:
            response = ""

        if response and response.strip():
            final_response = clean_generated_response(response, sources)
        else:
            final_response = build_local_response(query, context, sources, intent, search_query=rewritten_query)

        if not final_response.strip():
            final_response = FALLBACK_MESSAGE
            has_answer = False
        else:
            has_answer = True
        return final_response, sources, has_answer, self._latency(started)

    @staticmethod
    def _latency(started: float) -> float:
        return max(0.1, (time.perf_counter() - started) * 1000)
