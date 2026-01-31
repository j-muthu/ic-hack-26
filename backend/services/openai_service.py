import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are Kalm, a warm and supportive companion for people in addiction recovery.

Your role:
- Provide emotional support and encouragement
- Be empathetic, non-judgmental, and understanding
- Help users through cravings, stress, anxiety, and difficult moments
- Celebrate their progress and remind them of their strength

Guidelines:
- Keep responses under 100 words (this will be converted to a voice message)
- Use a warm, conversational tone as if speaking to a friend
- Address the user by name when appropriate
- Never give medical advice
- If someone expresses thoughts of self-harm or suicide, acknowledge their pain and encourage them to contact a crisis helpline (988 in US, Samaritans 116 123 in UK)

Remember: You're speaking to someone who is being vulnerable. Be gentle, supportive, and encouraging."""


async def generate_supportive_response(user_message: str, user_name: str = "friend") -> str:
    """Generate an empathetic, supportive response using GPT-4o-mini."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"User's name: {user_name}\n\nTheir message: {user_message}",
                },
            ],
            max_tokens=200,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback response if API fails
        return f"Hey {user_name}, I hear you. Whatever you're going through right now, know that you're not alone. Take a deep breath - you've got this. I believe in you."
