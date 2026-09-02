# Flebitech - Asistente educativo de flebitis química

Flebitech es un tutor conversacional para estudiantes y profesionales de enfermería, especializado en la prevención de flebitis química asociada a terapia intravenosa periférica. El proyecto se desarrolla en el contexto académico-clínico de la Universidad de La Sabana y laCardio.

---

## Inicio Rapido

### 1. Requisitos previos

- Python 3.11 recomendado para compatibilidad con CI.
- Python 3.9 o superior para ejecución local básica.

### 2. Instalacion de dependencias

```bash
pip install -r requirements.txt
```

### 3. Variables de entorno

Groq es opcional. Si no configuras `GROQ_API_KEY`, la aplicación sigue funcionando con respuesta determinista local desde la base indexada.

```env
GROQ_API_KEY=gsk_tu_clave_aqui
GROQ_MODEL=openai/gpt-oss-20b
FLEBITECH_CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

No guardes claves reales en Git. En Vercel, configura `GROQ_API_KEY` y `FLEBITECH_CORS_ORIGINS` como variables del entorno de despliegue.

### 4. Re-indexar documentos

```bash
python indexer.py
```

### 5. Ejecutar la aplicacion web

```bash
uvicorn dev_server:app --reload --port 8000
```

Abre `http://localhost:8000`. Este servidor replica localmente las rutas estáticas y `/api/*` usadas en Vercel. La interfaz alternativa de Streamlit sigue disponible con:

```bash
streamlit run app.py
```

---

## Estructura del proyecto

```text
FLEBITECH/
├── knowledge_base/                 # Base documental
│   ├── medicamentos.json           # 15 farmacos criticos estructurados
│   ├── escalas.md                  # DIVA, INS, VHP y algoritmo de puncion
│   ├── protocolo_basico.md         # Protocolo institucional
│   └── casos_clinicos.md           # Casos clinicos de toma de decisiones
│
├── backend/                        # Motor RAG y logica de negocio
│   ├── rag_engine.py               # Busqueda BM25 + entidades farmacologicas
│   ├── prompt_system.py            # Guardrails clinicos y routing
│   ├── groq_client.py              # Conector Groq + fallback RAG local
│   ├── response_builder.py         # Respuesta determinista cuando no hay LLM
│   └── metrics.py                  # Analitica SQLite de sesiones y brechas
│
├── api/index.py                    # API FastAPI para Vercel
├── public/index.html               # Interfaz web estatica
├── app.py                          # Interfaz Streamlit
├── docs/LINEA_BASE.md              # Registro de auditoria y alcance
└── requirements.txt
```

---

## Principio clinico de seguridad

Flebitech opera bajo RAG estricto: no debe inventar dosis, vias, diluciones ni datos clinicos. Si una consulta no está en los documentos indexados, responde:

> "Esa informacion no esta disponible en el material de Flebitech. Te recomendamos consultar el protocolo institucional o a tu supervisor clinico."

Las clasificaciones de via central son campos estructurados para evitar respuestas ambiguas. Mientras `fuente_via_central` indique `PENDIENTE`, deben tratarse como clasificacion operativa pendiente de validacion institucional, no como aprobacion clinica final.

## Estado de endurecimiento

El repositorio conserva riesgos abiertos documentados en [docs/LINEA_BASE.md](docs/LINEA_BASE.md) y en `Flebitech_Plan_Paso_a_Paso/`. Las etapas priorizadas cubren seguridad clinica, privacidad de metricas, prompt injection, XSS, pruebas automatizadas, reproducibilidad y gobernanza de fuentes.

El chat acepta hasta 8 mensajes de historial y un cuerpo de 18 KiB. La vista de métricas muestra únicamente tema, fecha y resultado; no devuelve la consulta ni la respuesta. Esto reduce la exposición de una sesión, pero no convierte el `session_id` del navegador en autenticación: no ingreses datos reales de pacientes.

`requirements.txt` contiene el conjunto completo de dependencias de ejecución con versiones fijadas y sin directivas de inclusión, para que Vercel pueda interpretarlo de forma reproducible. `requirements-dev.txt` aplica además las restricciones de `requirements.lock` para las herramientas de CI y desarrollo. El CI usa Python 3.11 y exige una cobertura inicial de 55 %; la protección obligatoria de la rama se configura en GitHub, fuera del repositorio.
