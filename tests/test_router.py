from backend.prompt_system import deterministic_route


def test_deterministic_route_negation():
    history = []
    # Prueba 1: Negación explícita
    query = "¿Qué medicamentos NO requieren vía central?"
    route = deterministic_route(query, history)
    assert "no " in route["rewritten_query"].lower() or " no " in route["rewritten_query"].lower()

    # Prueba 2
    query2 = "¿Cuál no se diluye con SSN?"
    route2 = deterministic_route(query2, history)
    assert "no " in route2["rewritten_query"].lower() or " no " in route2["rewritten_query"].lower()

def test_deterministic_route_out_of_domain_after_clinical():
    history = [{"role": "user", "content": "pH de vancomicina"}, {"role": "assistant", "content": "El pH es 2.5 - 4.5"}]
    query = "¿Cuál es la capital de Francia?"
    route = deterministic_route(query, history, known_medication=False)
    assert route["intent"] == "out_of_domain"
    assert not route["is_continuation"]
