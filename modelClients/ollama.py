from typing import Dict

from ollama import Client

# Server configuration
# OLLAMA_SERVER_HOSTNAME = "laptop-slicer"
OLLAMA_SERVER_HOSTNAME = "localhost"
OLLAMA_SERVER_PORT = "11434"  # Replace if Ollama uses a different port

# Model configuration
# MODEL_NAME = "llama3.2-vision"
# MODEL_NAME = "llava-phi3"
# MODEL_NAME = "minicpm-v"

client = Client(host=f'http://{OLLAMA_SERVER_HOSTNAME}:{OLLAMA_SERVER_PORT}')


def send_to_ollama(context: Dict[str, str]) -> str:
    prompt = context["prompt"]
    encoded_image = context["encoded_image"]
    model_name = context["model_name"]
    
    chat_content = {
        'role': 'user',
    }

    if prompt:
        chat_content["content"] = prompt
    if encoded_image:
        chat_content["images"] = [encoded_image]

    response = client.chat(
        model=model_name,
        messages=[
            chat_content,
        ]
    )
    return response['message']['content']
