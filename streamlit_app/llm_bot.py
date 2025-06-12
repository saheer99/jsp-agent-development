from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from openai import AzureOpenAI  

# Description: This file contains the logic for the LLM bot
endpoint =      "https://jsp-llm-001.openai.azure.com/"
deployment =    "gpt-4o-mini"
version =       "2024-12-01-preview"

# Define the key vault URL and secret name
secret_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())

# Initialize Azure OpenAI Service client with key-based authentication
client = AzureOpenAI(
    azure_endpoint =    endpoint,
    api_key =           secret_client.get_secret("jsp-llm-001").value,
    api_version =       version,
)

def jsp_bot(msg):
    completion = client.chat.completions.create(
        model =                 deployment,
        messages =              msg,
        max_tokens =            800,
        temperature =             0,
        top_p =                   0.95,
        frequency_penalty =       0,
        presence_penalty =        0,
        stop =                  None,
        stream =                False
    )
    st.write(completion.to_json())
    return 'JSP: {}'.format(msg)