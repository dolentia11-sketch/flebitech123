def test_vancomycin_ph_is_specific(orchestrator):
    response, sources, had_answer, _ = orchestrator.chat("¿Cuál es el pH de la vancomicina?")
    normalized = response.lower()
    assert had_answer is True
    assert "2.5 - 4.5" in normalized
    assert "osmolaridad" not in normalized
    assert sources == ["medicamentos.json"]

def test_exclusive_central_route_excludes_conditional_drugs(orchestrator):
    response, _, had_answer, _ = orchestrator.chat(
        "¿Qué medicamentos requieren vía central obligatoria?"
    )
    assert had_answer is True
    assert "nutrición parenteral total" in response.lower()
    assert "| Vancomicina |" not in response
    assert "| Furosemida |" not in response
