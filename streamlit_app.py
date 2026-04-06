import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64
from moviepy.editor import ImageSequenceClip
import tempfile
import numpy as np

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
    st.session_state.conversations = []

if "credits" not in st.session_state:
    st.session_state.credits = 0  # saldo inicial ahora es 0

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
    st.markdown("## 🐍 CobraMind")

    if st.button("💬 Chat"):
        st.session_state.page = "chat"

    if st.button("📘 About CobraMind"):
        st.session_state.page = "about"

    if st.button("🏦 Credits"):
        st.session_state.page = "credits"

    st.markdown("---")
    st.markdown(f"💰 **CobraCredits:** {st.session_state.credits}")
    st.markdown("---")

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
            st.session_state.messages.append({"role": "user", "content": user_input})

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

            st.session_state.messages.append({"role": "assistant", "content": full_response})

# -------------------
# CREDITS PAGE
# -------------------
elif st.session_state.page == "credits":

    st.title("CobraCredits 🐍💰")

    st.markdown(f"💰 **Créditos actuales:** {st.session_state.credits}")

    # Botones de compra
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Starter\n50,000 ⚡\n$5"):
            st.session_state.credits += 50000
            st.success("Compraste Starter: +50,000 ⚡")

    with col2:
        if st.button("Pro\n150,000 ⚡\n$12"):
            st.session_state.credits += 150000
            st.success("Compraste Pro: +150,000 ⚡")

    with col3:
        if st.button("Elite\n400,000 ⚡\n$25"):
            st.session_state.credits += 400000
            st.success("Compraste Elite: +400,000 ⚡")

    st.markdown("---")

    st.markdown("""
### 💰 ¿Qué son los CobraCredits?

CobraMind funciona con créditos:

- 💬 **Mensajes** → bajo costo  
- 🖼️ **Imágenes** → medio costo  
- 🎬 **Videos** → alto costo  

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
