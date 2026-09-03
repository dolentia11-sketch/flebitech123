"""Pipeline conversacional de Flebitech con degradación segura."""

import time

from backend.groq_client import GroqClient
from backend.prompt_system import (
    FALLBACK_MESSAGE,
    ROUTER_SYSTEM_PROMPT,
    build_generation_prompt,
    build_router_prompt,
    deterministic_route,
    is_knowledge_gap,
    normalize_route,
)
from backend.rag_engine import RAGEngine
from backend.response_builder import build_local_response, clean_generated_response


class ConversationalOrchestrator:
    def __init__(self, rag_engine: RAGEngine, groq_client: GroqClient):
        self.rag = rag_engine
        self.groq = groq_client

    def chat(self, original_query: str, history: list = None) -> tuple[str, list[str], bool, float]:
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
        current_medications = self._match_medications(query)
        fallback_route = deterministic_route(
            query,
            history,
            known_medication=bool(current_medications),
        )

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

        # Una coincidencia contra medicamentos.json tiene prioridad sobre una
        # clasificación incierta del proveedor externo. Esto evita que fármacos
        # documentados terminen marcados como fuera de dominio.
        if current_medications and intent in {"out_of_domain", "clinical_query", "tematica_general"}:
            intent = fallback_route["intent"]
            depth = fallback_route["expected_depth"]
            rewritten_query = query

        # Si el usuario nombra un fármaco nuevo, ese nombre reemplaza la entidad
        # activa anterior. Solo una comparación explícita necesita conservar ambos.
        if current_medications:
            if intent != "comparacion":
                rewritten_query = query
            else:
                current_medications = current_medications[:2]

        # Resuelve pronombres y preguntas elípticas ("¿y la dilución?") usando
        # la última entidad farmacológica del historial, sin volcar respuestas
        # completas dentro de la búsqueda.
        active_medications = current_medications
        if route.get("is_continuation") and not active_medications and intent != "out_of_domain":
            active_medications = self._last_medications_in_history(history)
            if active_medications:
                if len(active_medications) > 1:
                    return "¿Sobre cuál de estos medicamentos deseas consultar?", [], True, self._latency(started)
                medication_names = " ".join(med.get("nombre", "") for med in active_medications)
                rewritten_query = f"{medication_names} {query}".strip()


        if intent == "greeting":
            response = "Hola. Soy Flebitech. Puedo orientarte sobre medicamentos documentados, flebitis química, terapia intravenosa, escalas clínicas y selección de accesos vasculares."
            return response, [], True, self._latency(started)

        if intent == "gratitude":
            return "Con gusto. Mantengo el contexto clínico de esta conversación para que puedas continuar desde el punto anterior.", [], True, self._latency(started)

        if intent == "capabilities":
            response = (
                "Puedo ayudarte a consultar los medicamentos incluidos en Flebitech —pH, osmolaridad, "
                "dilución, tiempo de infusión, vía y cuidados de enfermería—, además de escalas DIVA, "
                "INS y VHP, prevención de flebitis y selección de catéteres."
            )
            return response, [], True, self._latency(started)

        if intent == "out_of_domain":
            response = "La documentación de Flebitech no especifica esa información. Puedo ayudarte únicamente con flebitis química, terapia intravenosa, medicamentos y accesos vasculares documentados."
            return response, [], False, self._latency(started)

        try:
            if self._needs_medication_catalog(query) and hasattr(self.rag, "medication_catalog_context"):
                context, sources, has_match = self.rag.medication_catalog_context()
            elif active_medications and hasattr(self.rag, "medication_context"):
                context, sources, has_match = self.rag.medication_context(rewritten_query)
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

        if response and response.strip() and not is_knowledge_gap(response):
            local_res = build_local_response(query, context, sources, intent, search_query=rewritten_query)
            if self._is_factually_valid(response, local_res):
                final_response = clean_generated_response(response, sources)
            else:
                final_response = local_res
        else:
            final_response = build_local_response(query, context, sources, intent, search_query=rewritten_query)

        if not final_response.strip():
            final_response = FALLBACK_MESSAGE
            has_answer = False
        else:
            has_answer = True
        return final_response, sources, has_answer, self._latency(started)

    @staticmethod
    def _is_factually_valid(llm_response: str, local_response: str) -> bool:
        """Valida que los datos críticos en la respuesta LLM existan en el fallback local."""
        import re
        
        def extract_critical_numbers(text):
            # Extraer números críticos como pH, concentraciones. No extraemos "1", "2" que pueden ser listas.
            return set(re.findall(r"\b\d+\.\d+\b|\b\d{2,}\b", text))
            
        def extract_drugs(text):
            # Extract common drug suffixes but avoid generic Spanish words ending in 'ico' (like clínico, médico)
            return set(re.findall(r"\b[a-z]{4,}(?:micina|floxacina|azol|mab|vir|ciclina|statina|pril|sartan)\b", text.lower()))

        llm_nums = extract_critical_numbers(llm_response)
        local_nums = extract_critical_numbers(local_response)
        if llm_nums - local_nums:
            return False
            
        llm_drugs = extract_drugs(llm_response)
        local_drugs = extract_drugs(local_response)
        return not llm_drugs - local_drugs

    @staticmethod
    def _latency(started: float) -> float:
        return max(0.1, (time.perf_counter() - started) * 1000)

    def _match_medications(self, text: str) -> list:
        matcher = getattr(self.rag, "match_medications", None)
        if not callable(matcher):
            return []
        try:
            return matcher(text)
        except Exception:
            return []

    def _last_medications_in_history(self, history: list) -> list:
        unique_meds = []
        seen = set()
        for message in reversed((history or [])[-8:]):
            meds = self._match_medications(str(message.get("content", "")))
            for med in meds:
                name = med.get("nombre")
                if name not in seen:
                    seen.add(name)
                    unique_meds.append(med)
            if len(unique_meds) >= 2:
                break
        return unique_meds

    def _needs_medication_catalog(self, query: str) -> bool:
        """Detecta preguntas que necesitan revisar el conjunto farmacológico."""
        import re
        import unicodedata

        text = unicodedata.normalize("NFKD", query or "").encode("ascii", "ignore").decode().lower()
        
        # Si menciona 1 medicamento específicamente y no usa "como", probablemente no es un query de catálogo.
        meds = self._match_medications(text)
        if len(meds) == 1 and not re.search(r"\bcomo\b", text):
            return False

        # Si menciona explícitamente escalas o catéteres, no es un query de catálogo de medicamentos.
        if re.search(r"\b(?:diva|ins|vhp|cateter|midline|picc|elegibilidad)\b", text):
            return False

        mentions_catalog = bool(re.search(r"\b(?:medicamentos?|farmacos?|cuales?|cual)\b", text))
        if not mentions_catalog:
            return False

        list_request = bool(re.search(
            r"\b(?:lista|listado|catalogo|dame|muestra|mostrar|cuales hay|cuales son|"
            r"que medicamentos|que farmacos|que hay|cuantos medicamentos|cuantos farmacos|"
            r"tienen documentados|estan documentados|estan incluidos|disponibles|"
            r"cual no|cuales no)\b",
            text,
        ))
        collection_question = any(
            term in text
            for term in (
                "requieren", "via central", "via periferica", "mayor riesgo", "alto riesgo",
                "ph", "osmolar", "dilucion", "infusion", "vesicante", "irritante",
                "diluy", "ssn", "dad"
            )
        )
        return list_request or (collection_question and bool(re.search(r"\b(?:cuales?)\b", text)))
