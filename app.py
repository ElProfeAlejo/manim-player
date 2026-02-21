import streamlit as st
import os
import subprocess
import uuid

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

user_id = st.session_state.user_id
code = st.text_area("Pega tu código de Manim aquí:", value="""from manim import *

# Configuración inicial de la escena
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_width = 16
config.frame_height = 9

class ManimTemplate(Scene):
    def construct(self):""", height=300)

if st.button("Renderizar Video"):
    with st.spinner("Renderizando... esto puede tardar un poco."):
        script_name = f"manim_script_{user_id}.py"
        media_dir = f"media_{user_id}"
        with open(script_name, "w", encoding="utf-8") as f:
            f.write(code)

        command = f"manim -ql --media_dir ./{media_dir} {script_name} ManimTemplate"
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
            video_path = f"{media_dir}/videos/{script_name[:-3]}/480p15/ManimTemplate.mp4"
            if os.path.exists(video_path):
                st.success("¡Renderizado completo!")
                st.video(video_path)
            elif result.returncode == -9:
                st.error("❌ El servidor de Streamlit mató el proceso porque superó el límite de 1GB de RAM.")
            else:
                st.error("Error al procesar el video. Consola:")
                st.code(result.stderr)
        except subprocess.TimeoutExpired:
            st.error("⏳ El renderizado tardó más de 2 minutos y fue cancelado para evitar bloquear la app.")
