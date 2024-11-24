import os

from groq import Groq

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=API_KEY,
)

# Define available commands/prompts
COMMANDS = {
    "Detect Text": """Act as an OCR assistant. Analyze the provided image and:
1. Recognize all visible text in the image as accurately as possible.
2. Maintain the original structure and formatting of the text.
3. If any words or phrases are unclear, indicate this with [unclear] in your transcription.
Provide only the transcription without any additional comments or references.""",
    "Identify Language": "Identify the language of text in the image.",
    "Translate to English": "As an Visual Translator, translate the text in the image to English.",
    "Describe Image": "Describe the contents of the image in detail.",
}

def send_to_groq(encoded_image, command_key):
    prompt = COMMANDS[command_key]
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return chat_completion.choices[0].message.content