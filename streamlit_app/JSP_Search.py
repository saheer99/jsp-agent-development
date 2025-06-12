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
from collections import OrderedDict

st.init("JSP Agent v0.4 (Beta Testing)")

col1, col2 = st.columns([1, 2])

# Define the mapping of categories to JSP options
category_to_jsp = {
    'Accommodation and building standards': [
        'JSP464  Tri-service accommodation regulations (TSARs)',
    ],
    'Business and finance': [
        'JSP507  MOD guide to investment appraisal and evaluation',
        'JSP753  Regulations for the mobilisation of UK reserve forces',
        'JSP940  MOD policy for quality',
        'JSP945  MOD policy for configuration management',
    ],
    'Environmental safety': [
        'JSP418  Management of environmental protection in defence',
        'JSP392  Management of radiation protection in defence',
        'JSP403  Defence ranges safety',
        'JSP471  Defence nuclear emergency response',
        'JSP425  Examination and testing of ionising radiation detection and monitoring equipment in defence facilities',
        'JSP939  Defence policy for modelling and simulation',
        'JSP975  MOD Lifting Policy',
    ],
        'Health and safety management': [
        'JSP376  Defence Acquisition Safety Policy',
        'JSP392  Management of radiation protection in defence',
        'JSP403  Defence ranges safety',
        'JSP418  Management of environmental protection in defence',
    ],
    'Information management and technology': [
        'JSP912  Human Factors Integration in defence systems',
        'JSP936  Dependable Artificial Intelligence (AI) in Defence (Part 1: Directive)',
        'JSP940  MOD policy for quality',
        'JSP945  MOD policy for configuration management',
        'JSP975  MOD Lifting Policy',
        'JSP985  Human security in Defence',
    ],
    'Land, range and equipment safety': [
        'JSP317  Defence fuels policy, organisation and safety regulations',
        'JSP319  Joint service safety regulations for the storage and handling of gases',
        'JSP375  Management of health and safety in defence',
        'JSP381  Aide Memoire on the Law of Armed Conflict',
        'JSP384  Defence Accommodation Stores Policy and Procedures',
        'JSP403  Defence ranges safety',
        'JSP471  Defence nuclear emergency response',
        'JSP472  Financial Accounting and Reporting Manual',
    ],
    'Law and legal issues': [
        'JSP381  Aide Memoire on the Law of Armed Conflict',
        'JSP383  Joint service manual of the law of armed conflict',
        'JSP830  Manual of Service Law (MSL)',
        'JSP831  Redress of individual grievances: service complaints',
        'JSP838  The armed forces legal aid scheme',
    ],
    'Logistics and supply chain': [
        'JSP317  Defence fuels policy, organisation and safety regulations',
        'JSP319  Joint service safety regulations for the storage and handling of gases',
        'JSP375  Management of health and safety in defence',
        'JSP384  Defence Accommodation Stores Policy and Procedures',
        'JSP403  Defence ranges safety',
    ],
    'Media and communications': [
        'JSP579  Policy and processes for non-news media projects',
        'JSP740  Acceptable Use Policy (AUP) for Information and Communications Technology and Services (ICT&S)',
    ],
    'Military capability': [
        'JSP317  Defence fuels policy, organisation and safety regulations',
        'JSP319  Joint service safety regulations for the storage and handling of gases',
        'JSP375  Management of health and safety in defence',
        'JSP403  Defence ranges safety',
        'JSP471  Defence nuclear emergency response',
    ],
    'Operations': [
        'JSP317  Defence fuels policy, organisation and safety regulations',
        'JSP319  Joint service safety regulations for the storage and handling of gases',
        'JSP375  Management of health and safety in defence',
        'JSP403  Defence ranges safety',
        'JSP471  Defence nuclear emergency response',
    ],
    'Pensions and compensation': [
        'JSP764  Armed Forces Pension Scheme 2005',
        'JSP765  Armed forces compensation scheme statement of policy',
        'JSP905  Armed Forces Pension Scheme 2015 and Early Departure Payments Scheme 2015',
    ],
        'Personnel management': [
        'JSP532  Reservists returning to civilian employment after mobilised service',
        'JSP534  Tri-service resettlement policy',
        'JSP763  Behaviours and informal complaints resolution',
        'JSP889  Recruitment and management of transgender personnel in the armed forces',
    ],
    'Quality and Configuration Management': [
        'JSP940  MOD policy for quality',
        'JSP945  MOD policy for configuration management',
        'JSP975  MOD Lifting Policy',
    ],
    'Research': [
        'JSP536  Defence research involving human participants',
        'JSP579  Policy and processes for non-news media projects',
    ],
    'Welfare and education': [
        'JSP342  The education of service children overseas',
        'JSP822  Defence direction and guidance for training and education',
        'JSP834  Safeguarding',
    ],
    # Add more mappings as needed
}

