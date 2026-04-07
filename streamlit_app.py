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
# FONDO ANIMADO (NUEVO)
# -------------------
particles_js = """
<style>
#particles-js {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
    top: 0;
    left: 0;
}
</style>

<div id="particles-js"></div>

<script src="https://cdn.jsdelivr.net/npm/tsparticles@2/tsparticles.bundle.min.js"></script>

<script>
tsParticles.load("particles-js", {
    fpsLimit: 60,
    interactivity: {
        events: {
            onHover: {
                enable: true,
                mode: "grab"
            },
            onClick: {
                enable: true,
                mode: "push"
            }
        },
        modes: {
            grab: {
                distance: 180,
                links: {
                    opacity: 0.7
                }
            },
            push: {
                quantity: 4
            }
        }
    },
    particles: {
        color: {
            value: "#ffffff"
        },
        links: {
            color: "#ffffff",
            distance: 150,
            enable: true,
            opacity: 0.2,
            width: 1
        },
        move: {
            enable: true,
            speed: 0.6
        },
        number: {
            density: {
                enable: true,
                area: 800
            },
            value: 80
        },
        opacity: {
            value: 0.2
        },
        size: {
            value: { min: 1, max: 3 }
        }
    },
    detectRetina: true
});
</script>
"""

st.components.v1.html(particles_js, height=0)

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
            model="gpt-4.1-mini",
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
    image_prompt = st.text_input("Prompt para imagen", key="image_prompt")
    if st.button("Create Image"):
        cost_image = 333
        if st.session_state.cobra_credits < cost_image:
            st.warning("No tienes suficientes CobraCredits.")
        elif image_prompt.strip():
            response = client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                size="1024x1024"
            )
            st.session_state.cobra_credits -= cost_image
            image_bytes = base64.b64decode(response.data[0].b64_json)
            st.image(Image.open(io.BytesIO(image_bytes)))

    # -------- VIDEO --------
    video_prompt = st.text_input("Prompt para video", key="video_prompt")
    if st.button("Create Video"):
        cost_video = 2000
        if st.session_state.cobra_credits < cost_video:
            st.warning("No tienes suficientes CobraCredits.")
        elif video_prompt.strip():
            frames = []
            base_prompt = f"{video_prompt}, same character"
            for i in range(6):
                response = client.images.generate(
                    model="gpt-image-1",
                    prompt=base_prompt + f", frame {i}",
                    size="1024x1024"
                )
                image_bytes = base64.b64decode(response.data[0].b64_json)
                frames.append(Image.open(io.BytesIO(image_bytes)))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                clip = ImageSequenceClip(
                    [np.array(f.convert("RGB")) for f in frames],
                    fps=2
                )
                clip.write_videofile(tmpfile.name, codec="libx264")
                st.session_state.cobra_credits -= cost_video
                st.video(tmpfile.name)

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
        if st.session_state.cobra_credits >= cost_message:
            st.session_state.cobra_credits -= cost_message
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[SYSTEM_PROMPT] + st.session_state.messages
                )
                reply = response.choices[0].message.content
                st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})
