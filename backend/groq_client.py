"""Cliente Groq con degradación controlada y diagnóstico seguro.

El cliente no decide qué texto mostrar al usuario. Cuando el proveedor falla,
devuelve una señal inequívoca para que el orquestador use el RAG local y no un
fallback genérico que parezca una respuesta vacía.
"""

import json
import os
import time
from typing import Any

from dotenv import load_dotenv

from backend.prompt_system import FALLBACK_MESSAGE

load_dotenv(override=True)

DEFAULT_MODEL = "openai/gpt-oss-20b"


class GroqClient:
    def __init__(self, api_key: str = None, model: str = None):
        load_dotenv(override=True)
        self._explicit_api_key = api_key is not None
        self.api_key = api_key if api_key is not None else os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        self.client = None
        self.last_error = ""
        self.last_call_ok = False
        self.last_json_ok = False
        self.cooldown_until = 0.0
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.strip() in {"", "tu_clave_groq_aqui"}:
            self.client = None
            return
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key, timeout=12.0)
        except Exception as exc:
            self.client = None
            self.last_error = f"No se pudo inicializar Groq: {type(exc).__name__}"

    def ensure_client(self):
        if self.client is not None or self._explicit_api_key:
            return
        load_dotenv(override=True)
        new_key = os.getenv("GROQ_API_KEY", "")
        if new_key and new_key != "tu_clave_groq_aqui":
            self.api_key = new_key
            self.model = os.getenv("GROQ_MODEL", self.model)
            self._init_client()

    @staticmethod
    def _is_reasoning_model(model: str) -> bool:
        return model.startswith("openai/gpt-oss")

    def _request_kwargs(self, model: str, messages: list, *, json_mode: bool, max_tokens: int) -> dict:
        # GPT-OSS puede gastar el presupuesto en razonamiento; max_tokens deja
        # la salida visible vacía. max_completion_tokens evita ese comportamiento.
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": 0.0 if json_mode else 0.2,
            "top_p": 0.9,
        }
        if self._is_reasoning_model(model):
            kwargs["max_completion_tokens"] = max_tokens
            kwargs["reasoning_effort"] = "low"
        else:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs

    def _mark_failure(self, exc: Exception):
        message = str(exc).lower()
        self.last_call_ok = False
        self.last_json_ok = False
        if "rate" in message or "429" in message or "quota" in message:
            self.last_error = "Límite de uso del proveedor LLM"
            self.cooldown_until = time.time() + 45
        elif "model" in message and ("not found" in message or "404" in message):
            self.last_error = "Modelo Groq no disponible"
            self.cooldown_until = time.time() + 300
        else:
            self.last_error = f"Error del proveedor LLM: {type(exc).__name__}"
            self.cooldown_until = time.time() + 30

    def _can_call(self) -> bool:
        self.ensure_client()
        return self.client is not None and time.time() >= self.cooldown_until

    def generate_json(self, messages: list) -> dict[str, Any]:
        """Genera JSON una vez; ante fallo devuelve un objeto neutro y trazable."""
        self.last_json_ok = False
        if not self._can_call():
            return {}
        try:
            completion = self.client.chat.completions.create(
                **self._request_kwargs(self.model, messages, json_mode=True, max_tokens=1200)
            )
            content = (completion.choices[0].message.content or "").strip()
            if not content:
                raise ValueError("El proveedor devolvió JSON vacío")
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("El proveedor devolvió JSON no estructurado")
            self.last_call_ok = True
            self.last_json_ok = True
            self.last_error = ""
            return result
        except Exception as exc:
            self._mark_failure(exc)
            return {}

    def generate_chat(self, messages: list) -> str:
        """Genera texto una vez y devuelve cadena vacía si debe activar el RAG local."""
        self.last_call_ok = False
        if not self._can_call():
            return ""
        try:
            completion = self.client.chat.completions.create(
                **self._request_kwargs(self.model, messages, json_mode=False, max_tokens=2400)
            )
            content = (completion.choices[0].message.content or "").strip()
            if not content:
                raise ValueError("El proveedor devolvió respuesta vacía")
            self.last_call_ok = True
            self.last_error = ""
            return content
        except Exception as exc:
            self._mark_failure(exc)
            return ""

    def status(self) -> dict:
        return {
            "configured": bool(self.client),
            "model": self.model,
            "cooldown": time.time() < self.cooldown_until,
            "last_error": self.last_error,
        }

    def ask(self, query: str, context: str, has_relevant_content: bool = True, history: list = None) -> tuple[str, float]:
        """Compatibilidad con la API anterior; el orquestador es el flujo principal."""
        start_time = time.time()
        return FALLBACK_MESSAGE, (time.time() - start_time) * 1000
