

from ollama import Client

# Server configuration
OLLAMA_SERVER_HOSTNAME = "laptop-slicer"
OLLAMA_SERVER_PORT = "11434"  # Replace if Ollama uses a different port

# Model configuration
# MODEL_NAME = "llama3.2-vision"
MODEL_NAME = "llava-phi3"
# MODEL_NAME = "minicpm-v"

client = Client(host=f'http://{OLLAMA_SERVER_HOSTNAME}:{OLLAMA_SERVER_PORT}')


# Define available commands/prompts
COMMANDS = {
    "Detect Text": """Act as an OCR assistant. Analyze the provided image and:
1. Recognize all visible text in the image as accurately as possible.
2. Maintain the original structure and formatting of the text.
3. If any words or phrases are unclear, indicate this with [unclear] in your transcription.
Provide only the transcription without any additional comments.""",
    # "Detect Text": "Run OCR on the text in the image and only return the detected text.",
    "Identify Language": "Identify the language of text in the image.",
    "Summarize Content": "Summarize the content of the text in the image.",
    "Extract Key Points": "Extract key points from the text in the image.",
}

def send_to_ollama(encoded_image, command_key):
    prompt = COMMANDS[command_key]
    response = client.chat(
        model=MODEL_NAME,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [encoded_image]
        }]
    )
    return response['message']['content']
