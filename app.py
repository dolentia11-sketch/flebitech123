# -*- coding: utf-8 -*-
"""
Flebitech MVP — Asistente Educativo sobre Flebitis Química y Terapia Intravenosa
Desarrollado en alianza académica-clínica entre Universidad de La Sabana y laCardio.
"""

import os
import sys
import uuid
import streamlit as st

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.rag_engine import RAGEngine
from backend.groq_client import GroqClient
from backend.prompt_system import is_knowledge_gap
from backend.metrics import log_question, get_session_stats, get_recent_interactions, get_knowledge_gaps

# 1. Configuración de página
st.set_page_config(
    page_title="Flebitech — Asistente de Flebitis Química",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización de Estado de Sesión
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! Soy el **asistente de Flebitech**, tu tutor clínico sobre prevención de flebitis química y accesos vasculares periféricos. ¿En qué puedo orientarte hoy?",
            "sources": ["protocolo_basico.md"],
            "is_valid": True
        }
    ]

# 3. Inicializar motores (con caché de Streamlit)
@st.cache_resource
def load_rag():
    return RAGEngine(knowledge_base_path="./knowledge_base/")

@st.cache_resource
def load_groq():
    return GroqClient()

rag = load_rag()
groq = load_groq()

# 4. Estilos CSS personalizados
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #003366;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4A5568;
        margin-bottom: 1.2rem;
    }
    .badge-lacardio {
        background-color: #002B66;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-sabana {
        background-color: #004080;
        color: #FFD100;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .chat-card {
        background-color: #F8FAFC;
        border-left: 4px solid #0056B3;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .gap-alert {
        background-color: #FFF5F5;
        border-left: 4px solid #E53E3E;
        padding: 12px 16px;
        border-radius: 8px;
        color: #9B2C2C;
    }
