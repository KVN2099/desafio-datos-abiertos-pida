import io
import os
import streamlit as st
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

st.title("Consulta sobre Documentos")

# Fixed UC volume configuration
CATALOG = "workspace"
SCHEMA = "default"
VOLUME = "unstructured_rag_pida"
volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

# Nota: El volumen de almacenamiento está preconfigurado

# Listar archivos disponibles
st.subheader("Archivos disponibles")
try:
    files = list(w.files.list_directory_contents(volume_path))

    if files:
        for file_item in files:
            file_name = os.path.basename(file_item.path)
            col1, col2 = st.columns([8, 1])
            with col1:
                st.text(file_name)
            with col2:
                if st.button("✕", key=f"delete_{file_item.path}"):
                    try:
                        w.files.delete(file_item.path)
                        st.success(f"Archivo eliminado: {file_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {str(e)}")
    else:
        st.info("No se encontraron archivos")

except Exception as e:
    st.error(f"Error al listar archivos: {str(e)}")

# Cargar archivos
st.subheader("Cargar archivo(s)")
uploaded_files = st.file_uploader("Seleccione archivo(s) para cargar", accept_multiple_files=True)

if uploaded_files and st.button("Cargar archivo(s) seleccionado(s)"):
    try:
        for uploaded_file in uploaded_files:
            # Read bytes reliably from Streamlit's UploadedFile
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name
            upload_path = f"{volume_path}/{file_name}"

            # Files API expects BinaryIO when passed positionally
            w.files.upload(upload_path, io.BytesIO(file_bytes), overwrite=True)

        st.success("Carga completada.")
        st.rerun()
    except Exception as e:
        st.error(f"Error al cargar archivo(s): {str(e)}")
