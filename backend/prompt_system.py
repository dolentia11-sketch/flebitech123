# -*- coding: utf-8 -*-
"""Prompts, routing y reglas de estilo del motor conversacional."""

import re
import unicodedata

FALLBACK_MESSAGE = "La documentación de Flebitech permite establecer algunos parámetros clínicos, pero no especifica la información exacta solicitada."

VALID_INTENTS = {
    "greeting", "dato_puntual", "explicacion", "guia_completa", "profundizacion",
    "comparacion", "criterios", "conducta", "algoritmo", "medicamento", "cateter",
    "tematica_general", "clinical_query", "capabilities", "gratitude", "out_of_domain"
}
VALID_DEPTHS = {"nivel_1", "nivel_2", "nivel_3", "nivel_4", "nivel_5"}


def _plain(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()


def deterministic_route(query: str, history: list = None, known_medication: bool = False) -> dict:
    """Clasificación de respaldo rápida y sin red.

    Es deliberadamente conservadora: el LLM puede mejorar la clasificación cuando está
    disponible, pero el producto sigue siendo útil con la API caída, sin clave o con
    límites de cuota agotados.
    """
    raw = (query or "").strip()
    text = _plain(raw)
    words = re.findall(r"[a-z0-9]+", text)
    clinical_terms = (
        "flebit", "cateter", "venos", "vena", "diva", "ins", "vhp", "vip", "puncion",
        "calibre", "gauge", "osmolar", "tonic", "ph", "diluc", "infus", "medicament",
        "farmac", "vancomicina", "amiodarona", "kcl", "potasio", "ceftriaxona", "npt",
        "nutricion parenteral", "clorhexidina", "antiseps", "midline", "picc", "cvc",
        "protocolo", "endotel", "extravas", "tromb", "paciente", "enfermer", "grado",
        "cordon", "palpable", "eritema", "edema", "dolor", "drenaje", "purulent",
        "punto", "adult", "pediatr", "neonat", "elegib", "conducta", "cuidad"
    )
    is_clinical = known_medication or any(term in text for term in clinical_terms)
    is_greeting = bool(re.fullmatch(r"(?:hola|buenas?|buenos dias|buenas tardes|buenas noches|hey)[!. ]*", text))
    is_gratitude = bool(re.fullmatch(r"(?:gracias|muchas gracias|perfecto|listo|entendido|muy bien)[!. ]*", text))
    asks_capabilities = bool(re.search(
        r"\b(?:que|cuales)\s+(?:puedes|sabes)\s+(?:hacer|responder)|"
        r"\b(?:en que|sobre que)\s+(?:me )?puedes ayudar\b",
        text,
    ))

    previous = " ".join(
        str(m.get("content", "")) for m in (history or [])[-2:] if m.get("role") in {"user", "assistant"}
    )
    explicit_out_of_domain = any(x in text for x in ("capital de", "precio", "pasaje", "restaurante", "futbol", "fútbol", "clima", "acciones de bolsa"))
    continuation = bool(history) and (
        text.startswith(("y ", "y?", "y en", "y la", "y el", "y si", "e "))
        or any(x in text for x in ("amplia", "amplia", "profundiza", "como se interpreta", "cual elegir", "qué grado", "que grado"))
        or bool(re.search(r"\b(su|sus|eso|esa|ese|aquello)\b", text))
        or ("grado" in text and not any(scale in text for scale in ("ins", "vhp", "vip")))
        or ("elegib" in text and not any(device in text for device in ("cateter", "midline", "picc", "cvc")))
        or (not is_clinical and not explicit_out_of_domain)
    )

    if is_greeting:
        intent, depth = "greeting", "nivel_1"
    elif is_gratitude:
        intent, depth = "gratitude", "nivel_1"
    elif asks_capabilities:
        intent, depth = "capabilities", "nivel_1"
    elif (not is_clinical and not previous) or explicit_out_of_domain:
        intent, depth = "out_of_domain", "nivel_1"
    elif any(x in text for x in ("completa", "completo", "toda la", "todo sobre", "tabla completa", "todos los", "todas las")):
        intent, depth = "guia_completa", "nivel_3"
    elif any(x in text for x in ("amplia", "amplia", "profundiza", "detalle", "mas informacion", "más información")):
        intent, depth = "profundizacion", "nivel_4"
    elif any(x in text for x in ("compara", "comparar", "diferencia", "versus", " vs ")):
        intent, depth = "comparacion", "nivel_5"
    elif any(x in text for x in ("criterio", "criterios", "elegib", "cuando usar", "cuándo usar", "indicacion", "indicación")):
        intent, depth = "criterios", "nivel_3"
    elif any(x in text for x in ("que hago", "qué hago", "conducta", "accion", "acción", "manejo", "actuar")):
        intent, depth = "conducta", "nivel_5"
    elif "algoritmo" in text or "paso a paso" in text:
        intent, depth = "algoritmo", "nivel_3"
    elif any(x in text for x in (
        "ph de", "osmolaridad de", "dilucion", "dilución", "diluyente",
        "cuanto tiempo", "cuánto tiempo", "tiempo de infusion", "via recomendada",
        "riesgo de flebitis", "cuidados de enfermeria",
    )):
        intent, depth = "dato_puntual", "nivel_1"
    elif known_medication or any(x in text for x in ("medicamento", "farmaco", "fármaco", "vancomicina", "amiodarona", "ceftriaxona", "potasio", "kcl")):
        intent, depth = "medicamento", "nivel_2"
    elif len(words) == 1 and is_clinical:
        intent, depth = "tematica_general", "nivel_2"
    elif "cateter" in text or "catéter" in raw.lower() or any(x in text for x in ("midline", "picc", "cvc", "acceso vascular")):
        intent, depth = "cateter", "nivel_2"
    elif any(x in text for x in ("que es", "qué es", "explica", "explícame", "definicion", "definición", "como se", "cómo se")):
        intent, depth = "explicacion", "nivel_2"
    else:
        intent, depth = "clinical_query", "nivel_2"

    rewritten = raw
    if continuation and previous:
        rewritten = f"{previous} {raw}"[-900:]

    return {
        "intent": intent,
        "is_continuation": continuation,
        "rewritten_query": rewritten,
        "expected_depth": depth,
    }


def normalize_route(candidate: dict, fallback: dict) -> dict:
    """Valida la salida del router para que un JSON defectuoso no rompa el turno."""
    if not isinstance(candidate, dict):
        return fallback
    route = dict(fallback)
    if candidate.get("intent") in VALID_INTENTS:
        route["intent"] = candidate["intent"]
    if candidate.get("expected_depth") in VALID_DEPTHS:
        route["expected_depth"] = candidate["expected_depth"]
    if isinstance(candidate.get("is_continuation"), bool):
        route["is_continuation"] = candidate["is_continuation"]
    if isinstance(candidate.get("rewritten_query"), str) and candidate["rewritten_query"].strip():
        route["rewritten_query"] = candidate["rewritten_query"].strip()[:1000]
    return route

# =======================================================================
# 1. ROUTER & QUERY REWRITER PROMPT
# =======================================================================
ROUTER_SYSTEM_PROMPT = """Eres el orquestador cognitivo de Flebitech.
Tu tarea es analizar la consulta del usuario en el contexto del historial y determinar la intención y la profundidad, además de reescribir la consulta para el motor RAG.

REGLAS:
1. "intent": Clasifica la intención principal de la consulta. Opciones:
   - "greeting": El usuario solo saluda (ej. "hola").
   - "dato_puntual": Pregunta por un dato específico (ej. "pH de vancomicina").
   - "explicacion": Solicita una explicación breve (ej. "Explícame DIVA").
   - "guia_completa": Pide una escala completa o información detallada (ej. "Escala INS completa").
   - "profundizacion": Pide ampliar una respuesta previa (ej. "Amplía el grado 2").
   - "comparacion": Está comparando conceptos.
   - "criterios": Solicita criterios de elegibilidad o evaluación.
   - "conducta": Solicita una conducta clínica.
   - "algoritmo": Solicita un algoritmo de decisión.
   - "medicamento": Solicita información sobre un medicamento (ej. "vancomicina").
   - "cateter": Solicita información sobre un catéter o acceso vascular.
   - "tematica_general": Escribe una sola palabra (ej. "catéter", "flebitis").
   - "clinical_query": Cualquier otra consulta clínica genérica.
   - "capabilities": Pregunta qué puede hacer o qué temas maneja Flebitech.
   - "gratitude": Agradecimiento o confirmación breve sin una nueva pregunta clínica.
   - "out_of_domain": El usuario pregunta algo que no tiene nada que ver con accesos venosos o medicamentos.

2. "is_continuation": true si la pregunta requiere el historial para entenderse (ej. "¿y en adulto?", "amplía", "¿cuál elegiría?"). false si es una pregunta autocontenida.

3. "rewritten_query": Reescribe la consulta para la búsqueda documental (RAG). 
   - Integra las referencias del historial si 'is_continuation' es true. Ej: si hablaban de "escala INS" y dice "grado 2", reescribe como "escala INS grado 2".
   - Si es un término amplio ("catéter", "vancomicina"), déjalo igual pero añade palabras clave relevantes si la intención lo exige.
   - No respondas a la pregunta, solo reformúlala en una frase útil para buscar en una base de datos.

4. "expected_depth": Asigna el nivel de profundidad de 1 a 5:
   - "nivel_1": Dato puntual (ej. "pH", "significado").
   - "nivel_2": Explicación breve (ej. "¿qué es DIVA?").
   - "nivel_3": Consulta completa (toda la información de la escala/documento).
   - "nivel_4": Profundización (ampliar un aspecto específico).
   - "nivel_5": Análisis clínico-educativo (requiere integrar varios documentos).

Genera ÚNICAMENTE un JSON válido:
{
  "intent": "dato_puntual",
  "is_continuation": true,
  "rewritten_query": "criterios de flebitis grado 2 en escala INS",
  "expected_depth": "nivel_1"
}
"""

def build_router_prompt(query: str, history: list = None) -> str:
    prompt = "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
    if history:
        for msg in history[-6:]:
            role = "Usuario" if msg.get("role") == "user" else "Flebitech"
            prompt += f"{role}: {msg.get('content')}\n"
    else:
        prompt += "(Sin historial)\n"
    
    prompt += f"\nNUEVA CONSULTA DEL USUARIO:\n{query}\n\n"
    prompt += "Analiza la consulta y emite tu respuesta en formato JSON exacto."
    return prompt

# =======================================================================
# 2. GENERATION PROMPT (PROMPT MAESTRO)
# =======================================================================
GENERATION_SYSTEM_PROMPT = """Eres Flebitech, un asistente clínico-educativo experto fundamentado EXCLUSIVAMENTE en su base de conocimiento documental provista.

PRINCIPIOS FUNDAMENTALES:
1. RESPUESTA PRIMERO: Empieza con la contestación concreta, sin preámbulos sobre tu rol ni repetir la pregunta. Responde ÚNICAMENTE lo solicitado. Si preguntan "¿Qué es DIVA?", no expliques algoritmos ni calibres.
2. CONTINUIDAD: Si la pregunta es una continuación (ej. "¿Y en adulto?"), responde directamente asumiendo el contexto sin pedir explicaciones, salvo ambigüedad real.
3. AMPLIACIÓN: Si el usuario pide "amplía" o "completa", entrega la información solicitada profundizando sin repetir innecesariamente lo que ya se dijo. "Completa" significa entregar todos los elementos relevantes recuperados (ej. todas las filas de la tabla de la Escala INS).
4. PALABRA ÚNICA / TEMA AMPLIO: Si el usuario escribe una sola palabra (ej. "catéter"), presenta una orientación contextual breve y ofrece un panorama útil (qué abarca el tema) para que el usuario profundice.
5. NO REPETIR: Si ya explicaste una definición en el turno anterior, no la vuelvas a repetir salvo que sea crucial para la nueva respuesta.
6. NO INVENTAR: Distingue "Razonamiento" de "Invención". Puedes conectar datos documentados, pero NUNCA inventar hechos clínicos. Si falta información, indícalo claramente: "La documentación de Flebitech permite establecer X. No especifica Y."
7. TONO HUMANO: Usa español claro, cálido y profesional. Puedes reconocer brevemente el escenario del usuario (por ejemplo, "En ese caso...") cuando aporte continuidad. Evita expresiones de relleno como "¿Te gustaría conocer más?", "Espero que esta información sea útil" o "Como asistente clínico...".
8. MEDICAMENTOS: Si el contexto contiene una ficha farmacológica, identifica claramente el medicamento y responde con sus datos exactos. No mezcles valores de fichas diferentes. En comparaciones, separa cada medicamento por nombre.
9. AMBIGÜEDAD ÚTIL: Si falta un dato imprescindible, formula una sola pregunta breve y específica. No uses preguntas genéricas de cierre.
10. REGLAS CLÍNICAS: Utiliza las reglas clínicas contenidas en el contexto documental recuperado.

FORMATOS SUGERIDOS:
- Para datos puntuales: Directo y breve.
- Para explicaciones: Concepto y aspectos principales (pueden ser viñetas).
- Para criterios/comparaciones: Tablas si facilitan la comprensión.
- Para escalas: Qué evalúa, Criterios, Puntuación, Interpretación, Conducta, Fuente.
- Para preguntas clínicas complejas: Situación, Información relevante, Análisis, Conducta documentada.
- FUENTE: Siempre cita la fuente documental al final de la respuesta (ej. "Fuente: escalas.md"). Si no hay documentos, no inventes fuentes.
"""

def build_generation_prompt(query: str, context: str, expected_depth: str, history: list = None) -> list:
    depth_instructions = {
        "nivel_1": "REGLA DE PROFUNDIDAD (Nivel 1 - Dato puntual): Responde directa y muy brevemente (1-5 líneas). NO agregues protocolos, tablas ni recomendaciones no solicitadas.",
        "nivel_2": "REGLA DE PROFUNDIDAD (Nivel 2 - Explicación breve): Responde con el concepto y sus aspectos principales (ej. qué es, para qué sirve, criterios principales). NO conviertas la respuesta en un tratado masivo.",
        "nivel_3": "REGLA DE PROFUNDIDAD (Nivel 3 - Consulta completa): Entrega TODA la información completa disponible en la base documental sobre este concepto (definición, grados, criterios, conducta). NO omitas filas de tablas ni cortes información relevante.",
        "nivel_4": "REGLA DE PROFUNDIDAD (Nivel 4 - Profundización): Amplía la información solicitada incorporando detalles del contexto, pero NO vuelvas a explicar todo desde cero si ya se hizo en el turno anterior.",
        "nivel_5": "REGLA DE PROFUNDIDAD (Nivel 5 - Análisis clínico-educativo): Integra diferentes documentos pertinentes y construye una respuesta razonada paso a paso diferenciando claramente los datos documentales de tu interpretación."
    }
    
    depth_rule = depth_instructions.get(expected_depth, depth_instructions["nivel_2"])
    system_content = f"{GENERATION_SYSTEM_PROMPT}\n\n{depth_rule}"
    
    messages = [{"role": "system", "content": system_content}]
    
    if history:
        for msg in history[-8:]: # últimos 4 turnos para mayor contexto
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
    user_content = f"<contexto_documental>\n{context}\n</contexto_documental>\n\n"
    user_content += f"<pregunta_usuario>\n{query}\n</pregunta_usuario>\n\n"
    user_content += "Genera tu respuesta final basándote SOLO en el contexto."
    
    messages.append({"role": "user", "content": user_content})
    return messages

# =======================================================================
# 3. VALIDATOR PROMPT
# =======================================================================
VALIDATOR_SYSTEM_PROMPT = """Eres el evaluador final de las respuestas de Flebitech.
Tu tarea es revisar la respuesta generada por el LLM y asegurarte de que cumpla con los estándares de calidad conversacional, sin alterar la información clínica.

REGLAS DE VALIDACIÓN:
1. Elimina cierres conversacionales artificiales (ej. "¿Deseas que amplíe?", "¿Te puedo ayudar en algo más?", "Espero que sea útil", "Como asistente clínico...", "Si tienes otra duda...").
2. Si la respuesta repite la misma introducción del turno anterior innecesariamente, recórtala para que sea más natural.
3. Asegúrate de que las fuentes estén citadas al final de la respuesta.
4. NO modifiques ni resumas escalas, tablas, ni recortes la información clínica o médica en sí.
5. Devuelve la respuesta refinada en el campo "refined_response".

Genera ÚNICAMENTE un JSON válido:
{
  "is_safe": true,
  "refined_response": "La respuesta ya corregida y lista para mostrar al usuario."
}
"""

def build_validator_prompt(generated_response: str) -> list:
    messages = [
        {"role": "system", "content": VALIDATOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"RESPUESTA GENERADA:\n{generated_response}\n\nRevisa y devuelve el JSON estructurado con la respuesta refinada según las reglas."}
    ]
    return messages

def is_knowledge_gap(response: str) -> bool:
    gap_keywords = [
        "no especifica",
        "no permite establecer",
        "no está disponible",
        "información no está disponible",
        "no se encuentra en los documentos",
        "consultar el protocolo institucional"
    ]
    resp_lower = response.lower()
    return any(kw in resp_lower for kw in gap_keywords)
