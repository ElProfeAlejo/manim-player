import streamlit as st
import os
import subprocess
import shutil
import uuid

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'editor'

if 'codigo_guardado' not in st.session_state:
    st.session_state.codigo_guardado = ""

def reiniciar_app():
    st.session_state.pantalla = 'editor'
    st.session_state.codigo_guardado = "" 

def ejecutar_manim(codigo, uid):
    st.info("🎬 Generando video con Manim... esto puede tardar.")
    
    script_name = f"script_{uid}.py"
    media_folder = f"media_{uid}"
    video_final = f"video_final_{uid}.mp4"
    
    with open(script_name, "w", encoding="utf-8") as f:
        f.write(codigo)
        
    try:
        cmd = f"manim -ql --media_dir ./{media_folder} {script_name} ManimTemplate"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        video_path = None
        for root, dirs, files in os.walk(media_folder):
            for file in files:
                if file.endswith(".mp4") and "ManimTemplate" in file:
                    video_path = os.path.join(root, file)
                    break
            if video_path:
                break
        
        if video_path and os.path.exists(video_path):
            shutil.copy(video_path, video_final)
            return video_final
        else:
            st.error("❌ Manim terminó, pero no se encontró el video generado.")
            st.code(result.stderr)
            return None            
    except subprocess.TimeoutExpired:
        st.error("⏳ Error: El renderizado superó los 2 minutos de límite.")
        return None
    except Exception as e:
        st.error(f"❌ Error crítico al ejecutar Manim: {str(e)}")
        return None

if st.session_state.pantalla == 'editor':
    code = st.text_area("Pega tu código de Manim aquí:", value=st.session_state.codigo_guardado, height=300)
    
    if st.button("Renderizar Video"):
        if not code.strip():
            st.warning("⚠️ Pega tu código de Manim primero.")
        else:
            st.session_state.codigo_guardado = code
            st.session_state.pantalla = 'resultado'
            st.rerun()
elif st.session_state.pantalla == 'resultado':
    ruta_del_video = ejecutar_manim(st.session_state.codigo_guardado, st.session_state.user_id)
    if ruta_del_video:
        st.video(ruta_del_video)
    
    st.button("Reiniciar", on_click=reiniciar_app)
