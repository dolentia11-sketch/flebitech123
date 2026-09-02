import json
import os

import pytest

from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator
from backend.rag_engine import RAGEngine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture(scope="module")
def rag():
    return RAGEngine(os.path.join(ROOT, "knowledge_base"))

@pytest.fixture(scope="module")
def orchestrator(rag):
    return ConversationalOrchestrator(rag, GroqClient(api_key=""))

def test_golden_queries(orchestrator):
    with open(os.path.join(DATA_DIR, "golden_queries.json"), "r", encoding="utf-8") as f:
        queries = json.load(f)
        
    for q in queries:
        query_text = q["query"]
        response, sources, had_answer, _latency = orchestrator.chat(query_text)
        
        normalized = response.lower()
        
        if "expected_had_answer" in q:
            assert had_answer == q["expected_had_answer"], f"Failed had_answer for '{query_text}'"
            
        if "expected_sources" in q:
            for src in q["expected_sources"]:
                assert src in sources, f"Source '{src}' not found for '{query_text}'"
                
        if "required_terms" in q:
            for term in q["required_terms"]:
                assert term.lower() in normalized, f"Required term '{term}' missing in response for '{query_text}'"
                
        if "forbidden_terms" in q:
            for term in q["forbidden_terms"]:
                assert term.lower() not in normalized, f"Forbidden term '{term}' found in response for '{query_text}'"
