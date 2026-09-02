# -*- coding: utf-8 -*-
"""
Motor de Búsqueda y Recuperación Aumentada (RAG) de Flebitech.
Combina búsqueda léxica BM25 con filtro de stopwords y coincidencia de entidades farmacológicas.
"""

import os
import json
import re
import math
import unicodedata
from typing import List, Dict, Any, Tuple

SPANISH_STOPWORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'al',
    'en', 'con', 'por', 'para', 'es', 'son', 'que', 'qué', 'como', 'cómo', 'cual',
    'cuál', 'cuáles', 'cuales', 'su', 'sus', 'mi', 'mis', 'tu', 'tus', 'se', 'lo',
    'le', 'les', 'y', 'o', 'u', 'pero', 'mas', 'más', 'este', 'esta', 'estos', 'estas',
    'sobre', 'entre', 'hacia', 'hasta', 'desde', 'durante', 'mediante', 'según', 'segun'
}

MED_ALIASES = {
    'vancomicina': ['vancomicina'],
    'cloruro de potasio (kcl)': ['cloruro de potasio', 'kcl', 'potasio'],
    'amiodarona': ['amiodarona'],
    'ciprofloxacina': ['ciprofloxacina', 'cipro'],
    'fenitoina (difenilhidantoina)': ['fenitoina', 'fenitoina sodica', 'difenilhidantoina'],
    'ampicilina': ['ampicilina'],
    'ampicilina sulbactam': ['ampicilina sulbactam', 'ampicilina/sulbactam', 'unasyn'],
    'ceftriaxona': ['ceftriaxona'],
    'gluconato de calcio al 10%': ['gluconato de calcio', 'calcio', 'gluconato calcio'],
    'dextrosa en agua destilada al 10% (dad 10%)': ['dad 10', 'dextrosa 10', 'dad10'],
    'dextrosa en agua destilada al 50% (dad 50%)': ['dad 50', 'dextrosa 50', 'dad50'],
    'nutricion parenteral total (npt)': ['nutricion parenteral', 'npt', 'nutrición parenteral'],
    'furosemida': ['furosemida', 'lasix'],
    'omeprazol iv': ['omeprazol'],
    'claritromicina iv': ['claritromicina'],
    'metronidazol iv': ['metronidazol', 'flagyl']
}

CLINICAL_KEYWORDS = {
    'ph', 'osmolaridad', 'tonicidad', 'flebitis', 'cateter', 'cateteres', 'vena', 'venas',
    'venoso', 'venosa', 'dilucion', 'diluyente', 'infusion', 'velocidad', 'diva', 'ins',
    'vhp', 'vip', 'puncion', 'calibre', 'gauge', 'gauges', 'antisepsia', 'clorhexidina',
    'via', 'periferico', 'periferica', 'central', 'midline', 'picc', 'cvc', 'endotelio',
    'eritema', 'edema', 'dolor', 'cordon', 'aposito', 'sangre', 'dosis', 'mg', 'meq', 'ml',
    'solucion', 'ssn', 'dad', 'vesicante', 'irritante', 'complicacion', 'extravasacion',
    'medicamento', 'farmaco', 'farmacos', 'antibiotico', 'neumonia', 'protocolo', 'escala',
    'escalas', 'enfermeria', 'enfermero', 'enfermera', 'paciente', 'torno', 'torniquete',
    'hemodilucion', 'lumen', 'antebrazo', 'mano', 'fosa', 'antecubital', 'criterios',
    'evaluacion', 'cuidados', 'riesgo', 'algoritmo', 'trombosis', 'tromboflebitis'
}

