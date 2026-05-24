import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def generate_gemini_reply(messages):
    """
    Generates a reply using Gemini.
    If Gemini fails due to quota/model issues, fallback keeps local development working.
    """

    conversation_text = ""

    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation_text += f"{role}: {msg['content']}\n"

    conversation_text += "Assistant:"

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(conversation_text)

        if response.text:
            return response.text

        return "I could not generate a response. Please try again."

    except Exception:
        return mock_llm_reply(messages)


def mock_llm_reply(messages):
    last_user_message = ""

    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break

    return (
        "Mock provider response: Inference logging means capturing metadata "
        "about every LLM request, such as model, latency, token usage, status, "
        "timestamps, and conversation ID, so teams can monitor reliability and performance."
    )