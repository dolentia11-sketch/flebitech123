import json
import os
import pytest
from backend.rag_engine import RAGEngine
from backend.orchestrator import ConversationalOrchestrator
from backend.groq_client import GroqClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture(scope="module")
def rag():
    return RAGEngine(os.path.join(ROOT, "knowledge_base"))

@pytest.fixture(scope="module")
def orchestrator(rag):
    return ConversationalOrchestrator(rag, GroqClient())

def test_conversations(orchestrator):
    with open(os.path.join(DATA_DIR, "conversations.json"), "r", encoding="utf-8") as f:
        conversations = json.load(f)
        
    for conv in conversations:
        history = []
        for turn in conv["turns"]:
            query = turn["query"]
            response, sources, has_answer, latency = orchestrator.chat(query, history=history)
            
            normalized = response.lower()
            
            if "required" in turn:
                for req in turn["required"]:
                    assert req.lower() in normalized, f"Conv {conv['id']}: missing '{req}' in response: {response}"
                    
            if "forbidden" in turn:
                for forbid in turn["forbidden"]:
                    assert forbid.lower() not in normalized, f"Conv {conv['id']}: found forbidden '{forbid}' in response: {response}"
                    
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
