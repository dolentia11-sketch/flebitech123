# -*- coding: utf-8 -*-
"""Servidor local que replica el enrutamiento estático + API de Vercel.

Ejecutar con: uvicorn dev_server:app --reload --port 8000
"""

import os

from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

from api.index import app as api_app


PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
static_app = StaticFiles(directory=PUBLIC_DIR, html=True)


async def app(scope, receive, send):
    """Enruta /api al backend y el resto a la aplicación web estática."""
    if scope["type"] == "http" and scope.get("path", "").startswith("/api/"):
        await api_app(scope, receive, send)
        return
    try:
        await static_app(scope, receive, send)
    except HTTPException as exc:
        # StaticFiles se usa aquí como ASGI puro (sin el middleware de Starlette
        # que normalmente transforma esta excepción en una respuesta HTTP).
        response = PlainTextResponse("Not Found", status_code=exc.status_code)
        await response(scope, receive, send)
