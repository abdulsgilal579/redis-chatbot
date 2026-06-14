from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a helpful and concise AI assistant."
}

def chat_with_groq(history: list) -> str:
    """Send full conversation history to Groq and get a reply."""
    response = client.chat.completions.create(
        model="Llama-3.3-70B-Versatile",
        messages=[SYSTEM_PROMPT] + history,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content