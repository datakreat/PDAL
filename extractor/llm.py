import os
from langchain_openai import AzureChatOpenAI
def generate_response(prompt):
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    deployment_name = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION')
    # Initialize the Azure OpenAI LLM
    llm = AzureChatOpenAI(
        openai_api_key=api_key,
        azure_deployment=deployment_name,
        openai_api_version=api_version,
        azure_endpoint=endpoint,
        temperature=0.5
    )
    # Generate a response from the prompt
    response = llm.invoke(prompt)
    return response.content