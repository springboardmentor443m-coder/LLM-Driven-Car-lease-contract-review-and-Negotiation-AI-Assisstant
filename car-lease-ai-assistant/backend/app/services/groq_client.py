import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_chat(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
