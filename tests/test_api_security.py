import json
import uuid

from fastapi.testclient import TestClient

from api import index


def _offline_client(monkeypatch) -> TestClient:
    """Evita tráfico a proveedores durante las pruebas de límites de la API."""
    monkeypatch.setattr(index.groq, "_explicit_api_key", True)
    monkeypatch.setattr(index.groq, "client", None)
    return TestClient(index.app)


def test_chat_rejects_more_history_than_the_documented_limit(monkeypatch):
    client = _offline_client(monkeypatch)
    history = [{"role": "user", "content": f"turno {number}"} for number in range(9)]

    response = client.post(
        "/api/chat",
        json={"query": "¿Qué es DIVA?", "session_id": "history_limit", "history": history},
    )

    assert response.status_code == 422


def test_chat_rejects_a_body_larger_than_the_transport_limit(monkeypatch):
    client = _offline_client(monkeypatch)

    response = client.post(
        "/api/chat",
        content=b"x" * (index.MAX_CHAT_REQUEST_BYTES + 1),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert "límite" in response.json()["detail"]


def test_metrics_response_omits_transcripts_and_queries(monkeypatch):
    client = _offline_client(monkeypatch)
    session_id = f"privacy_{uuid.uuid4().hex[:20]}"
    canary_query = "consulta-canario-no-debe-volver-en-metricas"

    chat_response = client.post(
        "/api/chat",
        json={"query": canary_query, "session_id": session_id},
    )
    assert chat_response.status_code == 200

    metrics_response = client.get("/api/metrics", params={"session_id": session_id})
    assert metrics_response.status_code == 200
    payload = metrics_response.json()
    serialized = json.dumps(payload, ensure_ascii=False)

    assert canary_query not in serialized
    assert "response" not in serialized
    assert all(set(item) <= {"timestamp", "topic", "had_answer"} for item in payload["recent"])
    assert all(set(item) <= {"timestamp", "topic"} for item in payload["gaps"])
