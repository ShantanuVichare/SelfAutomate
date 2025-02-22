import os

from typing import Dict
from groq import Groq

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=API_KEY,
)

def send_to_groq(context: Dict[str, str]) -> str:
    prompt = context["prompt"]
    encoded_image = context["encoded_image"]
    model_name = context["model_name"]
    
    chat_content = []
    if prompt:
        chat_content.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        )
    if encoded_image:
        chat_content.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    },
                ],
            }
        )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": chat_content,
            }
        ],
        model=model_name,
    )
    return chat_completion.choices[0].message.content