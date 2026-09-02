from backend.metrics import get_recent_interactions, init_db, log_question


def test_session_isolation():
    init_db()
    log_question("Q_A", "R_A", session_id="session_A", latency_ms=100)
    log_question("Q_B", "R_B", session_id="session_B", latency_ms=100)
    
    recent_A = get_recent_interactions(session_id="session_A", limit=5)
    assert len(recent_A) >= 1
    assert any(interaction["query"] == "Q_A" for interaction in recent_A)
    assert all(interaction["query"] != "Q_B" for interaction in recent_A)
