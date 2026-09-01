# -*- coding: utf-8 -*-
"""
Cliente de Integración con Groq API y Fallback Determinista para Flebitech.
"""

import os
import time
from typing import Tuple
from dotenv import load_dotenv

from backend.prompt_system import SYSTEM_PROMPT, FALLBACK_MESSAGE, build_user_prompt_with_history

# Cargar variables de entorno desde .env
load_dotenv(override=True)

FALLBACK_MODELS = [
    'openai/gpt-oss-120b',
    'qwen/qwen3.8-27b',
    'openai/gpt-oss-20b',
    'llama-3.3-70b-versatile'
]


class GroqClient:
    def __init__(self, api_key: str = None, model: str = None):
        load_dotenv(override=True)
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
        self.client = None
        self._init_client()

    def _init_client(self):
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

        # Re-intentar inicializar si se cargó la key después
        if self.client is None:
            load_dotenv(override=True)
            new_key = os.getenv("GROQ_API_KEY", "")
            if new_key and new_key != "tu_clave_groq_aqui":
                self.api_key = new_key
                self.model = os.getenv("GROQ_MODEL", self.model)
                self._init_client()

        # 2. Si el cliente Groq está disponible y configurado
        if self.client is not None:
            user_msg = build_user_prompt_with_history(query, context, history)
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if history:
                for msg in history[-6:]:  # últimos 3 turnos
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            messages.append({"role": "user", "content": user_msg})

            models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]

            for mod in models_to_try:
                try:
                    completion = self.client.chat.completions.create(
                        model=mod,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=2048,
                        top_p=0.9
                    )
                    response_text = completion.choices[0].message.content.strip()
                    latency = (time.time() - start_time) * 1000
                    self.model = mod
                    return response_text, latency
                except Exception as e:
                    error_msg = str(e).lower()
                    if "404" in error_msg or "model_not_found" in error_msg or "does not exist" in error_msg:
                        continue
                    elif "429" in error_msg or "503" in error_msg or "rate" in error_msg:
                        time.sleep(1)
                        try:
                            completion = self.client.chat.completions.create(
                                model=mod,
                                messages=messages,
                                temperature=0.1,
                                max_tokens=2048,
                                top_p=0.9
                            )
                            response_text = completion.choices[0].message.content.strip()
                            latency = (time.time() - start_time) * 1000
                            return response_text, latency
                        except Exception:
                            continue
                    else:
                        print(f"Aviso Groq API ({e}). Usando motor estructurado de respaldo...")
                        break

        # 3. Motor local de respaldo estructurado completo
        response_text = self._local_deterministic_response(query, context)
        latency = (time.time() - start_time) * 1000
        return response_text, latency

    def _local_deterministic_response(self, query: str, context: str) -> str:
        """Generador didáctico estructurado basado exclusivamente en el contexto recuperado."""
        q_lower = query.lower()
        chunks = context.split("### [Fuente:")
        first_chunk = chunks[1] if len(chunks) > 1 else context
        lines = [line.strip() for line in first_chunk.strip().split("\n") if line.strip()]

        # Extraer fuente
        source_title = lines[0].split("]")[0].strip() if len(lines) > 0 and "]" in lines[0] else "Material institucional de Flebitech"

        # Si el usuario pregunta expresamente por un único atributo puntual
        if any(k in q_lower for k in ['solo ph', 'cual es el ph', 'que ph tiene', 'valor de ph']):
            for line in lines[1:]:
                if 'ph:' in line.lower() or 'ph ' in line.lower():
                    return f"- **pH:** {line.replace('- pH:', '').strip()}\n\n*Fuente: {source_title}*"

        # Fallback estructurado completo (entrega la tabla, los pasos y los criterios íntegros)
        clean_lines = [l for l in lines[1:] if not l.startswith("### [Fuente:")]
        summary = "\n".join(clean_lines).strip() if clean_lines else first_chunk.strip()
        return f"{summary}\n\n*Fuente: {source_title}*"
