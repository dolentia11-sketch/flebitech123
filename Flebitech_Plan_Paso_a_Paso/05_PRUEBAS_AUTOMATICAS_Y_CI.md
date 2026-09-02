# Etapa 5 — Pruebas automáticas e integración continua

## Objetivo

Conseguir que cada cambio sea evaluado automáticamente desde un clon limpio, sin consumir la API de Groq y con una barrera real contra regresiones clínicas, de privacidad y seguridad.

## Paso 1. Crear rama

```bash
git switch master
git pull --ff-only
git switch -c test/ci-regression-suite
```

## Paso 2. Añadir dependencias de desarrollo

Crea `requirements-dev.txt`:

```text
-r requirements.txt
pytest>=8.3,<9
pytest-cov>=5,<7
httpx>=0.27,<1
ruff>=0.8,<1
```

No añadas `pytest` a la Lambda de producción si solo se usa para desarrollo.

Instala:

```bash
pip install -r requirements-dev.txt
```

## Paso 3. Mantener temporalmente las pruebas actuales

Antes de migrar, CI debe ejecutar los scripts existentes exactamente como están:

```bash
python test_conversacional.py
python test_orchestrator.py
python test_mock_1000.py
python test_flebitech.py
```

No borres un script hasta que su equivalente pytest demuestre la misma cobertura.

## Paso 4. Crear estructura pytest

```text
tests/
├── conftest.py
├── test_api.py
├── test_medications.py
├── test_metrics_privacy.py
├── test_orchestrator.py
├── test_prompt_security.py
├── test_rag.py
└── test_response_builder.py
```

En `tests/conftest.py` crea fixtures con Groq desactivado:

```python
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
```

## Paso 5. Crear pruebas semánticas, no literales frágiles

Ejemplo:

```python
def test_vancomycin_ph_is_specific(orchestrator):
    response, sources, had_answer, _ = orchestrator.chat("¿Cuál es el pH de la vancomicina?")
    normalized = response.lower()
    assert had_answer is True
    assert "2.5 - 4.5" in normalized
    assert "osmolaridad" not in normalized
    assert sources == ["medicamentos.json"]
```

Para la vía central usa aserciones negativas:

```python
def test_exclusive_central_route_excludes_conditional_drugs(orchestrator):
    response, _, had_answer, _ = orchestrator.chat(
        "¿Qué medicamentos requieren vía central obligatoria?"
    )
    assert had_answer is True
    assert "nutrición parenteral total" in response.lower()
    assert "| Vancomicina |" not in response
    assert "| Furosemida |" not in response
```

## Paso 6. Corregir la prueba de 1,000 turnos

No basta con validar `isinstance(response, str)`. Separa consultas por expectativa:

```python
CASES = [
    ("¿Cuál es el pH de la vancomicina?", True, "2.5 - 4.5"),
    ("¿Cuál es la capital de Francia?", False, "no especifica"),
    ("¿Cuándo uso Midline?", True, "7 a 29 días"),
]
```

En cada vuelta valida `had_answer` y el término requerido. Reporta exactitud, no solo ausencia de excepciones.

## Paso 7. Crear GitHub Actions

Crea `.github/workflows/ci.yml`:

```yaml
name: Flebitech CI

on:
  pull_request:
  push:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      GROQ_API_KEY: ""
      PYTHONUTF8: "1"

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: pip install -r requirements-dev.txt
      - run: python -m compileall -q backend api
      - run: ruff check backend api tests
      - run: pytest -q --cov=backend --cov=api --cov-report=term-missing
```

Durante la migración añade, antes de pytest, los cuatro scripts heredados. Retíralos de CI solo cuando estén cubiertos por pytest.

## Paso 8. Ejecutar localmente

```bash
ruff check backend api tests
pytest -q --cov=backend --cov=api --cov-report=term-missing --cov-fail-under=35
```

No fijes todavía una cobertura global artificialmente alta. Empieza con un umbral bajo pero obligatorio, exige ejecución en módulos críticos modificados y aumenta el umbral gradualmente.

La cobertura final debe incluir pruebas pytest para `api/index.py`. Los scripts heredados pueden seguir corriendo durante la transición, pero no sustituyen el informe de cobertura.

## Paso 9. Proteger la rama

En GitHub configura el check `Flebitech CI / test` como obligatorio antes del merge. Esta acción se realiza en la configuración del repositorio, no en el código.

No cierres esta etapa si `master` aparece sin protección en GitHub o si no existe un run de pull request recuperable para el commit auditado.

## Criterio de salida

- [ ] CI funciona desde clon limpio.
- [ ] No usa una clave real de Groq.
- [ ] Incluye aserciones negativas clínicas.
- [ ] Evalúa privacidad y seguridad.
- [ ] `api/index.py` contribuye al informe pytest/cobertura.
- [ ] Existe `--cov-fail-under` con umbral progresivo.
- [ ] Dependencias tienen lockfile o constraints reproducibles.
- [ ] Ningún PR puede fusionarse con CI rojo.
