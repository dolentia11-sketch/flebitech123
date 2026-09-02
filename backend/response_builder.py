"""Respuestas locales legibles cuando el LLM no está disponible.

No intenta inventar una respuesta: solo selecciona y presenta texto que ya fue
recuperado por el índice documental.
"""

import re
import unicodedata
from collections.abc import Iterable


def _plain(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()


def _blocks(context: str) -> list[str]:
    return [b.strip() for b in re.split(r"(?=### \[Fuente:)", context or "") if b.strip()]


def _source_line(sources: Iterable[str]) -> str:
    names = list(dict.fromkeys(sources or []))
    return f"\n\nFuente: {', '.join(names)}" if names else ""


def _as_bullets(lines: Iterable[str]) -> str:
    return "\n".join(
        line if line.lstrip().startswith(("-", "*", "|")) else f"- {line}"
        for line in lines
    )


def _clean_lines(block: str) -> list[str]:
    lines = []
    for line in block.splitlines():
        value = line.strip()
        if not value or value.startswith("### [Fuente:") or value.startswith("---"):
            continue
        lines.append(value)
    return lines


def _field_lines(blocks: list[str], terms: tuple, limit: int = 8, strict: bool = False) -> list[str]:
    selected = []
    for block in blocks:
        for line in _clean_lines(block):
            normalized = _plain(line)
            label = re.sub(r"^[\-*•\s]+", "", normalized)
            matches_label = any(re.match(rf"^{re.escape(term)}[a-z]*(?:\s|:)", label) for term in terms)
            if matches_label or (not strict and any(term in normalized for term in terms if term not in {"ph", "via"})):
                selected.append(line)
    # Preserva orden y elimina duplicados, incluso cuando el RAG trae secciones repetidas.
    return list(dict.fromkeys(selected))[:limit]


def _most_relevant_medication_blocks(query: str, blocks: list[str]) -> list[str]:
    """Evita mezclar la ficha del fármaco con reglas generales de otros documentos."""
    query_words = [w for w in re.findall(r"[a-z0-9]+", _plain(query)) if len(w) > 3]
    matches = []
    for block in blocks:
        normalized = _plain(block)
        header = re.search(r"medicamento:\s*([^\(\n]+)", normalized)
        if header:
            med_words = [w for w in re.findall(r"[a-z0-9]+", header.group(1)) if len(w) > 3]
            if any(word in query_words for word in med_words):
                matches.append(block)
    return matches or blocks


def _first_heading(block: str) -> str:
    match = re.search(r"\|\s([^|\]]+)\]", block)
    return match.group(1).strip() if match else "Información documental"


def _topic_map(query: str) -> list[str]:
    text = _plain(query)
    areas = []
    if any(x in text for x in ("diva", "acceso dificil")):
        areas.append("valoración DIVA y elección del acceso")
    if any(x in text for x in ("ins", "vhp", "flebit")):
        areas.append("clasificación y conducta ante flebitis")
    if any(x in text for x in ("cateter", "midline", "picc", "cvc", "calibre")):
        areas.append("selección de catéteres y accesos")
    if any(x in text for x in ("medicament", "farmac", "vancomicina", "amiodarona", "potasio", "kcl")):
        areas.append("parámetros y cuidados de medicamentos")
    if not areas:
        areas.append("prevención de flebitis química y terapia intravenosa")
    return areas


def _section_excerpt(blocks: list[str], marker: str, limit: int = 10) -> str:
    """Extrae una subsección documental sin arrastrar el resto del capítulo."""
    marker = _plain(marker)
    for block in blocks:
        lines = _clean_lines(block)
        for index, line in enumerate(lines):
            if marker in _plain(line):
                selected = []
                for candidate in lines[index:]:
                    if selected and candidate.startswith("###") and marker not in _plain(candidate):
                        break
                    selected.append(candidate)
                if selected:
                    return "\n".join(selected)
    return ""


def _table_rows(blocks: list[str], marker: str) -> list[list[str]]:
    marker = _plain(marker)
    rows = []
    for block in blocks:
        for line in _clean_lines(block):
            if line.startswith("|") and marker in _plain(line):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows.append(cells)
    return rows


def _format_scale_row(cells: list[str], scale: str) -> str:
    if len(cells) >= 4:
        return (
            f"## {scale}: {cells[0].replace('**', '')}\n\n"
            f"**Criterios clínicos:** {cells[1]}\n\n"
            f"**Interpretación:** {cells[2]}\n\n"
            f"**Conducta documentada:** {cells[3]}"
        )
    return "\n".join(cells)


def _vhp_item(blocks: list[str], score: str) -> str:
    marker = f"vhp {score}"
    for block in blocks:
        lines = _clean_lines(block)
        for index, line in enumerate(lines):
            if marker in _plain(line):
                selected = [line]
                if index + 1 < len(lines) and "accion" in _plain(lines[index + 1]):
                    selected.append(lines[index + 1])
                return "\n".join(selected)
    return ""


def _medication_names(blocks: list[str]) -> list[str]:
    names = []
    for block in blocks:
        title = _first_heading(block)
        if _plain(title).startswith("ficha farmacologica:"):
            names.append(title.split(":", 1)[1].strip())
    return list(dict.fromkeys(names))


def _medication_record(block: str) -> dict:
    """Convierte una ficha recuperada a campos presentables sin alterar sus valores."""
    title = _first_heading(block)
    if not _plain(title).startswith("ficha farmacologica:"):
        return {}

    record = {"nombre": title.split(":", 1)[1].strip()}
    field_map = {
        "ph": "pH",
        "osmolaridad": "Osmolaridad",
        "tonicidad": "Tonicidad",
        "via recomendada": "Vía recomendada",
        "riesgo de flebitis": "Riesgo de flebitis",
        "diluyente": "Diluyente",
        "volumen de dilucion": "Volumen de dilución",
        "tiempo de infusion": "Tiempo de infusión",
        "observaciones de enfermeria": "Observaciones de enfermería",
        "tipo de via central": "Tipo de vía central",
        "criterio de via central": "Criterio de vía central",
        "fuente de via central": "Fuente de vía central",
    }
    for line in _clean_lines(block):
        cleaned = re.sub(r"^[\-*•\s]+", "", line).strip()
        if ":" not in cleaned:
            continue
        label, value = cleaned.split(":", 1)
        canonical = field_map.get(_plain(label).strip())
        if canonical and value.strip():
            record[canonical] = value.strip()
    return record


def _medication_records(blocks: list[str]) -> list[dict]:
    return [record for record in (_medication_record(block) for block in blocks) if record]


def _is_plain_medication_catalog_request(text: str) -> bool:
    if not any(word in text for word in ("medicamento", "farmaco")):
        return False
    has_list_language = any(
        phrase in text
        for phrase in (
            "dame", "lista", "listado", "catalogo", "cuales hay", "cuales son",
            "que medicamentos", "que farmacos", "que hay", "cuantos medicamentos",
            "documentados", "incluidos", "disponibles", "todos los medicamentos",
            "cual ", "cuales ", "cual no"
        )
    )
    has_filter = any(
        term in text
        for term in (
            "requieren", "via central", "via periferica", "riesgo", "ph", "osmolar",
            "dilucion", "infusion", "vesicante", "irritante", "diluy", "ssn", "dad"
        )
    )
    return has_list_language and not has_filter

def _medication_collection_response(text: str, blocks: list[str], sources: list[str]) -> str:
    """Responde filtros sobre todo el catálogo conservando el texto documental exacto."""
    records = _medication_records(blocks)
    if not records:
        return ""

    has_negation = any(term in text for term in ("no ", "nunca ", "excepto ", "sin ", "contraindicado"))
    asks_exclusive = any(term in text for term in (
        "central obligatoria", "central obligatorio", "exclusivamente central",
        "via central exclusiva", "requieren via central",
    )) and not has_negation
    asks_conditional = any(term in text for term in (
        "pueden requerir", "segun concentracion", "segun duración",
        "segun duracion", "central condicionada",
    ))
    asks_no_central = "via central" in text and has_negation
    asks_no_ssn = "ssn" in text and has_negation
    asks_no_dad = "dad" in text and has_negation

    if asks_no_ssn or asks_no_dad:
        if asks_no_ssn:
            selected = [
                record for record in records
                if "incompatible con ssn" in _plain(record.get("Diluyente", "")) or "exclusivamente dad" in _plain(record.get("Diluyente", ""))
            ]
            title = "## Medicamentos incompatibles con SSN"
        else:
            selected = [
                record for record in records
                if "incompatible con dad" in _plain(record.get("Diluyente", "")) or "exclusivamente ssn" in _plain(record.get("Diluyente", ""))
            ]
            title = "## Medicamentos incompatibles con DAD"
        
        if selected:
            rows = "\n".join(
                f"| {record['nombre']} | {record.get('Diluyente', '')} |"
                for record in selected
            )
            return (
                f"{title}\n\n| Medicamento | Diluyente documentado |\n"
                "|---|---|\n"
                f"{rows}{_source_line(sources)}"
            )

    if "via central" in text or asks_exclusive or asks_conditional:
        if asks_exclusive:
            selected = [
                record for record in records
                if _plain(record.get("Tipo de vía central", "")) == "exclusiva"
            ]
            title = "## Medicamentos con vía central exclusiva"
            note = (
                "Se incluyen únicamente fichas clasificadas en la base local como de vía central exclusiva. "
                "La validación clínica institucional sigue pendiente si la fuente de vía central no está aprobada."
            )
        elif asks_conditional:
            selected = [
                record for record in records
                if _plain(record.get("Tipo de vía central", "")) == "condicionada"
            ]
            title = "## Medicamentos con vía central condicionada"
            note = "La indicación depende del criterio documentado de concentración, duración u otra condición clínica."
        elif asks_no_central:
            selected = [
                record for record in records
                if _plain(record.get("Tipo de vía central", "")) not in {"exclusiva", "condicionada"}
            ]
            title = "## Medicamentos que no requieren vía central exclusiva"
            note = "Estos medicamentos pueden administrarse por vía periférica según la documentación."
        else:
            selected = [
                record for record in records
                if _plain(record.get("Tipo de vía central", "")) in {"exclusiva", "condicionada", "opcional"}
            ]
            title = "## Uso documentado de vía central"
            note = "La tabla diferencia el tipo de indicación; no todas las opciones son obligatorias."

        if selected:
            rows = "\n".join(
                f"| {record['nombre']} | {record.get('Tipo de vía central', '')} | "
                f"{record.get('Criterio de vía central', record.get('Vía recomendada', ''))} |"
                for record in selected
            )
            return (
                f"{title}\n\n{note}\n\n"
                "| Medicamento | Clasificación | Criterio documentado |\n"
                "|---|---|---|\n"
                f"{rows}{_source_line(sources)}"
            )

    if any(term in text for term in ("riesgo", "vesicante", "irritante")):
        selected = records
        if "alto" in text or "mayor" in text or "extremo" in text:
            selected = [
                record for record in records
                if any(level in _plain(record.get("Riesgo de flebitis", "")) for level in ("alto", "extremo", "vesicante"))
            ]
        if selected:
            rows = "\n".join(
                f"| {record['nombre']} | {record.get('Riesgo de flebitis', '')} |"
                for record in selected
            )
            return "## Riesgo de flebitis documentado\n\n| Medicamento | Riesgo |\n|---|---|\n" + rows + _source_line(sources)

    field = next((
        label for marker, label in (
            ("ph", "pH"), ("osmolar", "Osmolaridad"), ("diluc", "Volumen de dilución"),
            ("infus", "Tiempo de infusión"), ("via", "Vía recomendada"),
        ) if marker in text
    ), "")
    if field:
        rows = "\n".join(f"| {record['nombre']} | {record.get(field, '')} |" for record in records)
        return f"## {field} por medicamento\n\n| Medicamento | {field} |\n|---|---|\n{rows}{_source_line(sources)}"
    return ""


def _medication_comparison(blocks: list[str], sources: list[str]) -> str:
    records = _medication_records(blocks)
    if len(records) < 2:
        return ""
    fields = ("pH", "Osmolaridad", "Vía recomendada", "Riesgo de flebitis", "Diluyente", "Tiempo de infusión")
    header = "| Aspecto | " + " | ".join(record["nombre"] for record in records) + " |"
    separator = "|---|" + "---|" * len(records)
    rows = "\n".join(
        "| " + field + " | " + " | ".join(record.get(field, "No especificado") for record in records) + " |"
        for field in fields
    )
    return f"## Comparación farmacológica\n\n{header}\n{separator}\n{rows}{_source_line(sources)}"


def build_local_response(query: str, context: str, sources: list[str], intent: str = "clinical_query", search_query: str = "") -> str:
    """Construye una respuesta útil, breve y rastreable desde el contexto RAG."""
    text = _plain(query)
    effective_text = _plain(f"{search_query} {query}")
    blocks = _blocks(context)
    if not blocks:
        return "La documentación de Flebitech no contiene un fragmento suficiente para responder esta consulta."

    if intent == "greeting":
        return "¡Hola! Soy Flebitech, tu asistente inteligente en prevención de flebitis química y accesos venosos periféricos, con protocolos de laCardio."

    if intent == "tematica_general":
        titles = list(dict.fromkeys(_first_heading(b) for b in blocks))[:4]
        bullets = "\n".join(f"- {title}" for title in titles)
        areas = ", ".join(_topic_map(query))
        title = query.strip().strip(".?!¡¿").capitalize()
        return f"## {title}\n\nLa base documental aborda este tema desde {areas}. Puedes consultar, por ejemplo:\n\n{bullets}{_source_line(sources)}"

    if "pediatr" in text and "diva" in effective_text:
        excerpt = _section_excerpt(blocks, "Criterios P-DIVA", limit=13)
        if excerpt:
            return "## DIVA en pediatría y neonatología\n\n" + excerpt + _source_line(sources)

    if "adult" in text and "diva" in effective_text:
        excerpt = _section_excerpt(blocks, "Criterios de Evaluación en Adultos", limit=13)
        if excerpt:
            return "## DIVA en adultos\n\n" + excerpt + _source_line(sources)

    if "diva" in effective_text and ("interpreta" in text or re.search(r"\b(?:4|5)\s+puntos?\b", text) or "diva alto" in text):
        if re.search(r"\b(?:4|5)\s+puntos?\b", text) or "diva alto" in text:
            rows = _table_rows(blocks, ">= 4 puntos")
        else:
            rows = sum((_table_rows(blocks, marker) for marker in ("0 - 1 punto", "2 - 3 puntos", ">= 4 puntos")), [])
        if rows:
            body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
            header = "| Puntuación DIVA | Riesgo | Éxito al primer intento | Conducta |\n|---|---|---|---|\n"
            return "## Interpretación DIVA\n\n" + header + body + _source_line(sources)

    grade = re.search(r"\bgrado\s*([0-4])\b", text)
    if grade and "ins" in effective_text:
        rows = _table_rows(blocks, f"grado {grade.group(1)}")
        if rows:
            return _format_scale_row(rows[0], "Escala INS") + _source_line(sources)

    vhp_score = re.search(r"\bvhp\s*([0-5])\b", text)
    if vhp_score:
        item = _vhp_item(blocks, vhp_score.group(1))
        if item:
            return f"## VHP {vhp_score.group(1)}\n\n{item}{_source_line(sources)}"

    if "cordon" in text and "palpable" in text:
        rows = _table_rows(blocks, "cordón venoso palpable")
        if rows:
            # Prefiere grado 3; grado 4 añade drenaje purulento y longitud >2,5 cm.
            row = next((candidate for candidate in rows if "grado 3" in _plain(candidate[0])), rows[0])
            return _format_scale_row(row, "Escala INS") + _source_line(sources)

    if "vhp" in effective_text and "criterio" in text:
        excerpt = _section_excerpt(blocks, "Escala Visual de Flebitis Hospitalaria", limit=14)
        if excerpt:
            return "## Criterios VHP\n\n" + excerpt + _source_line(sources)

    if any(device in effective_text for device in ("midline", "picc", "cvc", "cateter")) and any(x in text for x in ("elegib", "cuando uso", "cuando se usa", "cual elegir")):
        device = next((name for name in ("midline", "picc", "cvc") if name in text), "")
        if device:
            rows = _table_rows(blocks, device)
            rows = [row for row in rows if device in _plain(row[0])] or rows
            if rows:
                row = rows[0]
                labels = ("Dispositivo", "Duración", "Límites de pH/osmolaridad", "Indicaciones", "Punta")
                body = "\n\n".join(f"**{label}:** {value}" for label, value in zip(labels, row))
                return f"## {device.upper()}\n\n{body}{_source_line(sources)}"
        excerpt = _section_excerpt(blocks, "Criterios de Elegibilidad", limit=12)
        if excerpt:
            return "## Elegibilidad del acceso vascular\n\n" + excerpt + _source_line(sources)

    if _is_plain_medication_catalog_request(text):
        names = _medication_names(blocks)
        if names:
            return (
                f"## Medicamentos documentados ({len(names)})\n\n"
                + "\n".join(f"- {name}" for name in names)
                + "\n\nPuedes consultar cualquiera por nombre y pedir un dato concreto, como pH, dilución, vía, tiempo de infusión o cuidados."
                + _source_line(sources)
            )

    if any(word in text for word in ("medicamento", "farmaco", "cual ", "cuales ")):
        collection_response = _medication_collection_response(text, blocks, sources)
        if collection_response:
            return collection_response

    if intent == "comparacion":
        comparison = _medication_comparison(_most_relevant_medication_blocks(search_query or query, blocks), sources)
        if comparison:
            return comparison

    if intent == "comparacion" and len(_medication_names(_most_relevant_medication_blocks(search_query or query, blocks))) < 2:
        return "La consulta identifica un medicamento, pero no especifica el segundo elemento de comparación. Indica el medicamento o acceso que quieres contrastar." + _source_line(sources)

    if intent == "conducta" and any(x in effective_text for x in ("medicament", "vancomicina", "amiodarona", "potasio", "kcl")):
        med_blocks = _most_relevant_medication_blocks(search_query or query, blocks)
        lines = _field_lines(med_blocks, ("via", "riesgo", "diluy", "volumen", "tiempo", "observacion"), limit=7, strict=True)
        if lines:
            return "## Conducta documentada\n\n" + _as_bullets(lines) + _source_line(sources)

    if "cuidad" in text and any(x in effective_text for x in ("medicament", "vancomicina", "amiodarona", "potasio", "kcl")):
        med_blocks = _most_relevant_medication_blocks(search_query or query, blocks)
        lines = _field_lines(med_blocks, ("via", "diluy", "volumen", "tiempo", "observacion"), limit=6, strict=True)
        if lines:
            return "## Cuidados documentados\n\n" + _as_bullets(lines) + _source_line(sources)

    medication_terms = ("ph", "osmolar", "tonic", "via", "diluy", "diluc", "volumen", "infus", "riesgo", "observacion", "cuidad", "efectos secundarios", "adverso", "dosis", "contraindicacion", "interaccion")
    if intent == "dato_puntual" or (intent == "medicamento" and any(x in text for x in medication_terms)):
        field_terms = []
        if "ph" in text: field_terms.append("ph")
        if "osmolar" in text: field_terms.append("osmolar")
        if "tonic" in text: field_terms.append("tonic")
        if "via" in text: field_terms.append("via")
        if "diluc" in text: field_terms.extend(("diluy", "volumen"))
        if "infus" in text: field_terms.extend(("tiempo", "infus"))
        if "cuidad" in text: field_terms.append("observacion")
        if "riesgo" in text: field_terms.append("riesgo")
        lines = _field_lines(_most_relevant_medication_blocks(search_query or query, blocks), tuple(field_terms) or medication_terms, limit=8, strict=True)
        missing_terms = []
        if "efectos secundarios" in text or "adverso" in text: missing_terms.append("efectos secundarios")
        if "dosis" in text: missing_terms.append("dosis")
        if "contraindicacion" in text: missing_terms.append("contraindicaciones")
        if "interaccion" in text: missing_terms.append("interacciones")

        if lines:
            med_blocks = _most_relevant_medication_blocks(search_query or query, blocks)
            medication_names = []
            if med_blocks:
                for block in med_blocks:
                    match = re.search(r"MEDICAMENTO:\s*([^\n]+)", block, flags=re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        if name not in medication_names:
                            medication_names.append(name)
            
            if medication_names:
                medication_name = f" para {' y '.join(medication_names)}"
            else:
                medication_name = ""
            
            note = ""
            if missing_terms:
                note = f"\n\nNota: La documentación de Flebitech no especifica información sobre {', '.join(missing_terms)}."
                
            return f"## Información puntual{medication_name}\n\n" + _as_bullets(lines) + note + _source_line(sources)
        elif missing_terms:
            return f"La documentación de Flebitech no especifica información sobre {', '.join(missing_terms)} en este contexto."
    if intent == "medicamento":
        med_blocks = _most_relevant_medication_blocks(search_query or query, blocks)
        records = _medication_records(med_blocks)
        if records:
            record = records[0]
            labels = (
                "pH", "Osmolaridad", "Tonicidad", "Vía recomendada", "Riesgo de flebitis",
                "Diluyente", "Volumen de dilución", "Tiempo de infusión", "Observaciones de enfermería",
            )
            details = "\n".join(
                f"- **{label}:** {record[label]}" for label in labels if record.get(label)
            )
            return f"## {record['nombre']}\n\n{details}{_source_line(sources)}"

    # Para una guía completa se conserva la tabla y el texto recuperado, sin que el
    # fallback recorte una escala justo cuando el usuario pidió todas sus filas.
    if intent in {"guia_completa", "algoritmo"} or any(x in text for x in ("tabla", "completa", "todo sobre", "paso a paso")):
        chosen = blocks[0]
        return chosen[:14000].rstrip() + _source_line(sources)

    if any(x in text for x in ("ph", "osmolar", "diluy", "diluc", "infus", "cuidad", "via")):
        lines = _field_lines(_most_relevant_medication_blocks(search_query or query, blocks), ("ph", "osmolar", "diluy", "diluc", "via", "infus", "cuidad", "observacion"), limit=7)
        if lines:
            return "## Respuesta\n\n" + _as_bullets(lines) + _source_line(sources)

    # Explicaciones generales: toma la sección más relevante completa, sin
    # truncar a 4 líneas para no destruir tablas ni escalas.
    lines = _clean_lines(blocks[0])
    excerpt_lines = []
    for line in lines:
        if excerpt_lines and line.startswith("###"):
            break
        excerpt_lines.append(line)
    
    excerpt = "\n".join(excerpt_lines)
    return f"## Respuesta\n\n{excerpt}{_source_line(sources)}"


def clean_generated_response(response: str, sources: list[str]) -> str:
    """Elimina cierres robóticos y garantiza una referencia documental mínima."""
    value = (response or "").strip()
    if not value:
        return ""
    patterns = (
        r"\s*(?:¿te gustaría|¿deseas|¿quieres)\b.*$",
        r"\s*(?:espero que (?:esta|la) información.*)$",
        r"\s*(?:si tienes otra duda|como asistente clínico[^.]*\.)\s*$",
    )
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE | re.DOTALL).strip()
    if sources and not re.search(r"\bfuente(?:s)?\s*:", value, flags=re.IGNORECASE):
        value += _source_line(sources)
    return value
