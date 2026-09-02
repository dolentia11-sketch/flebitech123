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
    client = GroqClient()
    def mock_generate_chat(prompt):
        prompt_lower = prompt.lower()
        if "amiodarona" in prompt_lower and "ph" in prompt_lower:
            return "El pH de la amiodarona es 9.5." # Hallucination (real is 3.5 - 4.5)
        if "ampicilina" in prompt_lower and "vancomicina" in prompt_lower:
            return "El pH de vancomicina es 2.5 - 4.5 y el de ampicilina es 8.0 - 10.0 y el de penicilina es 9.0."
        if "vancomicina" in prompt_lower and "ph" in prompt_lower:
            # Valid LLM response
            return "El pH de la vancomicina es de 2.5 a 4.5."
        return ""
    client.generate_chat = mock_generate_chat
    return ConversationalOrchestrator(rag, client)

def test_conversations(orchestrator):
    with open(os.path.join(DATA_DIR, "conversations.json"), "r", encoding="utf-8") as f:
        conversations = json.load(f)
        
    for conv in conversations:
        history = []
        for turn in conv["turns"]:
            query = turn["query"]
            response, _sources, _has_answer, _latency = orchestrator.chat(query, history=history)
            
            normalized = response.lower()
            
            if "required" in turn:
                for req in turn["required"]:
                    assert req.lower() in normalized, f"Conv {conv['id']}: missing '{req}' in response: {response}"
                    
            if "forbidden" in turn:
                for forbid in turn["forbidden"]:
                    assert forbid.lower() not in normalized, f"Conv {conv['id']}: found forbidden '{forbid}' in response: {response}"
                    
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
