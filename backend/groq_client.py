# -*- coding: utf-8 -*-
"""
Cliente de Integración con Groq API y Fallback Determinista para Flebitech.
"""

import os
import time
from typing import Tuple
from dotenv import load_dotenv

from backend.prompt_system import SYSTEM_PROMPT, FALLBACK_MESSAGE, build_user_prompt

# Cargar variables de entorno desde .env
load_dotenv()

class GroqClient:
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client = None
        
        if self.api_key and self.api_key.strip() and self.api_key != "tu_clave_groq_aqui":
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Aviso: No se pudo inicializar cliente Groq: {e}")
                self.client = None

    def ask(self, query: str, context: str, has_relevant_content: bool = True) -> Tuple[str, float]:
        start_time = time.time()
        
        # 1. Si no hay contenido relevante en la base, responder de inmediato con la regla de oro
        if not has_relevant_content or not context.strip():
            latency = (time.time() - start_time) * 1000
            return FALLBACK_MESSAGE, latency

        # 2. Si el cliente Groq está disponible y configurado
        if self.client is not None:
            try:
                user_msg = build_user_prompt(query, context)
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ],
                    temperature=0.1,
                    max_tokens=600,
                    top_p=0.9
                )
                response_text = completion.choices[0].message.content.strip()
                latency = (time.time() - start_time) * 1000
                return response_text, latency
            except Exception as e:
                print(f"Error llamando a Groq API ({e}). Usando motor determinista local de respaldo...")

        # 3. Motor local de respaldo determinista (si aún no se ha colocado la API key o falla la red)
        response_text = self._local_deterministic_response(query, context)
        latency = (time.time() - start_time) * 1000
        return response_text, latency

    def _local_deterministic_response(self, query: str, context: str) -> str:
        """Generador didáctico basado exclusivamente en el contexto recuperado."""
        sections = context.split("### [Fuente:")
        first_chunk = sections[1] if len(sections) > 1 else context
        
        lines = [line for line in first_chunk.strip().split("\n") if line.strip()]
        title = lines[0].split("]")[0] if "]" in lines[0] else "Flebitech Knowledge Base"
        body = "\n".join(lines[1:12]) if len(lines) > 1 else first_chunk
        
        return f"📚 **Resumen Clínico Basado en Flebitech ({title}):**\n\n{body}\n\n*Nota: Para habilitar respuestas generativas en lenguaje natural con ultra-velocidad, agrega tu GROQ_API_KEY gratuita en el archivo .env.*"
