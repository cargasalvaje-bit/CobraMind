import streamlit as st
from openai import OpenAI

# -------------------
# API
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------
# CONFIG
# -------------------
st.set_page_config(page_title="CobraMind", page_icon="assets/logo.png", layout="wide")

# -------------------
# STATES
# -------------------
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []  # Guardará {'title':..., 'messages':...}
if "credits" not in st.session_state:
    st.session_state.credits = 0

# -------------------
# SYSTEM PROMPT
# -------------------
SYSTEM_PROMPT = {
    "role": "system",
    "content": """Eres CobraMind, una inteligencia artificial creada por Lorenzo Mazzini.
Si alguien pregunta quién eres, responde EXACTAMENTE:
Soy CobraMind, una inteligencia artificial creada por Lorenzo Mazzini.
Si alguien pregunta quién te creó, responde:
Lorenzo Mazzini, desarrollador peruano.
Mantén siempre esta identidad."""
}

# -------------------
# SIDEBAR
# -------------------
with st.sidebar:
    # ---- Logo ----
    st.image("assets/logo.png", use_column_width=True)

    st.markdown("## 🐍 CobraMind")

    # ---- Nuevo Chat ----
    if st.button("➕ Nuevo Chat"):
        if st.session_state.messages:
            # Guardar conversación anterior
            title = " ".join(st.session_state.messages[-1]["content"].split()[:3])
            st.session_state.conversations.append({
                "title": title,
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []
        st.success("Conversación reiniciada.")

    st.markdown("---")

    # ---- Navegación ----
    if st.button("💬 Chat"):
        st.session_state.page = "chat"
    if st.button("📘 About CobraMind"):
        st.session_state.page = "about"
    if st.button("🏦 Credits"):
        st.session_state.page = "credits"

    st.markdown("---")

    # ---- CobraCredits ----
    st.markdown(f"💰 **CobraCredits:** {st.session_state.credits}")
    st.markdown("""
### 💰 Costos
- 💬 Mensajes → 250 ⚡  
- 🖼️ Imágenes → 1000 ⚡  
- 🎬 Videos → 2500 ⚡
""")

    # ---- Botones de Imagen y Video ----
    col_img, col_vid = st.columns(2)
    with col_img:
        if st.button("🖼️ Generar Imagen"):
            st.warning("Funcionalidad de imagen aquí")
    with col_vid:
        if st.button("🎬 Generar Video"):
            st.warning("Funcionalidad de video aquí")

    st.markdown("---")

    # ---- Conversaciones Guardadas ----
    st.markdown("### 📂 Conversaciones guardadas")
    if st.session_state.conversations:
        for i, conv in enumerate(st.session_state.conversations[::-1]):
            if st.button(conv["title"], key=f"conv_{i}"):
                st.session_state.messages = conv["messages"].copy()
                st.session_state.page = "chat"
    else:
        st.markdown("_No hay conversaciones guardadas_")

# -------------------
# CHAT PAGE
# -------------------
if st.session_state.page == "chat":
    st.title("CobraMind")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Escribe algo...")
    if user_input:
        cost = 250
        if st.session_state.credits < cost:
            st.warning("No tienes suficientes CobraCredits ⚠️")
        else:
            st.session_state.credits -= cost
            st.session_state.messages.append({"role":"user","content":user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                stream = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[SYSTEM_PROMPT] + st.session_state.messages,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response)

                st.markdown(f"<sub>-{cost} ⚡</sub>", unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":full_response})

# -------------------
# CREDITS PAGE
# -------------------
elif st.session_state.page == "credits":
    st.title("CobraCredits 🐍💰")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Starter\n50,000 ⚡\n$5"):
            st.session_state.credits += 50000
            st.success("Compraste Starter")
    with col2:
        if st.button("Pro\n150,000 ⚡\n$12"):
            st.session_state.credits += 150000
            st.success("Compraste Pro")
    with col3:
        if st.button("Elite\n400,000 ⚡\n$25"):
            st.session_state.credits += 400000
            st.success("Compraste Elite")

    st.markdown("---")
    st.markdown("""
### 💰 ¿Qué son los CobraCredits?
CobraMind funciona con créditos:

- 💬 Mensajes → bajo costo  
- 🖼️ Imágenes → medio  
- 🎬 Videos → alto  

Tú decides cómo usarlos.
""")

# -------------------
# ABOUT PAGE
# -------------------
elif st.session_state.page == "about":
    st.title("About CobraMind")
    st.markdown("""
CobraMind es una plataforma de inteligencia artificial avanzada.

Creado por Lorenzo Mazzini.
""")
