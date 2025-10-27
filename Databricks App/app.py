import io
import os
import streamlit as st
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

st.title("UC Volume File Manager")

# Volume selection
volume_path_input = st.text_input(
    "Enter volume path (catalog.schema.volume):",
    placeholder="main.default.my_volume"
)

if volume_path_input:
    parts = volume_path_input.strip().split(".")
    if len(parts) == 3:
        catalog, schema, volume_name = parts
        volume_path = f"/Volumes/{catalog}/{schema}/{volume_name}"
        
        # Display all files in volume
        st.subheader("Files in Volume")
        try:
            files = list(w.files.list_directory_contents(volume_path))
            
            if files:
                for file_item in files:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        file_name = os.path.basename(file_item.path)
                        st.text(file_name)
                    
                    with col2:
                        # Download button
                        if st.button("Download", key=f"download_{file_item.path}"):
                            response = w.files.download(file_item.path)
                            file_data = response.contents.read()
                            st.download_button(
                                label="Save file",
                                data=file_data,
                                file_name=file_name,
                                key=f"save_{file_item.path}"
                            )
                    
                    with col3:
                        # Delete button
                        if st.button("Delete", key=f"delete_{file_item.path}"):
                            w.files.delete(file_item.path)
                            st.success(f"Deleted {file_name}")
                            st.rerun()
            else:
                st.info("No files found in this volume")
                
        except Exception as e:
            st.error(f"Error listing files: {str(e)}")
        
        # Upload section
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Select file to upload")
        
        if uploaded_file and st.button("Upload"):
            try:
                file_bytes = uploaded_file.read()
                binary_data = io.BytesIO(file_bytes)
                file_name = uploaded_file.name
                upload_path = f"{volume_path}/{file_name}"
                
                w.files.upload(upload_path, binary_data, overwrite=True)
                st.success(f"Successfully uploaded {file_name}")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error uploading file: {str(e)}")
    else:
        st.warning("Please enter volume path in format: catalog.schema.volume")
