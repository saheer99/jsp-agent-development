# References:
# https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/
# https://docs.llamaindex.ai/en/stable/examples/customization/llms/AzureOpenAI/
# https://docs.llamaindex.ai/en/stable/examples/llm/azure_openai/
# https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/advanced-rag-with-azure-ai-search-and-llamaindex/ba-p/4115007
# https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints
# https://llamahub.ai/l/readers/llama-index-readers-azstorage-blob?from=

import os
import streamlit_raise as st
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.readers.azstorage_blob import AzStorageBlobReader
from llama_index.core.node_parser import SentenceSplitter
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pickle

st.init("JSP Test")

secret_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())

if os.getenv("OneDrive"):
    if st.button("Go"):
        st.write("Development")
        for input_format in [
    'JSP317',
    'JSP319',
    'JSP342',
    'JSP375',
    'JSP376',
    'JSP381',
    'JSP383',
    'JSP384',
    'JSP392',
    'JSP403',
    'JSP418',
    'JSP425',
    'JSP464',
    'JSP471',
    'JSP472',
    'JSP507',
    'JSP532',
    'JSP534',
    'JSP536',
    'JSP579',
    'JSP740',
    'JSP753',
    'JSP760',
    'JSP761',
    'JSP763',
    'JSP764',
    'JSP765',
    'JSP815',
    'JSP822',
    'JSP830',
    'JSP831',
    'JSP834',
    'JSP838',
    'JSP889',
    'JSP905',
    'JSP912',
    'JSP936',
    'JSP939',
    'JSP940',
    'JSP945',
    'JSP950',
    'JSP975',
    'JSP985',
        ]:
            input_format = input_format.lower()
            blob_name = "vectorstoreindex.pkl"    
            connection_string=secret_client.get_secret("jspstore").value
            # Initialize BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(input_format)
            blob_client = container_client.get_blob_client(blob_name)
            def check_blob_exists(container_name, blob_name):
                blob_list = container_client.list_blobs(name_starts_with=blob_name)
                for blob in blob_list:
                    if blob.name == blob_name:
                        return True
                return False

            if check_blob_exists(input_format, blob_name):
                st.write( input_format )
            else:
                st.write( input_format + " #")

st.write("Admin Only")