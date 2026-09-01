# -*- coding: utf-8 -*-
"""
Cliente de Integración con Groq API y Fallback Determinista para Flebitech.
"""

import os
import time
import json
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

from backend.prompt_system import FALLBACK_MESSAGE

# Cargar variables de entorno desde .env
load_dotenv(override=True)

FALLBACK_MODELS = [
    'llama-3.3-70b-versatile',
    'mixtral-8x7b-32768',
    'gemma2-9b-it'
]

class GroqClient:
    def __init__(self, api_key: str = None, model: str = None):
        load_dotenv(override=True)
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
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

    def ensure_client(self):
        if self.client is None:
            load_dotenv(override=True)
            new_key = os.getenv("GROQ_API_KEY", "")
            if new_key and new_key != "tu_clave_groq_aqui":
                self.api_key = new_key
                self.model = os.getenv("GROQ_MODEL", self.model)
                self._init_client()

    def generate_json(self, messages: list) -> Dict[str, Any]:
        """Hace una llamada a Groq forzando el formato JSON."""
        self.ensure_client()
        if not self.client:
            return {"intent": "clinical_query", "is_continuation": False, "rewritten_query": "", "expected_depth": "nivel_2"}
        
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        
        for mod in models_to_try:
            try:
                completion = self.client.chat.completions.create(
                    model=mod,
                    messages=messages,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                    max_tokens=512
                )
                response_text = completion.choices[0].message.content.strip()
                return json.loads(response_text)
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "503" in error_msg or "rate" in error_msg:
                    time.sleep(1)
                    try:
                        completion = self.client.chat.completions.create(
                            model=mod,
                            messages=messages,
                            temperature=0.0,
                            response_format={"type": "json_object"},
                            max_tokens=512
                        )
                        response_text = completion.choices[0].message.content.strip()
                        return json.loads(response_text)
                    except Exception:
                        continue
                else:
                    continue
                    
        return {"intent": "clinical_query", "is_continuation": False, "rewritten_query": "", "expected_depth": "nivel_2"}

    def generate_chat(self, messages: list) -> str:
        """Hace una llamada a Groq para generar texto."""
        self.ensure_client()
        if not self.client:
            return FALLBACK_MESSAGE
            
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
                return completion.choices[0].message.content.strip()
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "503" in error_msg or "rate" in error_msg:
                    time.sleep(1)
                    try:
                        completion = self.client.chat.completions.create(
                            model=mod,
                            messages=messages,
                            temperature=0.1,
                            max_tokens=2048,
                            top_p=0.9
                        )
                        return completion.choices[0].message.content.strip()
                    except Exception:
                        continue
                else:
                    continue
        return FALLBACK_MESSAGE

    def ask(self, query: str, context: str, has_relevant_content: bool = True, history: list = None) -> Tuple[str, float]:
        """Método legacy por compatibilidad. No se debería usar con el nuevo orquestador."""
        start_time = time.time()
        latency = (time.time() - start_time) * 1000
        return FALLBACK_MESSAGE, latency
