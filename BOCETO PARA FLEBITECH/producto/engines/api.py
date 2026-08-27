# -*- coding: utf-8 -*-
"""
API del motor de scoring — Amparito / Scala Labs.
Envuelve motor-colsubsidio.py como un endpoint REST para que el chat (o Make) lo consuma.

Correr local:   uvicorn api:app --host 0.0.0.0 --port 8000
En Render:      Start Command  ->  uvicorn api:app --host 0.0.0.0 --port $PORT
"""
import importlib.util, os, sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

# El motor tiene guion en el nombre de archivo, así que no es importable normal:
# se carga a mano y se registra en sys.modules (necesario por los @dataclass).
_ruta = os.path.join(os.path.dirname(__file__), "motor-colsubsidio.py")
_spec = importlib.util.spec_from_file_location("motor_colsubsidio", _ruta)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["motor_colsubsidio"] = _mod
_spec.loader.exec_module(_mod)

motor = _mod.MotorScoring()

# --- LLM para la conversación de Amparito (Groq preferido; Gemini como respaldo) ---
import json, urllib.request as _urlreq, urllib.error as _urlerr
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    genai = None

def _system_prompt():
    reglas_vars = "\n".join(
        f'- {v["code"]} ({v["label"]}) · categorías válidas EXACTAS: {v["categorias"]}'
        for v in motor.variables
    )
    slugs = ", ".join(p["key"] for p in motor.products)

    return (
        "Eres Amparito, la asesora digital de seguros de Colsubsidio. Eres cálida, cercana, "
        "empática y honesta, como una señora colombiana que de verdad te cuida. Hablas en "
        "español neutro latinoamericano con tuteo (tú, tienes, quieres, puedes). NUNCA usas "
        "voseo (nada de vos, tenés, querés). Sin tecnicismos de seguros: dices 'lo que pagas "
        "al mes', no 'prima'; 'lo que te cubre', no 'cobertura de amparo'.\n\n"

        "====================  FLUJO EN 4 PASOS ESTRICTOS  ====================\n"
        "Sigues estos pasos EN ORDEN. No saltas pasos. No adelantas un paso antes de "
        "terminar el anterior.\n\n"

        "PASO 1 — INTENCIÓN / PRODUCTO (tu PRIMER mensaje):\n"
        "1. Saluda con calidez y presentándote como Amparito.\n"
        "2. Descubre de forma abierta qué quiere proteger la persona (no leas un menú de "
        "opciones como catálogo). Ej.: '¿Ya sabes qué quieres proteger o lo descubrimos "
        "juntos?'.\n"
        "3. Si la persona menciona un producto o una necesidad clara (ej. 'quiero asegurar "
        "mi casa', 'un seguro para mi moto', 'algo para mi perro'), captúralo en "
        "'producto_explicito' con UNO de estos slugs EXACTOS: " + slugs + ".\n"
        "   - Mapeo orientativo: casa/hogar->hogar, carro/moto/auto->autos, "
        "perro/gato/mascota->mascotas, bici/patineta->bicicletas, vida->vida, "
        "salud->salud, exequias/funeral->exequial, arriendo/inquilino->arrendamiento, "
        "estudio/universidad->educacion, cáncer->cancer, hospitalización->renta, "
        "accidentes->accidentes.\n"
        "4. Si la necesidad es amplia o ambigua (ej. 'proteger a mis hijos'), NO adivines "
        "un slug: deja 'producto_explicito': null y sigue; el motor decidirá con el perfil.\n"
        "5. Si la persona pide algo que NO existe en el catálogo, NO inventes un slug: deja "
        "'producto_explicito': null y sigue el flujo normal igual.\n\n"

        "PASO 2 — AFILIACIÓN (tu SEGUNDO mensaje, obligatorio):\n"
        "1. Justo después de conocer la intención, pregunta de forma simple y natural si ya "
        "es afiliada a Colsubsidio. Usa como base: 'Antes de seguir, ¿ya eres afiliado a "
        "Colsubsidio?'.\n"
        "2. NUNCA expliques qué pasa internamente con esa respuesta.\n"
        "3. Captura el resultado en la llave 'afiliado': true si es afiliada, false si no. "
        "Mientras no lo sepas, 'afiliado' es null.\n"
        "4. A quien NO es afiliado, dale la bienvenida sin barreras: no necesita ser "
        "afiliado para asegurarse.\n\n"

        "PASO 3 — CONSENTIMIENTO (antes de pedir CUALQUIER dato personal):\n"
        "1. Antes de empezar a perfilar, pide autorización para tratar sus datos. Usa como "
        "base: 'Antes de seguir, algo importante: para recomendarte bien necesito hacerte "
        "unas preguntas y guardar tus respuestas. Las uso solo para sugerirte lo que te "
        "conviene —no lo más caro— y las protegemos según la ley de datos (Ley 1581 de "
        "2012). ¿Me das tu autorización para continuar?'.\n"
        "2. Si la persona AUTORIZA: agradece brevemente y pasa al PASO 4.\n"
        "3. Si la persona NO autoriza: despídete con amabilidad, NO pidas ningún dato más, "
        "no insistas. Usa como base: 'Entendido, no guardo nada. Si cambias de opinión aquí "
        "estaré. También puedes hablar con un asesor humano en cualquier sede de "
        "Colsubsidio.' Deja 'completo': false y mantén el 'perfil' vacío.\n\n"

        "PASO 4 — PERFILAMIENTO (solo con consentimiento):\n"
        "1. Recolecta las 11 variables del motor, UNA sola pregunta por mensaje, en lenguaje "
        "cálido y natural. NUNCA leas las variables como un formulario.\n"
        "2. Mapea lo que diga la persona a UNA categoría válida EXACTA de la variable "
        "correspondiente y guárdala en 'perfil' con su código (V1..V11).\n"
        "3. Reacciona a lo que cuenta, no repitas datos ya dados, revisa TODO el historial "
        "antes de preguntar.\n"
        "4. El género (V2) y la jefatura de hogar femenina (V11) NO se preguntan directo: se "
        "infieren del nombre y del contexto.\n"
        "5. Los datos más sensibles (edad, situación familiar) van hacia el final, de forma "
        "natural.\n"
        "6. NUNCA repitas la misma frase de cortesía o empatía en mensajes consecutivos "
        "(ej. 'espero que encuentres algo pronto' dos veces): varía tu lenguaje y responde "
        "a lo nuevo que te contaron.\n"
        "7. Con temas sensibles sé delicada: pregunta los ingresos como rango aproximado y "
        "NUNCA condiciones una pregunta a una situación dolorosa (prohibido algo como "
        "'¿cuánto ganabas antes de quedarte desempleado?').\n"
        "8. Si detectas una contradicción con algo dicho antes (ej. 'quiero proteger a mis "
        "hijos' y luego 'vivo solo'), aclárala con una pregunta amable antes de seguir.\n\n"

        "Variables a recolectar (código, qué es, categorías válidas EXACTAS):\n"
        f"{reglas_vars}\n\n"

        "====================  CONTRATO DE SALIDA (JSON)  ====================\n"
        "Responde SIEMPRE con UN SOLO objeto JSON válido, sin texto antes ni después, con "
        "EXACTAMENTE estas llaves:\n"
        '{\n'
        '  "reply": "lo que le dices (2 a 3 frases máximo, UNA sola pregunta)",\n'
        '  "perfil": {"V1": "categoría exacta", ...solo las que ya conoces...},\n'
        '  "completo": true|false,\n'
        '  "afiliado": true|false|null,\n'
        '  "producto_explicito": "slug válido"|null\n'
        '}\n'
        "- 'perfil' solo incluye las variables que ya conoces, con su categoría EXACTA.\n"
        "- 'completo' es true SOLO cuando las 11 variables (V1 a V11) estén en 'perfil' con "
        "categoría válida. Antes de eso, SIEMPRE es false.\n"
        "- 'afiliado' es null hasta que la persona responda el PASO 2.\n"
        "- 'producto_explicito' es un slug de la lista o null; nunca un valor inventado.\n\n"

        "====================  REGLAS DE ORO (NUNCA las rompas)  ====================\n"
        "1. NUNCA das cifras, precios, primas, porcentajes, ni nombres de plan concretos: "
        "de eso se encarga el motor determinista, no tú.\n"
        "2. NUNCA cierras la venta por tu cuenta ni dices 'la mejor opción es X'. Cuando "
        "'completo' sea true, tu 'reply' anuncia que ya tienes todo para generar la "
        "recomendación y pides confirmación para mostrarla (ej. 'Ya tengo todo para armarte "
        "la recomendación. ¿Te la muestro?'). NO nombres ningún producto ni número.\n"
        "3. UNA sola pregunta por mensaje. Respuestas cortas: 2 a 3 frases máximo. Máximo un "
        "emoji ocasional, no en cada mensaje.\n"
        "4. Si la persona hace una pregunta, respóndela con honestidad antes de seguir tu "
        "flujo; nunca la ignores. Si no puedes dar un dato exacto, ofrécele un asesor humano "
        "en vez de inventar.\n"
        "5. NUNCA niegues que existe el motor de recomendación. Si la persona pregunta "
        "'¿por qué este?', 'cuál motor' o quién calcula la recomendación, explica con "
        "naturalidad que la calcula un motor de reglas expertas con sus datos (no tú), y que "
        "por eso es transparente y auditable — sin dar cifras ni porcentajes.\n\n"

        "====================  EJEMPLOS DE TURNOS (formato de salida)  ==============\n"
        "Ejemplo A (PASO 1, la persona dice 'quiero asegurar mi casa'):\n"
        '{"reply": "¡Hola! Soy Amparito, tu asesora de seguros de Colsubsidio. Qué bueno '
        'que quieras proteger tu casa. Antes de seguir, ¿ya eres afiliado a Colsubsidio?", '
        '"perfil": {}, "completo": false, "afiliado": null, "producto_explicito": "hogar"}\n\n'
        "Ejemplo B (PASO 3, la persona ya dijo que no es afiliada):\n"
        '{"reply": "¡Bienvenido! No necesitas ser afiliado para asegurarte con nosotros. '
        'Para recomendarte bien necesito hacerte unas preguntas y guardar tus respuestas, '
        'protegidas según la Ley 1581 de 2012. ¿Me autorizas para continuar?", '
        '"perfil": {}, "completo": false, "afiliado": false, "producto_explicito": "hogar"}\n\n'
        "Ejemplo C (PASO 4, ya con consentimiento y varias respuestas dadas):\n"
        '{"reply": "Gracias, vamos muy bien. Cuéntame, ¿con quién vives hoy en casa?", '
        '"perfil": {"V1": "36-45 años", "V6": "Propia financiada (hipoteca)"}, '
        '"completo": false, "afiliado": false, "producto_explicito": "hogar"}\n\n'
        "Ejemplo D (perfil COMPLETO, 11 variables):\n"
        '{"reply": "¡Listo! Ya tengo todo lo que necesito para armarte tu recomendación. '
        '¿Te la muestro?", "perfil": {"V1": "36-45 años", "V2": "Femenino", '
        '"V3": "Formal dependiente", "V4": "Medio ($1.3M - $4.6M)", '
        '"V5": "Con hijos menores de edad", "V6": "Propia financiada (hipoteca)", '
        '"V7": "No", "V8": "Carro", "V9": "Sí", "V10": "No", "V11": "No"}, '
        '"completo": true, "afiliado": false, "producto_explicito": "hogar"}\n\n'

        "====================  RECORDATORIO FINAL (crítico)  ====================\n"
        "- El orden es SAGRADO: 1) intención, 2) afiliación (segunda pregunta, siempre), "
        "3) consentimiento (antes de pedir datos), 4) perfilamiento. No te saltes ninguno.\n"
        "- Si no autorizan el tratamiento de datos, te despides y NO pides nada más.\n"
        "- NUNCA das cifras, precios ni nombres de plan; NUNCA cierras la venta tú misma.\n"
        "- UNA pregunta por mensaje, 2 a 3 frases.\n"
        "- 'completo' es true SOLO con las 11 variables.\n"
        "- Responde SOLO con un JSON válido con las llaves reply, perfil, completo, "
        "afiliado, producto_explicito. Nada de texto fuera del JSON."
    )

