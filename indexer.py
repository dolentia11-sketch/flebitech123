#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Re-indexación de la Base de Conocimiento de Flebitech.
Ejecutar: python indexer.py
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.rag_engine import RAGEngine

def main():
    print("==================================================")
    print("[*] Indexando Base Documental de Flebitech...")
    print("==================================================")
    
    rag = RAGEngine(knowledge_base_path="./knowledge_base/")
    
    print(f"[+] Total de fragmentos indexados: {len(rag.chunks)}")
    print(f"[+] Total de medicamentos estructurados: {len(rag.medications)}")
    print(f"[+] Vocabulario lexico: {len(rag.idf)} terminos unicos")
    print("==================================================")
    print("[OK] Base de conocimiento indexada y lista para consultas.")

if __name__ == "__main__":
    main()
