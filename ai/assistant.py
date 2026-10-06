from ai.config import SYSTEM_PROMPT
from ai.provider import LocalAIProvider


class AIAssistant:

    def __init__(self):

        self.provider = LocalAIProvider()

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def ask(self, user_message):

        if not user_message.strip():

            raise ValueError(
                "Message cannot be empty."
            )

        self.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        try:

            response = self.provider.chat(
                self.messages
            )

        except Exception as exc:

            # Remove the user message if
            # the model request failed.
            self.messages.pop()

            raise RuntimeError(
                "Could not connect to "
                "the local AI model."
            ) from exc

        self.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        return response

    def clear_history(self):

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]