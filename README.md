# 🏥 Flebitech — Asistente Educativo de Flebitis Química

Flebitech es un tutor conversacional inteligente diseñado para estudiantes y profesionales de enfermería, especializado en la **prevención de flebitis química asociada a terapia intravenosa periférica**, desarrollado en alianza académica-clínica entre la **Universidad de La Sabana** y **laCardio**.

---

## 🚀 Inicio Rápido (MVP sin Costos)

### 1. Requisitos Previos
* Python 3.9 o superior instalado.

### 2. Instalación de Dependencias
`ash
pip install -r requirements.txt
`

### 3. Configuración de Variables de Entorno (Opcional para Groq API)
1. Obtén tu clave gratuita en [Groq Console](https://console.groq.com) (sin tarjeta de crédito).
2. Abre el archivo .env y pega tu clave:
`env
GROQ_API_KEY=gsk_tu_clave_aqui
`
*(Nota: Si no colocas la clave de Groq, la aplicación funcionará de todas formas en modo determinista local con la base de conocimiento indexada).*

### 4. Re-indexar Base de Documentos
`ash
python indexer.py
`

### 5. Ejecutar la Aplicación Web
`ash
streamlit run app.py
`
La aplicación se abrirá automáticamente en tu navegador en http://localhost:8501.

---

## 📁 Estructura del Proyecto

`
FLEBITECH/
├── knowledge_base/                 # Base de conocimiento documental
│   ├── medicamentos.json           # 15 fármacos críticos estructurados (pH, osmolaridad, diluciones)
│   ├── escalas.md                  # Escala DIVA, Escala de Flebitis INS (0-4), algoritmo de punción
│   ├── protocolo_basico.md         # Protocolo de Hospitalización LaCardio (M-03-01-A-043)
│   └── casos_clinicos.md           # 3 Casos clínicos de toma de decisiones
│
├── backend/                        # Motor RAG y Lógica de Negocio
│   ├── indexer.py / indexer.py     # Script de indexación
│   ├── rag_engine.py               # Motor híbrido de búsqueda (TF-IDF + Entidades farmacológicas)
│   ├── prompt_system.py            # Guardrails clínicos y system prompt estricto
│   ├── groq_client.py              # Conector Groq API (Llama 3.3 70B) + Fallback didáctico
│   └── metrics.py                  # Analítica SQLite para detección de brechas
│
├── app.py                          # 🎯 Aplicación Streamlit completa
├── data/metrics.db                 # Base de datos local de métricas y consultas
├── .env                            # Variables de entorno (GROQ_API_KEY)
└── requirements.txt                # Dependencias mínimas
`

---

## 🛡️ Principio Clínico de Seguridad (Guardrail)
Flebitech opera bajo un **RAG estricto**: nunca inventa dosis ni datos clínicos. Si una consulta no está en los documentos indexados, responde obligatoriamente:
> *"ℹ️ Esa información no está disponible en el material de Flebitech. Te recomendamos consultar el protocolo institucional o a tu supervisor clínico."*
