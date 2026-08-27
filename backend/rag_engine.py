# -*- coding: utf-8 -*-
"""
Motor de Búsqueda y Recuperación Aumentada (RAG) de Flebitech.
Combina búsqueda léxica BM25/TF-IDF con filtro de stopwords y coincidencia de entidades farmacológicas.
"""

import os
import json
import re
import math
from typing import List, Dict, Any, Tuple

SPANISH_STOPWORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'a', 'al',
    'en', 'con', 'por', 'para', 'es', 'son', 'que', 'qué', 'como', 'cómo', 'cual',
    'cuál', 'cuáles', 'cuales', 'su', 'sus', 'mi', 'mis', 'tu', 'tus', 'se', 'lo',
    'le', 'les', 'y', 'o', 'u', 'pero', 'mas', 'más', 'este', 'esta', 'estos', 'estas',
    'sobre', 'entre', 'hacia', 'hasta', 'desde', 'durante', 'mediante', 'según', 'segun'
}

class RAGEngine:
    def __init__(self, knowledge_base_path: str = "./knowledge_base/"):
        self.kb_path = os.path.abspath(knowledge_base_path)
        self.chunks: List[Dict[str, Any]] = []
        self.medications: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.index_documents()

    def _tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        cleaned = re.sub(r'[^\w\s\.\,\-\%]', ' ', text.lower())
        tokens = [t.strip('.,;:') for t in cleaned.split() if len(t.strip('.,;:')) > 1]
        if remove_stopwords:
            tokens = [t for t in tokens if t not in SPANISH_STOPWORDS]
        return tokens

    def index_documents(self):
        self.chunks = []
        self.medications = []
        
        # 1. Cargar medicamentos.json
        med_file = os.path.join(self.kb_path, 'medicamentos.json')
        if os.path.exists(med_file):
            try:
                with open(med_file, 'r', encoding='utf-8') as f:
                    self.medications = json.load(f)
                
                for med in self.medications:
                    content = (
                        f"MEDICAMENTO: {med.get('nombre')} ({med.get('grupo', '')})\n"
                        f"- pH: {med.get('ph')}\n"
                        f"- Osmolaridad: {med.get('osmolaridad')}\n"
                        f"- Tonicidad: {med.get('tonicidad')}\n"
                        f"- Vía Recomendada: {med.get('via_recomendada')}\n"
                        f"- Riesgo de Flebitis: {med.get('riesgo_flebitis')}\n"
                        f"- Diluyente: {med.get('diluyente_recomendado')}\n"
                        f"- Volumen de Dilución: {med.get('volumen_minimo_dilucion')}\n"
                        f"- Tiempo de Infusión: {med.get('tiempo_infusion_minimo')}\n"
                        f"- Observaciones de Enfermería: {med.get('observaciones_enfermeria')}"
                    )
                    self.chunks.append({
                        'id': f"med_{med.get('nombre')}",
                        'source': 'medicamentos.json',
                        'title': f"Ficha Farmacológica: {med.get('nombre')}",
                        'content': content,
                        'entity_key': med.get('nombre', '').lower()
                    })
            except Exception as e:
                print(f"Aviso cargando medicamentos.json: {e}")

        # 2. Cargar archivos Markdown
        md_files = ['escalas.md', 'protocolo_basico.md', 'casos_clinicos.md']
        for fname in md_files:
            fpath = os.path.join(self.kb_path, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Dividir por secciones ## o ###
                    sections = re.split(r'\n(?=##?\s)', text)
                    for idx, sec in enumerate(sections):
                        sec_str = sec.strip()
                        if len(sec_str) < 30:
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

        # 3. Construir índice TF-IDF para búsqueda léxica rápida
        self._build_tfidf_index()

    def _build_tfidf_index(self):
        doc_freq = {}
        total_docs = len(self.chunks)
        if total_docs == 0:
            return

        for chunk in self.chunks:
            tokens = set(self._tokenize(chunk['content'] + " " + chunk['title']))
            for t in tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1

        self.idf = {t: math.log((total_docs + 1) / (df + 1)) + 1.0 for t, df in doc_freq.items()}
        self.doc_vectors = []

        for chunk in self.chunks:
            tokens = self._tokenize(chunk['content'] + " " + chunk['title'])
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            
            vec = {}
            if tokens:
                for t, count in tf.items():
                    if t in self.idf:
                        vec[t] = (count / len(tokens)) * self.idf[t]
            self.doc_vectors.append(vec)

    def search(self, query: str, top_k: int = 3) -> Tuple[str, List[str], bool]:
        if not self.chunks:
            return "", [], False

        q_lower = query.lower()
        q_tokens = self._tokenize(query, remove_stopwords=True)
        
        # Si la consulta no tiene términos significativos
        if not q_tokens and not any(m['nombre'].lower() in q_lower for m in self.medications):
            return "", [], False

        scores = [0.0] * len(self.chunks)
        matched_any_entity = False

        # 1. Boost directo por entidad / fármaco
        for i, chunk in enumerate(self.chunks):
            if chunk.get('entity_key') and chunk['entity_key'] in q_lower:
                scores[i] += 20.0
                matched_any_entity = True
            
            # Coincidencia con título de sección
            if any(t in chunk['title'].lower() for t in q_tokens if len(t) > 3):
                scores[i] += 8.0

        # 2. Puntuación TF-IDF de tokens de la pregunta
        for t in q_tokens:
            if t in self.idf:
                idf_val = self.idf[t]
                for i, doc_vec in enumerate(self.doc_vectors):
                    if t in doc_vec:
                        scores[i] += doc_vec[t] * idf_val * 3.0

        # 3. Ordenar por relevancia
        # Umbral mínimo de relevancia: score >= 0.8 si no es entidad exacta
        min_threshold = 0.5
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
