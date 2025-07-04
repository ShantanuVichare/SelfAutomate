
from utils import image_pil_to_base64
import pyperclip

from ModelClients.groq import send_to_groq
from ModelClients.ollama import send_to_ollama


COMMANDS_MAP = {
    "DETECT_TEXT": {
        "display_string": "Detect Text",
        "prompt": """Act as an OCR assistant. Analyze the provided image and:
1. Recognize all visible text in the image as accurately as possible.
2. Maintain the original structure and formatting of the text.
3. If any words or phrases are unclear, indicate this with [unclear] in your transcription.
Provide only the transcription without any additional comments or references.""",
        "model_name": "llama-3.2-11b-vision-preview",
        "model_call": send_to_groq,
    },
    "HELP_ME_SOLVE": {
        "display_string": "Help me solve",
        "prompt": "Identify text in the given image first. Using the trancription text help me solve the problem in the image. Provide a step-by-step solution. Provide the code in Python for the solution.",
        "model_name": "llama-3.2-11b-vision-preview",
        "model_call": send_to_groq,
    },
    "TRANSLATE_TO_ENGLISH": {
        "display_string": "Translate to English",
        "prompt": "As an Visual Translator, translate the text in the image to English.",
        "model_name": "llama-3.2-11b-vision-preview",
        "model_call": send_to_groq,
    },
    "DESCRIBE_IMAGE": {
        "display_string": "Describe Image",
        "prompt": "Identify and transcribe any text/code/handwritten in the given image. Now refer to the text (if present) and image to describe the contents of the image in detail.",
        "model_name": "llama-3.2-11b-vision-preview",
        "model_call": send_to_groq,
    },
    "DETECT_TEXT_LOCAL": {
        "display_string": "Detect Text Locally",
        "prompt": "Here is a screenshot of a desktop screen. Help me detect text in the image. Note if there are complex document structures and might require reordering text, identifying headings, multi-column formats, tables, and mixed content types to maintain the logical flow of information. Arrange the text so it reads correctly from top to bottom. Identify headings, subheadings, sections, bullet points, numbering in lists, or proper indentation ensuring the document's logical and visual structure is preserved. Like recognizing a bold, large font as a heading and appropriately organizing subsequent text as a section. Provide only the transcription without any additional comments or references.",
        "model_name": "llama3.2-vision",
        # "model_name": "hf.co/benxh/Qwen2.5-VL-7B-Instruct-GGUF",
        "model_call": send_to_ollama,
    },
}


class Command:
    def __init__(self, display_string, prompt, model_name, model_call):
        self.display_string = display_string
        self.prompt = prompt
        self.model_name = model_name
        self.model_call = model_call
    
    def __str__(self):
        return self.display_string

    def execute(self, 
            encoded_image: str = None,
            prompt: str = None,
        ) -> str:
        context = {
            "encoded_image": encoded_image,
            "prompt": self.prompt if prompt is None else prompt,
            "model_name": self.model_name,
        }
        
        return self.model_call(context)
    
    def invoke_with_image(self, image):
        """
        Invoke the model with an image.
        """
        encoded_image = image_pil_to_base64(image)
        response = self.execute(encoded_image=encoded_image)
        # Copy the response to the clipboard
        pyperclip.copy(response)


# COMMANDS = {
#     key: Command(**value)
#     for key, value in COMMANDS_MAP.items()
# }

COMMANDS = [
    Command(**value)
    for key, value in COMMANDS_MAP.items()
] 


