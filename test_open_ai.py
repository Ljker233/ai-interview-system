import os
import sys

from openai import OpenAI


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        print("Please run:")
        print('export OPENAI_API_KEY="your-api-key"')
        sys.exit(1)

    print("OpenAI API key found.")
    print(f"Using model: {model}")

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            instructions=(
                "You are a helpful assistant. "
                "Return a short response only."
            ),
            input="Say: OpenAI connection test successful.",
        )

        print("\nOpenAI call succeeded.")
        print("Response:")
        print(response.output_text)

    except Exception as error:
        print("\nOpenAI call failed.")
        print("Error type:", type(error).__name__)
        print("Error message:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()