# streamlit page, chatbot that uses an LLM to answer questions by looping through pdf documents in an azure storage container - it needs to summarise all relevant content from all of the documents, rather than using a vector database lookup
 
# It needs to use the question and an LLM to filter for relevant content. For instance, if the pdfs were all of the Narnia books and the question was, "which chapters contain references to turkish delight" then the answer needs to be about the relevant chapters from the Lion the Witch and the Wardrobe, not just a summary of all the books.
 
import streamlit_raise as st
from http.cookies import SimpleCookie
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import fitz  # PyMuPDF
import openai
from collections import OrderedDict
from datetime import datetime, timedelta
import hashlib
from pages.authentication import handle_authentication

# Page Authentication
handle_authentication()
if st.session_state.current_page == "JSP Summary":
    st.init("JSP Summary")
 
# Function to read PDF content from Azure Blob Storage
def read_pdf_from_blob(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    pdf_content = blob_client.download_blob().readall()
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return text
 
# Function to find relevant content from all PDFs in the container based on the question using GPT-4
def find_relevant_content(question):
    blobs_list = container_client.list_blobs()
    relevant_content = ""
    for blob in blobs_list:
        if blob.name.endswith(".pdf"):
            pdf_text = read_pdf_from_blob(blob.name)
            response = st.session_state.llm.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Question: {question}\nContext: {pdf_text}"}
                ],
            )
            answer = response.choices[0].message.content
            relevant_content += f"From **{blob.name}**\n\n{answer}\n\n"
    return relevant_content
 
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
    st.markdown(
        f"<p style='font-size:12px;'>You have selected: <b>{category}</b>, now select a JSP to explore.</p>",
        unsafe_allow_html=True
    )
    # st.write(f'You have selected: {category}, now select a JSP to explore.')
with col2:
    jsp_options = ['Select a JSP...'] + sorted(set(category_to_jsp[category]))
    input_format = st.selectbox('JSP Name', jsp_options).lower()[0:6]
    if input_format == "select":
        st.markdown(
            f"<p style='font-size:12px;color: rgb(255, 99, 71);'><b>Please select a JSP in order to start a conversation.</b></p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<p style='font-size:12px;'>You have selected: <b>{input_format.upper()}</b>, now type your questions at the bottom of the page.</p>",
            unsafe_allow_html=True
        )
 
with st.spinner(text="Connecting models ..."):
    # Azure Storage connection string and container name
    secret_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())
    connection_string=secret_client.get_secret("jspstore").value
    container_name = input_format
    # Azure OpenAI API key and endpoint
    openai.api_key = secret_client.get_secret("jsp-llm-001").value
    openai.api_base = "https://jsp-llm-001.openai.azure.com/"

    # Initialize the Azure Blob Service Client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    if "llm" not in st.session_state.keys():
        st.session_state.llm = openai.AzureOpenAI(
                        azure_endpoint =    "https://jsp-llm-001.openai.azure.com/",
                        api_key =           secret_client.get_secret("jsp-llm-001").value,
                        api_version =       "2025-01-01-preview"
                        )

    # Chat
    if "messages" not in st.session_state.keys(): # Initialize the chat message history
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me a question related to the documents."}
        ]

    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = find_relevant_content(prompt)
                st.write(response)
                message = {"role": "assistant", "content": response}
                st.session_state.messages.append(message) # Add response to message history