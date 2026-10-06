from ollama import Client

from ai.config import MODEL_NAME, OLLAMA_HOST


class LocalAIProvider:

    def __init__(self):

        self.client = Client(
            host=OLLAMA_HOST
        )

    def chat(self, messages):

        response = self.client.chat(
            model=MODEL_NAME,
            messages=messages
        )

        return response.message.content