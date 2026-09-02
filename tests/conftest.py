import os

import pytest

from backend.groq_client import GroqClient
from backend.orchestrator import ConversationalOrchestrator
from backend.rag_engine import RAGEngine


@pytest.fixture(scope="session")
def rag():
    return RAGEngine(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))


@pytest.fixture()
def orchestrator(rag):
    return ConversationalOrchestrator(rag, GroqClient(api_key=""))
