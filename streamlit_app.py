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
st.set_page_config(
    page_title="CobraMind",
    page_icon="assets/logo.png",
    layout="wide"
)

# -------------------
# STATES
# -------------------
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "cobra_credits" not in st.session_state:
    st.session_state.cobra_credits = 0

# -------------------
# SYSTEM PROMPT
# -------------------
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Eres CobraMind, una inteligencia artificial creada por Lorenzo Mazzini. 
Si alguien pregunta quién eres, responde EXACTAMENTE: Soy CobraMind, una inteligencia artificial creada por Lorenzo Mazzini. 
Si alguien pregunta quién te creó, responde: Lorenzo Mazzini, desarrollador peruano. 
Mantén siempre esta identidad.
"""
}

# -------------------
# RESUMEN CHAT
# -------------------
def generate_summary(messages):
    try:
        user_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # 👈 cambiado
            messages=[SYSTEM_PROMPT, {"role": "user", "content": f"Resume en 5 palabras: {user_text}"}]
        )
        return response.choices[0].message.content.strip()
    except:
        return "Nueva conversación"

# -------------------
# FUNCIÓN REDONDEAR CREDITOS
# -------------------
def round_down_10(n):
    return n - (n % 10)

# -------------------
# SIDEBAR
# -------------------
with st.sidebar:
    st.markdown("## 🐍 CobraMind")

    if st.button("💬 Chat"):
        st.session_state.page = "chat"
    if st.button("📘 About CobraMind"):
        st.session_state.page = "about"
    if st.button("🏦 CobraCredits"):
        st.session_state.page = "credits"

    st.markdown("---")

    if st.button("➕ Nuevo Chat"):
        if st.session_state.messages:
            title = generate_summary(st.session_state.messages)
            st.session_state.conversations.append({
                "title": title,
                "messages": st.session_state.messages.copy()
            })
            st.session_state.messages = []
            st.session_state.page = "chat"

    st.markdown("### Conversaciones")
    for i, conv in enumerate(st.session_state.conversations):
        if st.button(conv["title"], key=f"conv_{i}"):
            st.session_state.messages = conv["messages"].copy()
            st.session_state.page = "chat"

    st.markdown("---")
    st.markdown("<h3 style='color:green'>💰 Créditos: {:,} 🐍</h3>".format(st.session_state.cobra_credits), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Generar contenido")

    # -------- IMAGEN --------
    image_prompt = st.text_input(
        "Prompt para imagen",
        placeholder="Describe bien la imagen...",
        key="image_prompt"
    )
    if st.button("Create Image"):
        cost_image = 333
        if st.session_state.cobra_credits < cost_image:
            st.warning("No tienes suficientes CobraCredits para generar una imagen.")
        elif image_prompt.strip():
            with st.spinner("Generando imagen..."):
                try:
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=image_prompt,
                        size="1024x1024"
                    )
                    st.session_state.cobra_credits -= cost_image
                    image_bytes = base64.b64decode(response.data[0].b64_json)
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=image_prompt)
                except Exception as e:
                    st.error(f"Error generando imagen: {e}")
        else:
            st.warning("Escribe un prompt.")

    # -------- VIDEO --------
    video_prompt = st.text_input(
        "Prompt para video",
        placeholder="Describe bien el video...",
        key="video_prompt"
    )
    if st.button("Create Video"):
        cost_video = 2000
        if st.session_state.cobra_credits < cost_video:
            st.warning("No tienes suficientes CobraCredits para generar un video.")
        elif video_prompt.strip():
            with st.spinner("Generando video..."):
                frames = []
                try:
                    base_prompt = f"{video_prompt}, same character, same style, smooth animation, cinematic"
                    total_frames = 6

                    for i in range(total_frames):
                        st.write(f"Frame {i+1}/{total_frames}")
                        response = client.images.generate(
                            model="gpt-image-1",
                            prompt=base_prompt + f", slight movement, frame {i+1}",
                            size="1024x1024"
                        )
                        image_bytes = base64.b64decode(response.data[0].b64_json)
                        image = Image.open(io.BytesIO(image_bytes))
                        frames.append(image)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                        clip = ImageSequenceClip(
                            [np.array(f.convert("RGB")) for f in frames],
                            fps=2
                        )
                        clip.write_videofile(tmpfile.name, codec="libx264")

                        st.session_state.cobra_credits -= cost_video
                        st.success("Video listo 🎉")
                        st.video(tmpfile.name)

                except Exception as e:
                    st.error(f"Error generando video: {e}")

# -------------------
# CHAT
# -------------------
if st.session_state.page == "chat":
    st.image("assets/logo.png", width=120)
    st.title("CobraMind")
    st.caption("AI Assistant • Powered by OpenAI")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Escribe algo...")
    if user_input:
        cost_message = 50
        if st.session_state.cobra_credits < cost_message:
            st.warning("No tienes suficientes CobraCredits para enviar un mensaje.")
        else:
            st.session_state.cobra_credits -= cost_message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                try:
                    stream = client.chat.completions.create(
                        model="gpt-4.1-mini",  # 👈 cambiado
                        messages=[SYSTEM_PROMPT] + st.session_state.messages,
                        stream=True
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            placeholder.markdown(full_response)
                except:
                    full_response = "Error con la API."
                    placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})

# -------------------
# ABOUT
# -------------------
elif st.session_state.page == "about":
    st.title("About CobraMind")
    st.markdown("""
CobraMind es una plataforma de inteligencia artificial de nueva generación diseñada para transformar la manera en que las personas piensan, crean y trabajan. 
No es solo un chatbot, sino un sistema avanzado capaz de comprender el contexto, adaptarse al usuario y ofrecer soluciones reales en tiempo real. 
Impulsada por modelos modernos como GPT-4.1, CobraMind combina velocidad, precisión y una experiencia intuitiva para ofrecer resultados de alta calidad. 
Además CobraMind ofrece un código para ajustarse a su entorno y tipo de respuesta.

---

### Capacidades avanzadas
CobraMind genera contenido, resuelve problemas, explica conceptos y crea código. También incluye generación de imágenes, video, automatización y herramientas multimedia.

---

### Por qué CobraMind
Enfocada en rendimiento, simplicidad y evolución constante.

---

### Visión
Convertirse en una de las plataformas de IA más completas del mundo para ayudar a diversas personas.

---

### Creado por Lorenzo Mazzini.
""")

# -------------------
# COBRACREDITS
# -------------------
elif st.session_state.page == "credits":
    st.title("CobraCredits 🏦")
    st.markdown("<h2 style='color:green; text-align:center;'>💰 Créditos actuales: {:,} 🐍</h2>".format(st.session_state.cobra_credits), unsafe_allow_html=True)

    st.markdown("### Packs disponibles")
    
    col1, col2, col3 = st.columns(3)

    mini_credits = round_down_10(8000)
    pro_credits = round_down_10(32000)
    elite_credits = round_down_10(200000)

    with col1:
        if st.button(f"Mini Pack - 5 USD - {mini_credits:,} créditos"):
            st.session_state.cobra_credits += mini_credits
            st.success("Seleccionaste Mini Pack")
    with col2:
        if st.button(f"Pro Pack - 20 USD - {pro_credits:,} créditos"):
            st.session_state.cobra_credits += pro_credits
            st.success("Seleccionaste Pro Pack")
    with col3:
        if st.button(f"Elite Pack - 100 USD - {elite_credits:,} créditos"):
            st.session_state.cobra_credits += elite_credits
            st.success("Seleccionaste Elite Pack")
