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

FALLBACK_MODELS = [
    'openai/gpt-oss-120b',
    'qwen/qwen3.8-27b',
    'openai/gpt-oss-20b',
    'llama-3.3-70b-versatile'
]


class GroqClient:
    def __init__(self, api_key: str = None, model: str = None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
        self.client = None
        
        if self.api_key and self.api_key.strip() and self.api_key != "tu_clave_groq_aqui":
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key, timeout=15.0)
            except Exception as e:
                print(f"Aviso: No se pudo inicializar cliente Groq: {e}")
                self.client = None

    def ask(self, query: str, context: str, has_relevant_content: bool = True, history: list = None) -> Tuple[str, float]:
        start_time = time.time()
        
        # 1. Si no hay contenido relevante en la base, responder de inmediato con la regla de oro
        if not has_relevant_content or not context.strip():
            latency = (time.time() - start_time) * 1000
            return FALLBACK_MESSAGE, latency

        # 2. Si el cliente Groq está disponible y configurado
        if self.client is not None:
            user_msg = build_user_prompt(query, context)
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if history:
                for msg in history[-6:]:  # últimos 3 turnos
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_msg})

            # Probar el modelo configurado y luego alternativas si el modelo no existe
            models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]

            for mod in models_to_try:
                try:
                    completion = self.client.chat.completions.create(
                        model=mod,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1024,
                        top_p=0.9
                    )
                    response_text = completion.choices[0].message.content.strip()
                    latency = (time.time() - start_time) * 1000
                    self.model = mod
                    return response_text, latency
                except Exception as e:
                    error_msg = str(e).lower()
                    if "404" in error_msg or "model_not_found" in error_msg or "does not exist" in error_msg:
                        # Modelo no disponible, intentar siguiente en la lista
                        continue
                    elif "429" in error_msg or "503" in error_msg or "rate" in error_msg:
                        # Rate limit temporal: esperar y reintentar
                        time.sleep(1)
                        try:
                            completion = self.client.chat.completions.create(
                                model=mod,
                                messages=messages,
                                temperature=0.1,
                                max_tokens=1024,
                                top_p=0.9
                            )
                            response_text = completion.choices[0].message.content.strip()
                            latency = (time.time() - start_time) * 1000
                            return response_text, latency
                        except Exception:
                            continue
                    else:
                        print(f"Error llamando a Groq API ({e}). Usando motor determinista local de respaldo...")
                        break

        # 3. Motor local de respaldo determinista (si aún no se ha colocado la API key o falla la red)
        response_text = self._local_deterministic_response(query, context)
        latency = (time.time() - start_time) * 1000
        return response_text, latency

    def _local_deterministic_response(self, query: str, context: str) -> str:
        """Generador didáctico basado exclusivamente en el contexto recuperado."""
        content = context.strip()
        if len(content) > 2000:
            content = content[:1997] + "..."
            
        return f"💡 **Resumen Clínico Basado en Flebitech:**\n\n{content}\n\n*Nota: Para habilitar respuestas generativas en lenguaje natural con ultra-velocidad, agrega tu GROQ_API_KEY gratuita en el archivo .env.*"
