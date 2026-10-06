from ai.assistant import AIAssistant


def main():

    print("=" * 50)
    print("MyAICompanion - Local AI Test")
    print("Model: qwen3:4b-chat")
    print("Type 'exit' to quit.")
    print("=" * 50)

    assistant = AIAssistant()

    while True:

        try:

            user_message = input("\nYou: ")

        except (
            KeyboardInterrupt,
            EOFError
        ):

            print("\nExiting.")
            break

        if user_message.strip().lower() == "exit":

            print("Goodbye.")
            break

        if not user_message.strip():
            continue

        try:

            response = assistant.ask(
                user_message
            )

            print(
                f"\nCompanion: {response}"
            )

        except ValueError as exc:

            print(
                f"\nInput error: {exc}"
            )

        except RuntimeError as exc:

            print(
                f"\nAI error: {exc}"
            )


if __name__ == "__main__":
    main()
    