class RAGEngine:
    def __init__(self, knowledge_base_path: str = "./knowledge_base/"):
        self.kb_path = os.path.abspath(knowledge_base_path)
        self.chunks: List[Dict[str, Any]] = []
        self.medications: List[Dict[str, Any]] = []
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, int]] = []
        self.doc_lengths: List[int] = []
        self.avg_dl: float = 0.0
        self.index_documents()

    @staticmethod
    def _normalize(text: str) -> str:
        """Normaliza el texto quitando acentos y pasándolo a minúsculas."""
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()

    def _tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        # Indexar y consultar con la misma normalización evita que "fenitoína"
        # y "fenitoina" terminen en vocabularios distintos.
        cleaned = re.sub(r'[^\w\s\.\,\-\%]', ' ', self._normalize(text))
        tokens = [t.strip('.,;:') for t in cleaned.split() if len(t.strip('.,;:')) > 1]
        if remove_stopwords:
            tokens = [t for t in tokens if t not in SPANISH_STOPWORDS]
        return tokens

    @classmethod
    def _medication_aliases(cls, medication_name: str) -> List[str]:
        """Construye alias buscables a partir del catálogo, sin mantener otra lista paralela.

        Los alias explícitos cubren marcas o abreviaturas clínicas. Las variantes
        derivadas permiten reconocer automáticamente medicamentos nuevos, nombres
        con paréntesis y sufijos como ``IV``.
        """
        normalized_name = cls._normalize(medication_name).strip()
        aliases = set(MED_ALIASES.get(normalized_name, []))
        aliases.add(normalized_name)

        without_parentheses = re.sub(r"\s*\([^)]*\)\s*", " ", normalized_name).strip()
        if without_parentheses:
            aliases.add(without_parentheses)

        for parenthetical in re.findall(r"\(([^)]*)\)", normalized_name):
            value = parenthetical.strip()
            if value:
                aliases.add(value)

        without_iv = re.sub(r"\s+iv$", "", normalized_name).strip()
        if without_iv:
            aliases.add(without_iv)

        return sorted(
            {cls._normalize(alias).strip() for alias in aliases if alias and len(alias.strip()) >= 3},
            key=len,
            reverse=True,
        )

    @staticmethod
    def _find_fuzzy_alias(query: str, alias: str) -> int:
        """Busca el alias con tolerancia a errores tipográficos (fuzzy matching).
        Devuelve el índice aproximado de la coincidencia, o -1 si no coincide.
        """
        import difflib
        import re
        
        query_clean = re.sub(r'[^\w\s]', '', query)
        alias_clean = re.sub(r'[^\w\s]', '', alias)
        
        query_words = query_clean.split()
        alias_words = alias_clean.split()
        
        if not alias_words or len(alias_words) > len(query_words):
            return -1
            
        for i in range(len(query_words) - len(alias_words) + 1):
            window = " ".join(query_words[i:i+len(alias_words)])
            match = False
            
            if window == alias_clean:
                match = True
            else:
                # Si hay números en el alias, deben coincidir exactamente en la ventana
                nums_alias = re.findall(r'\d+', alias_clean)
                nums_window = re.findall(r'\d+', window)
                if nums_alias != nums_window:
                    continue
                    
                if len(alias_clean) <= 4 and len(window) == len(alias_clean):
                    if sum(1 for a, b in zip(window, alias_clean) if a != b) <= 1:
                        match = True
                elif difflib.SequenceMatcher(None, window, alias_clean).ratio() >= 0.85:
                    match = True
                
            if match:
                first_word = query_words[i]
                # Buscar la posición de la palabra en la cadena original
                # Se usa una búsqueda básica para tener un orden relativo
                match_obj = re.search(rf"\b{re.escape(first_word)}", query, re.IGNORECASE)
                return match_obj.start() if match_obj else query.find(first_word)
                
        return -1

    def match_medications(self, query: str) -> List[Dict[str, Any]]:
        """Devuelve, en orden de mención, los medicamentos nombrados en la consulta."""
        normalized_query = self._normalize(query or "")
        matches = []
        for medication in self.medications:
            aliases = self._medication_aliases(medication.get("nombre", ""))
            positions = []
            for alias in aliases:
                idx = self._find_fuzzy_alias(normalized_query, alias)
                if idx != -1:
                    positions.append(idx)
            if positions:
                matches.append((min(positions), medication))
        return [medication for _, medication in sorted(matches, key=lambda item: item[0])]

    def medication_context(self, query: str) -> Tuple[str, List[str], bool]:
        """Recupera únicamente las fichas farmacológicas mencionadas en la consulta."""
        matched = self.match_medications(query)
        if not matched:
            return "", [], False

        matched_names = {self._normalize(med.get("nombre", "")) for med in matched}
        medication_chunks = [
            chunk for chunk in self.chunks
            if self._normalize(chunk.get("entity_key", "")) in matched_names
        ]
        if not medication_chunks:
            return "", [], False

        context = "\n\n".join(
            f"### [Fuente: {chunk['source']} | {chunk['title']}]\n{chunk['content']}"
            for chunk in medication_chunks
        )
        return context, ["medicamentos.json"], True

    def index_documents(self):
        self.chunks = []
        self.medications = []
        
        # Recorrer recursivamente buscando archivos .json y .md
        md_files = []
        json_files = []
        
        for root, _, files in os.walk(self.kb_path):
            for file in files:
                full_path = os.path.join(root, file)
                if file.endswith('.json'):
                    json_files.append((file, full_path))
                elif file.endswith('.md'):
                    md_files.append((file, full_path))
        
        # 1. Cargar archivos JSON (medicamentos y potencialmente otros)
        for fname, fpath in json_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Procesamiento específico si parece ser medicamentos
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'nombre' in data[0]:
                    self.medications.extend(data)
                    for med in data:
                        content = (
                            f"MEDICAMENTO: {med.get('nombre')} ({med.get('grupo', '')})\n"
                            f"- pH: {med.get('ph')}\n"
                            f"- Osmolaridad: {med.get('osmolaridad')}\n"
                            f"- Tonicidad: {med.get('tonicidad')}\n"
                            f"- Vía Recomendada: {med.get('via_recomendada')}\n"
                            f"- Tipo de Vía Central: {med.get('tipo_via_central', 'pendiente_revision')}\n"
                            f"- Criterio de Vía Central: {med.get('criterio_via_central', '')}\n"
                            f"- Fuente de Vía Central: {med.get('fuente_via_central', '')}\n"
                            f"- Riesgo de Flebitis: {med.get('riesgo_flebitis')}\n"
                            f"- Diluyente: {med.get('diluyente_recomendado')}\n"
                            f"- Volumen de Dilución: {med.get('volumen_minimo_dilucion')}\n"
                            f"- Tiempo de Infusión: {med.get('tiempo_infusion_minimo')}\n"
                            f"- Observaciones de Enfermería: {med.get('observaciones_enfermeria')}"
                        )
                        self.chunks.append({
                            'id': f"med_{med.get('nombre')}",
                            'source': fname,
                            'title': f"Ficha Farmacológica: {med.get('nombre')}",
                            'content': content,
                            'entity_key': med.get('nombre', '').lower()
                        })
            except Exception as e:
                print(f"Aviso cargando {fname}: {e}")

        # 2. Cargar archivos Markdown
        for fname, fpath in md_files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Dividir por secciones principales ## (preservando subsecciones ### dentro del mismo bloque temático)
                sections = re.split(r'\n(?=##\s)', text)
                for idx, sec in enumerate(sections):
                    sec_str = sec.strip()
                    # Omitir encabezados de metadatos o introducciones sin contenido clínico
                    if len(sec_str) < 300 and not sec_str.startswith('##'):
                        continue
                    if len(sec_str) < 50:
                        continue
                    
                    lines = sec_str.split('\n')
                    header = lines[0].replace('#', '').strip() if lines else fname
                    
                    self.chunks.append({
                        'id': f"{fname}_{idx}",
                        'source': fname,
                        'title': header,
                        'content': sec_str,
                        'entity_key': ''
                    })
            except Exception as e:
                print(f"Aviso cargando {fname}: {e}")

        # 3. Construir índice BM25 (reemplaza a TF-IDF)
        self._build_tfidf_index()

    def _build_tfidf_index(self):
        doc_freq = {}
        total_docs = len(self.chunks)
        if total_docs == 0:
            return

        self.doc_lengths = []
        total_len = 0

        for chunk in self.chunks:
            tokens = self._tokenize(chunk['content'] + " " + chunk['title'])
            self.doc_lengths.append(len(tokens))
            total_len += len(tokens)
            
            for t in set(tokens):
                doc_freq[t] = doc_freq.get(t, 0) + 1

        # Calcular longitud promedio de los documentos
        self.avg_dl = total_len / total_docs if total_docs > 0 else 0

        # Calcular IDF
        self.idf = {t: math.log((total_docs + 1) / (df + 1)) + 1.0 for t, df in doc_freq.items()}
        self.doc_vectors = []

        # Guardar las frecuencias de los términos por documento para cálculo dinámico BM25
        for chunk in self.chunks:
            tokens = self._tokenize(chunk['content'] + " " + chunk['title'])
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            
            self.doc_vectors.append(tf)

    def search(self, query: str, top_k: int = 3) -> Tuple[str, List[str], bool]:
        if not self.chunks:
            return "", [], False

        q_norm = self._normalize(query)
        q_tokens = self._tokenize(query, remove_stopwords=True)
        
        # La entidad farmacológica se resuelve desde el catálogo completo. Así un
        # medicamento nuevo funciona sin agregarlo manualmente al enrutador.
        matched_medications = self.match_medications(query)
        matched_medication_names = {
            self._normalize(medication.get('nombre', '')) for medication in matched_medications
        }
        has_med = bool(matched_medications)

        # Si la consulta no tiene términos significativos
        if not q_tokens and not has_med:
            return "", [], False

        scores = [0.0] * len(self.chunks)
        matched_any_entity = False

        # 1. Boost directo por entidad / fármaco con aliases y títulos de escala
        for i, chunk in enumerate(self.chunks):
            ek = chunk.get('entity_key')
            title_norm = self._normalize(chunk.get('title', ''))

            if ek:
                ek_norm = self._normalize(ek)
                if ek_norm in matched_medication_names:
                    scores[i] += 20.0
                    matched_any_entity = True
            
            # Boost por escalas clínicas y algoritmos en título
            if 'diva' in q_norm and 'diva' in title_norm:
                scores[i] += 30.0
            if ('adulto' in q_norm or 'criterios' in q_norm) and 'diva' in title_norm:
                scores[i] += 20.0
            if 'ins' in q_norm and 'ins' in title_norm:
                scores[i] += 30.0
            if ('vhp' in q_norm or 'vip' in q_norm) and ('vhp' in title_norm or 'vip' in title_norm):
                scores[i] += 30.0
            if ('elegibilidad' in q_norm or 'dispositivo' in q_norm or 'seleccion' in q_norm or 'midline' in q_norm or 'picc' in q_norm or 'cvc' in q_norm) and ('elegibilidad' in title_norm or 'dispositivo' in title_norm):
                scores[i] += 30.0
            if ('cateter' in q_norm or 'cateteres' in q_norm or 'via' in q_norm) and ('elegibilidad' in title_norm or 'calibre' in title_norm or 'algoritmo' in title_norm):
                scores[i] += 20.0
            if ('calibre' in q_norm or 'gauge' in q_norm) and ('calibre' in title_norm or 'gauge' in title_norm):
                scores[i] += 25.0
            if ('protocolo' in q_norm or 'insercion' in q_norm or 'puncion' in q_norm) and ('algoritmo' in title_norm or 'puncion' in title_norm):
                scores[i] += 20.0

            # Coincidencia con título de sección
            if any(t in title_norm for t in q_tokens if len(t) > 3):
                scores[i] += 8.0

        # 2. Puntuación BM25Okapi de tokens de la pregunta
        k1 = 1.5
        b = 0.75
        
        for t in q_tokens:
            if t in self.idf:
                idf_val = self.idf[t]
                for i, doc_vec in enumerate(self.doc_vectors):
                    if t in doc_vec:
                        freq = doc_vec[t]
                        doc_len = self.doc_lengths[i]
                        
                        # Fórmula BM25
                        tf_norm = (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * doc_len / self.avg_dl))
                        score = tf_norm * idf_val
                        
                        scores[i] += score * 3.0

        # Verificar relevancia del dominio clínico
        has_clinical = any(self._normalize(kw) in q_norm for kw in CLINICAL_KEYWORDS)

        # 3. Ordenar por relevancia
        # Si la consulta no contiene entidades, fármacos ni conceptos clínicos clave, exige un score significativamente mayor
        min_threshold = 0.5 if (matched_any_entity or has_med or has_clinical) else 15.0
        ranked_indices = sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)
        top_indices = [idx for idx in ranked_indices[:top_k] if scores[idx] >= min_threshold]

        if not top_indices:
            # No se encontraron coincidencias relevantes en la base
            return "", [], False

        retrieved_chunks = [self.chunks[idx] for idx in top_indices]
        sources = list(dict.fromkeys([c['source'] for c in retrieved_chunks]))
        
        formatted_context_parts = []
        for c in retrieved_chunks:
            formatted_context_parts.append(f"### [Fuente: {c['source']} | {c['title']}]\n{c['content']}")

        full_context = "\n\n".join(formatted_context_parts)
        return full_context, sources, True

    def medication_catalog_context(self) -> Tuple[str, List[str], bool]:
        """Devuelve las fichas farmacológicas completas para consultas de catálogo."""
        medication_chunks = [chunk for chunk in self.chunks if chunk.get('entity_key')]
        if not medication_chunks:
            return "", [], False
        context = "\n\n".join(
            f"### [Fuente: {chunk['source']} | {chunk['title']}]\n{chunk['content']}"
            for chunk in medication_chunks
        )
        return context, ["medicamentos.json"], True