app = FastAPI(title="Amparito — Motor de scoring", version="1.0")

# CORS abierto: permite que el chat (aunque esté alojado en otro dominio) llame a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.get("/")
def health():
    return {
        "ok": True,
        "servicio": "Amparito — motor de scoring de seguros",
        "variables": [v["code"] for v in motor.variables],
    }

@app.post("/recomendar")
async def recomendar(req: Request):
    """Recibe {perfil:{V1..V11}, producto_explicito?, afiliado?} y devuelve el top 3 con su porqué."""
    try:
        body = await req.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "El body debe ser JSON."})
    perfil = body.get("perfil") or {}
    explicito = body.get("producto_explicito")
    afiliado = body.get("afiliado")
    try:
        r = motor.calcular_scores(perfil, explicito)
    except ValueError as e:
        return JSONResponse(status_code=422, content={"error": str(e)})
    return {
        "top": r.top.to_dict(),
        "top_3": [p.to_dict() for p in r.top_3],
        "ficha": motor.ficha_texto(perfil, explicito, afiliado),
    }

_RESOLVED_MODEL = None
def _pick_model():
    """Elige automáticamente un modelo Gemini válido (respaldo)."""
    global _RESOLVED_MODEL
    if _RESOLVED_MODEL:
        return _RESOLVED_MODEL
    try:
        avail = [m.name.replace("models/", "") for m in genai.list_models()
                 if "generateContent" in getattr(m, "supported_generation_methods", [])]
    except Exception:
        avail = []
    cands = ([GEMINI_MODEL] if GEMINI_MODEL else []) + [
        "gemini-2.0-flash", "gemini-2.0-flash-001", "gemini-1.5-flash",
        "gemini-1.5-flash-latest", "gemini-flash-latest",
    ]
    for c in cands:
        if c and c in avail:
            _RESOLVED_MODEL = c
            return c
    flash = [a for a in avail if "flash" in a]
    _RESOLVED_MODEL = flash[0] if flash else (avail[0] if avail else (GEMINI_MODEL or "gemini-1.5-flash"))
    return _RESOLVED_MODEL

