import io
import os
import streamlit as st
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

st.title("UC Volume File Manager")

# Fixed UC volume configuration
CATALOG = "workspace"
SCHEMA = "default"
VOLUME = "unstructured_rag_pida"
volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

st.caption(f"Volume: {CATALOG}.{SCHEMA}.{VOLUME}")

# Display all files in volume
st.subheader("Files in Volume")
try:
    files = list(w.files.list_directory_contents(volume_path))

    if files:
        for file_item in files:
            file_name = os.path.basename(file_item.path)
            st.text(file_name)
    else:
        st.info("No files found in this volume")

except Exception as e:
    st.error(f"Error listing files: {str(e)}")

# Upload section
st.subheader("Upload File(s)")
uploaded_files = st.file_uploader("Select file(s) to upload", accept_multiple_files=True)

if uploaded_files and st.button("Upload selected file(s)"):
    try:
        for uploaded_file in uploaded_files:
            # Read bytes reliably from Streamlit's UploadedFile
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name
            upload_path = f"{volume_path}/{file_name}"

            # Files API expects BinaryIO when passed positionally
            w.files.upload(upload_path, io.BytesIO(file_bytes), overwrite=True)

        st.success("Upload complete.")
        st.rerun()
    except Exception as e:
        st.error(f"Error uploading file(s): {str(e)}")
