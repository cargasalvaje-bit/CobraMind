import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64
from moviepy.editor import ImageSequenceClip
import tempfile
import numpy as np
import json
import os

# -------------------
# CONFIG
# -------------------
st.set_page_config(
    page_title="CobraMind",
    page_icon="assets/logo.png",
    layout="wide"
)

# Diseño CSS para forzar fondo blanco puro y eliminar bordes grises
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fondo blanco para toda la app */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Estilizar los inputs para que no tengan fondos grises pesados */
    div[data-baseweb="input"] {
        background-color: #FAFAFA !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------
# BASE DE DATOS LOCAL (JSON)
# -------------------
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users_data):
    with open(DB_FILE, "w") as f:
        json.dump(users_data, f, indent=4)

def save_current_user_state():
    if st.session_state.get("logged_in") and st.session_state.get("current_user"):
        users = load_users()
        username = st.session_state.current_user
        
        users[username]["page"] = st.session_state.page
        users[username]["messages"] = st.session_state.messages
        users[username]["conversations"] = st.session_state.conversations
        users[username]["cobra_credits"] = st.session_state.cobra_credits
        
        save_users(users)

# -------------------
# GESTIÓN DE SESIÓN
# -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None 

# -------------------
# PANTALLA DE AUTENTICACIÓN
# -------------------
if not st.session_state.logged_in:
    col_main_1, col_main_2, col_main_3 = st.columns([1, 2, 1])
    
    with col_main_2:
        st.write("") 
        st.write("") 
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Log in", use_container_width=True):
                st.session_state.auth_mode = "login"
        with col_btn2:
            if st.button("Create an account", use_container_width=True):
                st.session_state.auth_mode = "signup"

        if st.session_state.auth_mode == "login":
            st.markdown("### Log In")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Ingresar", use_container_width=True):
                users = load_users()
                if login_user in users and users[login_user]["password"] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.session_state.page = users[login_user].get("page", "chat")
                    st.session_state.messages = users[login_user].get("messages", [])
                    st.session_state.conversations = users[login_user].get("conversations", [])
                    st.session_state.cobra_credits = users[login_user].get("cobra_credits", 0)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        elif st.session_state.auth_mode == "signup":
            st.markdown("### Create an Account")
            new_user = st.text_input("Choose Username", key="new_user")
            new_pass = st.text_input("Choose Password", type="password", key="new_pass")
            
            if st.button("Registrar Cuenta", use_container_width=True):
                if new_user.strip() == "" or new_pass.strip() == "":
                    st.warning("Por favor rellena todos los campos.")
                else:
                    users = load_users()
                    if new_user in users:
                        st.error("El usuario ya existe. Elige otro.")
                    else:
                        users[new_user] = {
                            "password": new_pass,
                            "page": "chat",
                            "messages": [],
                            "conversations": [],
                            "cobra_credits": 1000 
                        }
                        save_users(users)
                        st.success("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
    st.stop() 

# -------------------
# CLIENTE API
# -------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
# FUNCIONES
# -------------------
def generate_summary(messages):
    try:
        user_text = "\n".join(
            [m["content"] for m in messages if m["role"] == "user"]
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                SYSTEM_PROMPT,
                {"role": "user", "content": f"Resume en 5 palabras: {user_text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except:
        return "Nueva conversación"
# -------------------
# SIDEBAR
# -------------------
with st.sidebar:
    st.markdown("## 🐍 CobraMind")
    st.markdown(f"👤 *Usuario: {st.session_state.current_user}*")

    if st.button("💬 Chat"):
        st.session_state.page = "chat"
        save_current_user_state()

    if st.button("📘 About CobraMind"):
        st.session_state.page = "about"
        save_current_user_state()

    if st.button("🏦 CobraCredits"):
        st.session_state.page = "credits"
        save_current_user_state()

    if st.button("🚪 Log Out"):
        save_current_user_state()
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.auth_mode = None
        st.rerun()

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
            save_current_user_state()

    st.markdown("### Conversaciones")

    for i, conv in enumerate(st.session_state.conversations):
        if st.button(conv["title"], key=f"conv_{i}"):
            st.session_state.messages = conv["messages"].copy()
            st.session_state.page = "chat"
            save_current_user_state()

    st.markdown("---")
    st.markdown("<h3 style='color:green'>💰 Créditos: {:,} 🐍</h3>".format(st.session_state.cobra_credits), unsafe_allow_html=True)

    st.markdown("---")
    st.sidebar.subheader("Generar contenido")

    # -------- IMAGEN --------
    image_prompt = st.text_input("Prompt para imagen", placeholder="Describe bien la imagen...", key="image_prompt")
    if st.button("Create Image"):
        cost_image = 333
        if st.session_state.cobra_credits < cost_image:
            st.warning("No tienes suficientes CobraCredits para generar una imagen.")
        elif image_prompt.strip():
            with st.spinner("Generando imagen..."):
                try:
                    response = client.images.generate(model="gpt-image-1", prompt=image_prompt, size="1024x1024")
                    st.session_state.cobra_credits -= cost_image
                    image_bytes = base64.b64decode(response.data.b64_json)
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=image_prompt)
                    save_current_user_state()
                except Exception as e:
                    st.error(f"Error generando imagen: {e}")
        else:
            st.warning("Escribe un prompt.")

    # -------- VIDEO --------
    video_prompt = st.text_input("Prompt para video", placeholder="Describe bien el video...", key="video_prompt")
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
                        response = client.images.generate(model="gpt-image-1", prompt=base_prompt + f", slight movement, frame {i+1}", size="1024x1024")
                        image_bytes = base64.b64decode(response.data.b64_json)
                        image = Image.open(io.BytesIO(image_bytes))
                        frames.append(image)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                        clip = ImageSequenceClip([np.array(f.convert("RGB")) for f in frames], fps=2)
                        clip.write_videofile(tmpfile.name, codec="libx264")
                        st.session_state.cobra_credits -= cost_video
                        st.success("Video listo 🎉")
                        st.video(tmpfile.name)
                        save_current_user_state()
                except Exception as e:
                    st.error(f"Error generando video: {e}")

# -------------------
# VISTAS DE PÁGINAS
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
                        model="gpt-4.1-mini",
                        messages=[SYSTEM_PROMPT] + st.session_state.messages,
                        stream=True
                    )
                    for chunk in stream:
                        if chunk.choices.delta.content:
                            full_response += chunk.choices.delta.content
                            placeholder.markdown(full_response)
                except:
                    full_response = "Error con la API."
                    placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})
                save_current_user_state()

elif st.session_state.page == "about":
    st.title("📘 About CobraMind")
    st.write("CobraMind es un asistente avanzado potenciado por inteligencia artificial.")
    st.write("Desarrollado por Lorenzo Mazzini.")

elif st.session_state.page == "credits":
    st.title("🏦 CobraCredits")
    st.write(f"Actualmente posees **{st.session_state.cobra_credits:,}** créditos CobraCredits.")



