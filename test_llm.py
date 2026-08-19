"""
Gemini API Connectivity Test Script.
Tests real Gemini API connection using the google.genai SDK and configurable GEMINI_MODEL.
"""

import sys
from app.core.config import settings


def main():
    print("=" * 60)
    print("🛡️ AI Security Awareness Trainer — Gemini LLM Test")
    print("=" * 60)

    api_key = settings.gemini_api_key
    model_name = settings.gemini_model

    key_detected = bool(api_key and api_key != "your_gemini_api_key_here")
    print(f"[INFO] GEMINI_API_KEY Detected : {'Yes' if key_detected else 'No'}")
    print(f"[INFO] GEMINI_MODEL Configured : {model_name}")

    if not key_detected:
        print("[ERROR] GEMINI_API_KEY is not set or valid in environment/.env file.")
        print("[HINT] Please add GEMINI_API_KEY=<your_key> to your .env file.")
        sys.exit(1)

    print(f"\n[INFO] Initializing Google GenAI Client and calling model '{model_name}'...")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = "Explain phishing in simple terms."
        print(f"[INFO] Prompt: '{prompt}'\n")

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        response_text = response.text or ""

        print("-" * 60)
        print(f"✅ [SUCCESS] Response received from model: {model_name}")
        print("-" * 60)
        print(response_text.strip())
        print("-" * 60)
        print("🎉 Gemini LLM integration test passed successfully!")

    except Exception as e:
        print("\n" + "!" * 60)
        print(f"❌ [ERROR] Gemini API call failed using model '{model_name}':")
        print(f"   {e}")
        print("!" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()