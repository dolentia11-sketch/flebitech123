import os
import pytest
from backend.rag_engine import _validate_medication_record, RAGEngine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_validate_medication_record():
    valid = {
        "nombre": "Test",
        "ph": "1",
        "osmolaridad": "1",
        "via_recomendada": "1",
        "riesgo_flebitis": "1",
        "diluyente_recomendado": "1",
        "tiempo_infusion_minimo": "1",
        "observaciones_enfermeria": "1"
    }
    assert _validate_medication_record(valid) == []
    
    invalid = valid.copy()
    del invalid["ph"]
    assert _validate_medication_record(invalid) == ["ph"]

def test_all_medications_valid():
    rag = RAGEngine(os.path.join(ROOT, "knowledge_base"))
    assert len(rag.medications) > 0, "No medications loaded"
    # The rag engine already filters and logs invalid medications.
    # To test strictly, we could reload the JSON ourselves and check.
    import json
    with open(os.path.join(ROOT, "knowledge_base", "medicamentos.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    for med in data:
        missing = _validate_medication_record(med)
        assert not missing, f"Medication '{med.get('nombre', 'Unknown')}' is missing fields: {missing}"