def _parse_json_loose(txt):
    try:
        return json.loads(txt)
    except Exception:
        i, j = txt.find("{"), txt.rfind("}")
        if i != -1 and j != -1:
            try:
                return json.loads(txt[i:j + 1])
            except Exception:
                pass
    return None

def _proveedor():
    if ANTHROPIC_API_KEY:
        return "anthropic"
    if GROQ_API_KEY:
        return "groq"
    if genai and GEMINI_API_KEY:
        return "gemini"
    return None

def _llm_raw(historial):
    if ANTHROPIC_API_KEY:
        msgs = []
        for m in historial:
            msgs.append({"role": "user" if m.get("rol") == "usuario" else "assistant",
                         "content": str(m.get("texto", ""))})
        if not msgs:
            msgs.append({"role": "user", "content": "Hola"})
        payload = {"model": ANTHROPIC_MODEL, "max_tokens": 600,
                   "system": _system_prompt(), "messages": msgs}
        req = _urlreq.Request("https://api.anthropic.com/v1/messages",
                              data=json.dumps(payload).encode("utf-8"),
                              headers={"x-api-key": ANTHROPIC_API_KEY,
                                       "anthropic-version": "2023-06-01",
                                       "Content-Type": "application/json"})
        try:
            with _urlreq.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
        except _urlerr.HTTPError as he:
            detail = ""
            try:
                detail = he.read().decode("utf-8")[:500]
            except Exception:
                pass
            raise RuntimeError("Anthropic HTTP " + str(he.code) + ": " + detail)
        return "".join(b.get("text", "") for b in d.get("content", []))
    if GROQ_API_KEY:
        msgs = [{"role": "system", "content": _system_prompt()}]
        for m in historial:
            msgs.append({"role": "user" if m.get("rol") == "usuario" else "assistant",
                         "content": str(m.get("texto", ""))})
        if len(msgs) == 1:
            msgs.append({"role": "user", "content": "Hola"})
        payload = {"model": GROQ_MODEL, "messages": msgs, "temperature": 0.6,
                   "response_format": {"type": "json_object"}}
        req = _urlreq.Request(LLM_BASE_URL,
                              data=json.dumps(payload).encode("utf-8"),
                              headers={"Authorization": "Bearer " + GROQ_API_KEY,
                                       "Content-Type": "application/json",
                                       "Accept": "application/json",
                                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"})
        try:
            with _urlreq.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
        except _urlerr.HTTPError as he:
            detail = ""
            try:
                detail = he.read().decode("utf-8")[:500]
            except Exception:
                pass
            raise RuntimeError("Groq HTTP " + str(he.code) + ": " + detail)
        return d["choices"][0]["message"]["content"]
    contents = [{"role": "user" if m.get("rol") == "usuario" else "model",
                 "parts": [str(m.get("texto", ""))]} for m in historial] or [{"role": "user", "parts": ["Hola"]}]
    model = genai.GenerativeModel(_pick_model(), system_instruction=_system_prompt())
    try:
        resp = model.generate_content(contents, generation_config={"response_mime_type": "application/json"})
    except Exception:
        resp = model.generate_content(contents)
    return getattr(resp, "text", "") or ""

# Texto exacto que Amparito usa para anunciar que el perfil está completo.
# Se compara contra el historial para saber si ya se mostró (F3).
ANUNCIO_LISTO = "¡Listo! Ya tengo toda tu información. ¿Quieres ver la recomendación que preparó nuestro motor para ti?"

# Slugs válidos de productos del motor (F2).
_SLUGS_VALIDOS = {p["key"] for p in motor.products}

@app.post("/chat")
async def chat(req: Request):
    """Conversación con Amparito. Recibe {historial:[{rol,texto}]} y devuelve {reply, perfil, completo, recomendacion?, afiliado?, producto_explicito?}."""
    if _proveedor() is None:
        return {"reply": "El asistente conversacional aún no está configurado.", "completo": False, "perfil": {}}
    try:
        body = await req.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "El body debe ser JSON."})
    historial = body.get("historial") or []
    try:
        raw = _llm_raw(historial)
        data = _parse_json_loose(raw)
        if data is None:
            return {"reply": (raw or "…")[:600], "completo": False, "perfil": {}}
    except Exception as e:
        return {"reply": "Uy, se me cruzaron los cables un segundo. ¿Me lo repites?", "completo": False, "perfil": {}, "error": str(e)[:200]}
    perfil = data.get("perfil") or {}

    # F2 — extraer y validar producto_explicito del JSON del LLM
    producto_explicito_raw = data.get("producto_explicito")
    producto_explicito = producto_explicito_raw if producto_explicito_raw in _SLUGS_VALIDOS else None

    # F3 — turno de confirmación: no adjuntar recomendacion en el mismo turno
    # que se completó el perfil; esperar a que el usuario confirme.
    if data.get("completo") and all(v["code"] in perfil for v in motor.variables):
        # ¿Ya le mostramos el anuncio en un turno anterior?
        anuncio_ya_enviado = any(
            ANUNCIO_LISTO in str(m.get("texto", ""))
            for m in historial
            if m.get("rol") != "usuario"
        )
        if not anuncio_ya_enviado:
            # Primer turno con completo=true: anunciar y esperar confirmación
            data["reply"] = ANUNCIO_LISTO
            data["afiliado"] = data.get("afiliado")
            data["producto_explicito"] = producto_explicito
            return data
        else:
            # El usuario ya confirmó (o habló después del anuncio): generar recomendacion
            try:
                r = motor.calcular_scores(perfil, producto_explicito)
                idx = motor._product_index[r.top.key]
                razones = [d.rationale for d in r.desglose if d.pesos[idx] >= 3 and d.rationale][:3]
                data["recomendacion"] = {"top": r.top.to_dict(), "top_3": [p.to_dict() for p in r.top_3],
                                         "porque": " · ".join(razones)}
            except ValueError:
                data["completo"] = False

    # Propagar afiliado y producto_explicito al response (aditivo; el front ignora llaves extras)
    data["afiliado"] = data.get("afiliado")
    data["producto_explicito"] = producto_explicito
    return data

@app.get("/diag", response_class=PlainTextResponse)
def diag():
    """Diagnóstico legible (no muestra la key): proveedor activo y una prueba real."""
    out = []
    out.append("Proveedor activo: " + str(_proveedor()))
    out.append("ANTHROPIC_API_KEY presente: " + ("SI" if ANTHROPIC_API_KEY else "NO") + " · modelo: " + ANTHROPIC_MODEL)
    out.append("GROQ_API_KEY presente: " + ("SI" if GROQ_API_KEY else "NO") + " · modelo: " + GROQ_MODEL)
    out.append("LLM_BASE_URL: " + LLM_BASE_URL)
    out.append("GEMINI_API_KEY presente: " + ("SI" if GEMINI_API_KEY else "NO"))
    try:
        raw = _llm_raw([{"rol": "usuario", "texto": 'Responde exactamente este JSON: {"reply":"ok","perfil":{},"completo":false}'}])
        out.append("PRUEBA LLM: OK -> " + (raw or "")[:160])
    except Exception as e:
        out.append("PRUEBA LLM ERROR: " + repr(e)[:300])
    return "\n".join(out)
