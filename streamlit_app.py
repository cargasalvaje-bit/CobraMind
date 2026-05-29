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
                        response = client.images.generate(
                            model="gpt-image-1", 
                            prompt=base_prompt + f", slight movement, frame {i+1}", 
                            size="1024x1024",
                            response_format="b64_json"
                        )
                        
                        image_bytes = base64.b64decode(response.data[0].b64_json)
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
                        model="gpt-4o-mini",
                        messages=[SYSTEM_PROMPT] + st.session_state.messages,
                        stream=True
                    )
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            placeholder.markdown(full_response)
                except Exception as e:
                    full_response = "Error con la API."
                    placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})
                save_current_user_state()

elif st.session_state.page == "about":
    st.title("📘 About CobraMind")
    
    st.markdown("### What it offers")
    st.write("CobraMind is an advanced artificial intelligence assistant designed to seamlessly optimize your workflow. It features multi-modal capabilities allowing users to engage in context-aware conversations, generate custom visual assets from raw text descriptions, and stitch together seamless cinematic video compositions natively within a single user interface.")
    
    st.markdown("### Behind the Code")
    st.write("This entire software ecosystem was architected and deployed by Lorenzo Mazzini, a passionate developer from Peru. By bridging complex backend integrations like open-source video renderers and OpenAI state-of-the-art language models, this platform transforms intricate API architectures into a fluid, user-friendly computational experience.")
    
    st.markdown("### The Inspiration")
    st.write("The platform was inspired by a core vision to build a continuous, hyper-responsive digital companion that transcends the limits of standard text chatbots. It is driven by the ambition to build toolsets that empower individual builders, unlocking new horizons of scalable creative expression and professional productivity.")

elif st.session_state.page == "credits":
    st.title("🏦 CobraCredits Bank")
    st.write(f"Actualmente posees **{st.session_state.cobra_credits:,}** créditos CobraCredits.")
    
    st.markdown("---")
    st.subheader("🛒 Recargar Créditos")
    st.write("Selecciona un paquete para añadir más fondos a tu cuenta inmediatamente:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("### 🥉 Paquete Básico")
        st.write("➕ 1,000 CobraCredits")
        if st.button("Comprar 1k Créditos", use_container_width=True):
            st.session_state.cobra_credits += 1000
            save_current_user_state()
            st.success("¡Se han añadido 1,000 créditos a tu cuenta! 🎉")
            st.rerun()
            
    with col_p2:
        st.markdown("### 🥈 Paquete Avanzado")
        st.write("➕ 5,000 CobraCredits")
        if st.button("Comprar 5k Créditos", use_container_width=True):
            st.session_state.cobra_credits += 5000
            save_current_user_state()
            st.success("¡Se han añadido 5,000 créditos a tu cuenta! 🚀")
            st.rerun()
            
    with col_p3:
        st.markdown("### 🥇 Paquete Cobra Master")
        st.write("➕ 20,000 CobraCredits")
        if st.button("Comprar 20k Créditos", use_container_width=True):
            st.session_state.cobra_credits += 20000
            save_current_user_state()
            st.success("¡Se han añadido 20,000 créditos a tu cuenta! 🐍")
            st.rerun()