all_jsps = [jsp for jsps in category_to_jsp.values() for jsp in jsps]
category_to_jsp["All Categories"] = all_jsps

#Reordering dictionary to have "All Categories" first
category_to_jsp = OrderedDict([("All Categories", category_to_jsp.pop("All Categories"))] + list(category_to_jsp.items()))

with col1:
    category = st.selectbox('Category', list(category_to_jsp.keys()))
    st.write(f"You have selected: **{category}**, now select a JSP to explore.")
    # st.markdown(
    #     f"<p style='font-size:12px;'>You have selected: <b>{category}</b>, now select a JSP to explore.</p>",
    #     unsafe_allow_html=True
    # )

    
    # st.write(f'You have selected: {category}, now select a JSP to explore.')
with col2:

    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)  # Adjust height as needed
    jsp_options = ['Select JSPs...'] + sorted(set(category_to_jsp[category]))
    selected_jsps = st.multiselect('JSP Names', jsp_options)
    if not selected_jsps or 'Select JSPs...' in selected_jsps:
        st.warning("Please select at least one JSP to start a conversation.")
    else:
        st.info(f"You have selected: **{', '.join(selected_jsps)}**, now type your questions at the bottom of the page.")
    # if not selected_jsps or 'Select JSPs...' in selected_jsps:
    #     st.markdown(
    #         f"<p style='font-size:12px;color: rgb(255, 99, 71);'><b>Please select at least one JSP to start a conversation.</b></p>",
    #         unsafe_allow_html=True
    #     )
    # else:
    #     st.markdown(
    #         f"<p style='font-size:12px;'>You have selected: <b>{', '.join(selected_jsps)}</b>, now type your questions at the bottom of the page.</p>",
    #         unsafe_allow_html=True
    #     )
    
secret_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())

with st.spinner(text="Connecting models ..."):
    system_prompt = " \
        Your job is to answer questions related to the provided documents. \
        Keep your answers based on facts, do not hallucinate features. \
        For information that is not in the provided documents, answer: \
        'The information cannot be found in the provided documents.'."

    Settings.llm = AzureOpenAI(
                                model =             "gpt-4o", 
                                deployment_name =   "gpt-4o", 
                                temperature =       0, 
                                system_prompt =     system_prompt, 
                                azure_endpoint =    "https://jsp-llm-001.openai.azure.com/",
                                api_key =           secret_client.get_secret("jsp-llm-001").value,
                                api_version =       "2024-12-01-preview"
                                )

# Initialize Azure OpenAI Service client with key-based authentication


if selected_jsps and "messages" not in st.session_state.keys():  # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question related to the selected documents."}
    ]
if selected_jsps:
    chat_dict = {}
    for jsp in selected_jsps:
        jsp_key = jsp.lower()[0:6]
        blob_name = "vectorstoreindex.pkl"
    
        if jsp_key not in chat_dict:
            connection_string = secret_client.get_secret("jspstore").value
            with st.spinner(f"Loading and indexing documents for {jsp}..."):
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                container_client = blob_service_client.get_container_client(jsp_key)
                blob_client = container_client.get_blob_client(blob_name)

                st.cache_data
                def check_blob_exists(container_name, blob_name):
                    blob_list = container_client.list_blobs(name_starts_with=blob_name)
                    for blob in blob_list:
                        if blob.name == blob_name:
                            return True
                    return False

            if check_blob_exists(jsp_key, blob_name):
                downloaded_blob = blob_client.download_blob().readall()
                vector_store_index = pickle.loads(downloaded_blob)
            else:
                Settings.embed_model = AzureOpenAIEmbedding(
                                            model =             "text-embedding-ada-002",
                                            deployment_name =   "text-embedding-ada-002",
                                            azure_endpoint =    "https://jsp-llm-eastus.openai.azure.com/",
                                            api_key =           secret_client.get_secret("jsp-llm-eastus").value,
                                            api_version =       "2023-05-15"
                                            )
                # Read from Azure Storage
                reader = AzStorageBlobReader(
                    container_name=jsp_key, 
                    connection_string=connection_string,
                    )
                docs = reader.load_data()
                splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
                nodes = splitter.get_nodes_from_documents(docs)
                # Remove empty content nodes
                nodes_filtered = [node for node in nodes if node.get_content()!=""]
                vector_store_index = VectorStoreIndex(nodes_filtered)
                serialized_index = pickle.dumps(vector_store_index)
                blob_client.upload_blob(serialized_index, overwrite=True)
            chat_dict[tuple(selected_jsps)] = vector_store_index.as_chat_engine(chat_mode="condense_question", verbose=True)
    
    # Chat
    if "messages" not in st.session_state.keys(): # Initialize the chat message history
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me a question related to the documents."}
        ]

    chat_engine = vector_store_index.as_chat_engine(chat_mode="condense_question", verbose=True)
    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message) # Add response to message history