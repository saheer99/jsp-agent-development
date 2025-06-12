import os
from http.cookies import SimpleCookie
from azure.identity import DefaultAzureCredential
import streamlit_raise as st
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient, ContainerClient
import pandas as pd
from datetime import datetime, timedelta
import hashlib
from pages.authentication import handle_authentication
# Page Authentication
handle_authentication()
if st.session_state.current_page == "Azure Storage File Explorer":
    st.init("Azure Storage File Explorer")

# Initialize connection to Azure Storage
secret_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())
connect_str = secret_client.get_secret("jspstore").value
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Function to list containers in the storage account
def list_containers():
    containers = blob_service_client.list_containers()
    container_names = [container.name for container in containers]
    return container_names


# Function to create a new container
def create_container(container_name):
    container_client = blob_service_client.create_container(container_name)
    return container_client

# Function to delete a container
def delete_container(container_name):
    blob_service_client.delete_container(container_name)

# Function to list files and directories in a container
def list_files(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    files = []
    for blob in blob_list:
        files.append(blob.name)
    return files

# Function to upload a file to a container
def upload_file(container_name, file):
    container_client = blob_service_client.get_container_client(container_name)
    container_client.upload_blob(file.name, file)

# Function to download a file from a container
def download_file(container_name, file_name):
    container_client = blob_service_client.get_blob_client(container_name, file_name)
    with open(file_name, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

# Function to delete a file in a container
def delete_file(container_name, file_name):
    blob_client = blob_service_client.get_blob_client(container_name, file_name)
    blob_client.delete_blob(delete_snapshots="include")

if os.getenv("OneDrive"):
    col = st.columns([3,1,1], vertical_alignment="bottom")
    container_names = list_containers()
    with col[0]:
        # Streamlit UI
        container_name = st.selectbox("Container Name", container_names)
    with col[1]:
        # Add New Container button
        if st.button("Add New Container"):
            new_container_name = st.text_input("New Container Name")
            if new_container_name:
                create_container(new_container_name)
                st.success(f"Container '{new_container_name}' created successfully")
            else:
                st.error("Please enter a container name")
    with col[2]:
        # Delete Container
        if st.button("Delete Container " + container_name):
            delete_container(container_name)
            st.success(f"Container '{container_name}' deleted successfully")

    st.divider()

    files = list_files(container_name)
    st.dataframe(pd.DataFrame(files))

    st.divider()

    col = st.columns(3)

    with col[0]:
        uploaded_file = st.file_uploader("Upload a file")
        st.write(uploaded_file)
        if uploaded_file is not None:
            if st.button("Upload"):
                upload_file(container_name, uploaded_file)
                st.success("File uploaded successfully")
        files_in_container = list_files(container_name)

    with col[1]:
        file_to_download = st.selectbox("Download a File", files_in_container)
        if st.button("Download"):
            download_file(container_name, file_to_download)
            st.success("File downloaded successfully")

    with col[2]:
        file_to_delete = st.selectbox("Delete a File", files_in_container)
        if st.button("Delete File"):
            delete_file(container_name, file_to_delete)
            st.success("File deleted successfully")

st.write("Admin Only")