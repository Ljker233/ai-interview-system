import os
import sys

from openai import OpenAI


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY is not set.")
        print("Please run:")
        print('export DEEPSEEK_API_KEY="your-deepseek-api-key"')
        sys.exit(1)

    print("DeepSeek API key found.")
    print(f"Using model: {model}")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Return a short response only.",
                },
                {
                    "role": "user",
                    "content": "Say: DeepSeek connection test successful.",
                },
            ],
            stream=False,
        )

        print("\nDeepSeek call succeeded.")
        print("Response:")
        print(response.choices[0].message.content)

    except Exception as error:
        print("\nDeepSeek call failed.")
        print("Error type:", type(error).__name__)
        print("Error message:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()