</style>
""", unsafe_allow_html=True)

# 5. Header Principal
col_title, col_logos = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-title">🏥 Flebitech — Tutor de Flebitis Química</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Herramienta conversacional de apoyo educativo para enfermería · '
        '<span class="badge-lacardio">laCardio</span> <span class="badge-sabana">Univ. de La Sabana</span></div>',
        unsafe_allow_html=True
    )
with col_logos:
    st.caption("🔒 RAG Estricto: Respuestas 100% basadas en protocolos institucionales.")

# 6. Barra Lateral (Sidebar)
with st.sidebar:
    st.subheader("📊 Monitor de Aprendizaje")
    stats = get_session_stats(st.session_state.session_id)
    
    st.metric(label="Preguntas en esta sesión", value=stats["total_preguntas"])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric(label="Respondidas", value=stats["respondidas"])
    with col_s2:
        st.metric(label="Brechas", value=stats["brechas_detectadas"])
        
    st.progress(stats["tasa_resolucion"] / 100.0)
    st.caption(f"Tasa de resolución documental: **{stats['tasa_resolucion']}%**")
    
    st.markdown("---")
    st.subheader("⚙️ Estado del Motor")
    if groq.client is not None:
        st.success(f"🟢 Groq LLM Activo ({groq.model})")
    else:
        st.info("🟡 Modo Determinista RAG (Agrega GROQ_API_KEY en .env para LLM en tiempo real)")
    
    st.caption(f"📚 {len(rag.chunks)} fragmentos clínicos indexados")
    st.caption(f"💊 {len(rag.medications)} fármacos críticos en base")
    
    st.markdown("---")
    st.caption("⚠️ **Aviso de Seguridad**: Flebitech es una herramienta didáctica para enfermería y no sustituye el criterio clínico ni los protocolos institucionales de laCardio.")

# 7. Pestañas de Navegación
tab_chat, tab_meds, tab_cases, tab_analytics = st.tabs([
    "💬 Chat Educativo",
    "💊 Biblioteca de Medicamentos",
    "🎯 Casos Clínicos Simulados",
    "📈 Métricas y Brechas"
])

# ==========================================================
# TAB 1: CHAT EDUCATIVO
# ==========================================================
with tab_chat:
    st.markdown("##### 💡 Preguntas Frecuentes Rápidas (Haz clic para consultar):")
    cols_sug = st.columns(4)
    
    sugeridas = [
        "¿Qué es la valoración DIVA y cuándo usarla?",
        "¿Qué medicamentos requieren vía central obligatoria?",
        "¿Cómo se clasifica la flebitis según la escala INS?",
        "¿Cuáles son los cuidados con la Vancomicina e infusión?"
    ]
    
    pregunta_click = None
    for i, preg in enumerate(sugeridas):
        with cols_sug[i]:
            if st.button(preg, key=f"sug_{i}", use_container_width=True):
                pregunta_click = preg

    st.markdown("---")

    # Mostrar historial de mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.caption(f"📄 Fuentes: {', '.join(msg['sources'])}")

    # Input del usuario (escrito o por botón sugerido)
    prompt_input = st.chat_input("Escribe tu pregunta sobre flebitis química, medicamentos o catéteres...")
    user_query = pregunta_click or prompt_input

    if user_query:
        # 1. Agregar y mostrar mensaje de usuario
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # 2. Recuperar del RAG
        context, sources, has_match = rag.search(user_query, top_k=3)

        # 3. Consultar Groq / Fallback
        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conocimiento de Flebitech..."):
                response_text, latency = groq.ask(
                    user_query,
                    context,
                    has_relevant_content=has_match,
                    history=st.session_state.messages[:-1]
                )
                
                is_gap = is_knowledge_gap(response_text) or not has_match
                
                st.markdown(response_text)
                if sources and not is_gap:
                    st.caption(f"📚 Fuentes consultadas: {', '.join(sources)} · Latencia: {latency:.0f} ms")
                elif is_gap:
                    st.warning("⚠️ Pregunta fuera de la base documental indexada. Registrada como brecha de conocimiento.")
                
                # 4. Registrar en base de datos de analítica SQLite
                log_question(
                    query=user_query,
                    response=response_text,
                    session_id=st.session_state.session_id,
                    had_answer=not is_gap,
                    source_docs=",".join(sources),
                    latency_ms=latency
                )

        # 5. Guardar en memoria de sesión
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "sources": sources if not is_gap else [],
            "is_valid": not is_gap
        })
        st.rerun()

# ==========================================================
# TAB 2: BIBLIOTECA DE MEDICAMENTOS
# ==========================================================
with tab_meds:
    st.subheader("💊 Base Estructurada de Medicamentos Críticos")
    st.markdown("Consulta los parámetros físico-químicos (pH, osmolaridad, diluciones y riesgos de flebitis).")
    
    filtro_med = st.text_input("🔍 Buscar medicamento por nombre o grupo:", "")
    
    meds_filtrados = [
        m for m in rag.medications
        if filtro_med.lower() in m.get("nombre", "").lower() or filtro_med.lower() in m.get("grupo", "").lower()
    ]
    
    for med in meds_filtrados:
        with st.expander(f"📌 **{med.get('nombre')}** — {med.get('grupo')} (Riesgo: {med.get('riesgo_flebitis')})"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**pH:** {med.get('ph')}")
                st.markdown(f"**Osmolaridad:** {med.get('osmolaridad')}")
                st.markdown(f"**Tonicidad:** {med.get('tonicidad')}")
                st.markdown(f"**Vía Recomendada:** {med.get('via_recomendada')}")
            with col_m2:
                st.markdown(f"**Diluyente:** {med.get('diluyente_recomendado')}")
                st.markdown(f"**Volumen Mínimo:** {med.get('volumen_minimo_dilucion')}")
                st.markdown(f"**Tiempo de Infusión:** {med.get('tiempo_infusion_minimo')}")
            
            st.info(f"💡 **Recomendaciones de Enfermería:** {med.get('observaciones_enfermeria')}")

# ==========================================================
# TAB 3: CASOS CLÍNICOS SIMULADOS
# ==========================================================
with tab_cases:
    st.subheader("🎯 Simulador de Toma de Decisiones Clínicas")
    st.markdown("Pon a prueba tu criterio clínico en situaciones reales de enfermería.")
    
    caso_sel = st.selectbox(
        "Selecciona un caso clínico para resolver:",
        [
            "Caso 1: Paciente con DIVA elevado y prescripción de Vancomicina",
            "Caso 2: Paciente con dolor agudo durante infusión de KCl (Flebitis INS)",
            "Caso 3: Nutrición Parenteral e Hiperosmolaridad Crítica"
        ]
    )
    
    if "Caso 1" in caso_sel:
        st.markdown("""
        **Escenario:** Mujer de 68 años hospitalizada por neumonía. Orden médica: *Vancomicina 1 g IV c/12h por 10 días*.
        La paciente tiene historial de accesos venosos difíciles, venas no visibles ni palpables (DIVA = 4).
        
        **¿Cuál es la conducta de enfermería más adecuada?**
        """)
        opcion = st.radio(
            "Selecciona tu decisión:",
            [
                "A) Canalizar a ciegas una vénula de 1 mm en el dorso de la mano con catéter 18G.",
                "B) Solicitar valoración por equipo de accesos vasculares para Línea Media (Midline) o PICC guiado por ecografía.",
                "C) Administrar la vancomicina en bolo rápido directo para terminar pronto."
            ]
        )
        if st.button("Evaluar Decisión (Caso 1)"):
            if "B)" in opcion:
                st.success("✅ **¡Correcto!** Por el score DIVA >= 4 y la duración del tratamiento (10 días) con un fármaco de pH muy ácido (2.5-4.5), la indicación de excelencia es un acceso vascular intermedio o central guiado por ultrasonido.")
            else:
                st.error("❌ **Incorrecto.** Canalizar vénulas distales o pasar en bolo rápido causa flebitis química severa inmediata, extravasación o síndrome del hombre rojo.")

    elif "Caso 2" in caso_sel:
        st.markdown("""
        **Escenario:** Paciente con reposición de *Cloruro de Potasio (KCl) 40 mEq en 500 ml SSN*.
        A las 2 horas presenta eritema de 4 cm y dolor ardoroso en sitio de punción (Flebitis INS Grado 2).
        
        **¿Cuál es la conducta inmediata?**
        """)
        opcion2 = st.radio(
            "Selecciona tu decisión:",
            [
                "A) Aumentar la velocidad para terminar más rápido.",
                "B) Detener la infusión inmediatamente, RETIRAR el catéter venoso periférico y rotar de extremidad con mayor dilución.",
                "C) Solo aplicar hielo sobre el catéter sin retirarlo."
            ]
        )
        if st.button("Evaluar Decisión (Caso 2)"):
            if "B)" in opcion2:
                st.success("✅ **¡Correcto!** En la escala INS, un Grado 2 (dolor + eritema/edema) exige el **retiro obligatorio e inmediato** del catéter periférico para prevenir progresión a cordón fibroso o trombosis.")
            else:
                st.error("❌ **Incorrecto.** Nunca se debe forzar una infusión irritante ni mantener un catéter con signos de flebitis Grado 2.")

    elif "Caso 3" in caso_sel:
        st.markdown("""
        **Escenario:** Paciente con indicación de *Nutrición Parenteral Total (NPT)* con osmolaridad calculada de **1250 mOsm/L**. El médico interno pide infundirla por el catéter periférico 18G en antebrazo.
        
        **¿Cuál es tu respuesta de enfermería?**
        """)
        opcion3 = st.radio(
            "Selecciona tu decisión:",
            [
                "A) Conectar la NPT de inmediato al catéter 18G porque es de buen calibre.",
                "B) Rechazar la infusión periférica: soluciones con osmolaridad > 900 mOsm/L exigen Vía Central exclusiva.",
                "C) Diluir la NPT con agua de grifo."
            ]
        )
        if st.button("Evaluar Decisión (Caso 3)"):
            if "B)" in opcion3:
                st.success("✅ **¡Correcto!** Toda solución con osmolaridad superior a 900 mOsm/L está estrictamente contraindicada por vía periférica porque produce lisis endotelial acelerada.")
            else:
                st.error("❌ **Incorrecto.** Infundir NPT > 900 mOsm/L en vena periférica destruye la capa íntima vascular en pocas horas.")

# ==========================================================
# TAB 4: MÉTRICAS Y DETECCIÓN DE BRECHAS
# ==========================================================
with tab_analytics:
    st.subheader("📈 Analítica de Consultas y Brechas de Conocimiento")
    st.markdown("Registro continuo de dudas frecuentes para retroalimentación docente y actualización de guías.")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown("##### 🕒 Últimas Consultas Realizadas:")
        recent = get_recent_interactions(limit=8)
        if recent:
            for r in recent:
                icon = "✅" if r["had_answer"] else "⚠️"
                st.markdown(f"**{icon} [{r['timestamp']}]** ({r['topic']}): *{r['query']}*")
        else:
            st.info("Aún no hay interacciones registradas en esta sesión.")
            
    with col_a2:
        st.markdown("##### 🚨 Brechas Detectadas (Preguntas sin respuesta en base):")
        gaps = get_knowledge_gaps(limit=8)
        if gaps:
            for g in gaps:
                st.markdown(f'<div class="gap-alert">📌 <b>{g["timestamp"]}</b> ({g["topic"]}): {g["query"]}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 No se han detectado brechas de conocimiento sin responder.")
