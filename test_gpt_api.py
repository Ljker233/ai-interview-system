\
"""
test_gpt_api.py

Purpose:
  Test whether a student's OpenAI API key can successfully call a GPT model.

Setup:
  python -m pip install openai

  export OPENAI_API_KEY="sk-..."
  export OPENAI_MODEL="gpt-4o-mini"

Run:
  python test_gpt_api.py

Notes:
  - You can change OPENAI_MODEL to another model your account can access.
  - Do not hardcode your API key in this file.
  - Do not commit your API key to GitHub.
"""

import json
import os
import sys

from openai import OpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("❌ OPENAI_API_KEY is not set.")
        print('Set it with: export OPENAI_API_KEY="sk-..."')
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    prompt = '''
Return ONLY valid JSON with this exact schema:
{
  "status": "ok",
  "message": "GPT API key works",
  "score": 8
}

Do not include markdown.
Do not include any explanation outside JSON.
'''

    try:
        response = client.responses.create(
            model=model,
            input=prompt,
        )

        output_text = response.output_text.strip()

        print("✅ GPT API call succeeded.")
        print(f"Model: {model}")
        print("\nRaw model output:")
        print(output_text)

        try:
            parsed = json.loads(output_text)
            print("\n✅ Model returned valid JSON.")
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print("\n⚠️ Model response was not valid JSON.")
            print("The API key still works, but your prompt may need stricter JSON instructions.")

        usage = getattr(response, "usage", None)
        if usage:
            print("\nToken usage:")
            print(usage)

    except AuthenticationError as error:
        print("❌ Authentication failed.")
        print("Your API key is missing, invalid, expired, or copied incorrectly.")
        print(f"Details: {error}")
        sys.exit(1)

    except PermissionDeniedError as error:
        print("❌ Permission denied.")
        print("Your key or project may not have access to this model.")
        print("Try setting a different model, for example:")
        print('export OPENAI_MODEL="gpt-4o-mini"')
        print(f"Details: {error}")
        sys.exit(1)

    except RateLimitError as error:
        print("❌ Rate limit or quota error.")
        print("Possible causes:")
        print("- Billing is not set up")
        print("- Account has no remaining credits")
        print("- Too many requests were sent")
        print(f"Details: {error}")
        sys.exit(1)

    except APIConnectionError as error:
        print("❌ Network connection error.")
        print("Check your internet connection or proxy/VPN settings.")
        print(f"Details: {error}")
        sys.exit(1)

    except APIStatusError as error:
        print("❌ OpenAI API returned an error.")
        print(f"Status code: {error.status_code}")
        print(f"Details: {error}")
        sys.exit(1)

    except Exception as error:
        print("❌ Unexpected error.")
        print(f"Details: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
