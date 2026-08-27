# -*- coding: utf-8 -*-
"""
Módulo de Métricas y Analítica de Aprendizaje para Flebitech.
Base de datos SQLite para registrar interacciones, temas y brechas de conocimiento.
Usa SQLite en memoria en entornos serverless (Vercel) y archivo local en otros entornos.
"""

import os
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

# Detectar si estamos en Vercel (filesystem efímero, /tmp es la única zona escribible)
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))

if IS_VERCEL:
    DB_PATH = ":memory:"
else:
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    DB_PATH = os.path.join(DB_DIR, 'metrics.db')

# Thread-local storage para conexiones en memoria
_local = threading.local()
_memory_db: Optional[sqlite3.Connection] = None
_lock = threading.Lock()


def get_db_connection() -> sqlite3.Connection:
    global _memory_db

    if IS_VERCEL:
        with _lock:
            if _memory_db is None:
                _memory_db = sqlite3.connect(":memory:", check_same_thread=False)
                _memory_db.row_factory = sqlite3.Row
                _init_schema(_memory_db)
            return _memory_db
    else:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def _init_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            topic TEXT,
            had_answer INTEGER DEFAULT 1,
            source_docs TEXT,
            latency_ms REAL
        )
    ''')
    conn.commit()


def init_db():
    conn = get_db_connection()
    _init_schema(conn)
    if not IS_VERCEL:
        conn.close()


def detect_topic(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ['diva', 'dificil', 'difícil', 'palpar', 'vena no visible', 'ecografia', 'ultrasonido']):
        return 'Valoración DIVA'
    elif any(k in q for k in ['escala', 'vhp', 'grado 0', 'grado 1', 'grado 2', 'grado 3', 'grado 4', 'cordon', 'cordón', 'eritema', 'edema', 'secrecion', 'purulenta', 'escala ins', 'flebitis ins']):
        return 'Escalas de Flebitis (INS/VHP)'
    elif any(k in q for k in ['cateter', 'catéter', 'calibre', 'gauge', '24g', '22g', '20g', '18g', '16g', '14g']):
        return 'Selección de Catéter'
    elif any(k in q for k in ['osmolaridad', 'tonicidad', 'hipotonica', 'hipotónica', 'isotonica', 'isotónica', 'hipertonica', 'hipertónica', 'hemodilucion', 'hemodilución', 'mosm']):
        return 'Parámetros Fisicoquímicos (pH/Osmolaridad)'
    elif any(k in q for k in ['vancomicina', 'potasio', 'kcl', 'amiodarona', 'ciprofloxacina', 'fenitoina', 'fenitoína', 'ceftriaxona', 'ampicilina', 'calcio', 'dextrosa', 'npt', 'nutricion parenteral', 'nutrición parenteral', 'furosemida', 'omeprazol', 'claritromicina', 'metronidazol', 'dad 5', 'dad 10', 'dad 50']):
        return 'Medicamentos Específicos'
    elif any(k in q for k in [' ph ', ' ph,', ' ph.', 'ph ', 'ph<', 'ph>', 'ph=', 'acido', 'ácido', 'alcalino']):
        return 'Parámetros Fisicoquímicos (pH/Osmolaridad)'
    elif any(k in q for k in ['caso', 'clinico', 'clínico', 'paciente', 'escenario', 'simulacion', 'simulación']):
        return 'Casos Clínicos / Escenarios'
    elif any(k in q for k in ['protocolo', 'lacardio', 'sabana', 'clorhexidina', '2 intentos', 'puncion', 'punción', 'algoritmo']):
        return 'Protocolos Institucionales'
    else:
        return 'Consulta General / Otra'


def log_question(query: str, response: str, session_id: str = 'default',
                 had_answer: bool = True, source_docs: str = '', latency_ms: float = 0.0) -> int:
    init_db()
    topic = detect_topic(query)
    is_fallback = 'Esa información no está disponible en el material de Flebitech' in response or not had_answer
    had_ans_int = 0 if is_fallback else 1

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (timestamp, session_id, query, response, topic, had_answer, source_docs, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        session_id,
        query,
        response,
        topic,
        had_ans_int,
        source_docs,
        latency_ms
    ))
    row_id = cursor.lastrowid
    conn.commit()
    if not IS_VERCEL:
        conn.close()
    return row_id


def get_session_stats(session_id: Optional[str] = None) -> Dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if session_id:
        cursor.execute('SELECT COUNT(*) as total FROM interactions WHERE session_id = ?', (session_id,))
        total = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as answered FROM interactions WHERE session_id = ? AND had_answer = 1', (session_id,))
        answered = cursor.fetchone()['answered']
        cursor.execute('SELECT COUNT(*) as gaps FROM interactions WHERE session_id = ? AND had_answer = 0', (session_id,))
        gaps = cursor.fetchone()['gaps']
    else:
        cursor.execute('SELECT COUNT(*) as total FROM interactions')
        total = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as answered FROM interactions WHERE had_answer = 1')
        answered = cursor.fetchone()['answered']
        cursor.execute('SELECT COUNT(*) as gaps FROM interactions WHERE had_answer = 0')
        gaps = cursor.fetchone()['gaps']

    if not IS_VERCEL:
        conn.close()
    return {
        'total_preguntas': total,
        'respondidas': answered,
        'brechas_detectadas': gaps,
        'tasa_resolucion': round((answered / total * 100), 1) if total > 0 else 100.0
    }


def get_recent_interactions(limit: int = 10) -> List[Dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interactions ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    if not IS_VERCEL:
        conn.close()
    return rows


def get_knowledge_gaps(limit: int = 10) -> List[Dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, query, topic FROM interactions WHERE had_answer = 0 ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    if not IS_VERCEL:
        conn.close()
    return rows
