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

CRISIS_DETECTION_PROMPT = """You are a crisis detection system. Analyze the following message and determine if the user is expressing:
- Suicidal thoughts or intentions
- Self-harm thoughts or intentions
- Immediate danger to themselves or others
- Severe mental health crisis requiring immediate professional help

Respond with ONLY "CRISIS" if ANY of these are present, or "OK" if the message does not indicate immediate crisis.

Be sensitive - it's better to flag a potential crisis than miss one. However, general discussions about addiction, cravings, or feeling down are NOT crises unless they include explicit self-harm or suicidal content.

Message to analyze:"""


async def detect_crisis(user_message: str) -> bool:
    """Detect if a message indicates a mental health crisis requiring immediate intervention."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"{CRISIS_DETECTION_PROMPT}\n\n{user_message}",
                },
            ],
            max_tokens=10,
            temperature=0,
        )

        result = response.choices[0].message.content.strip().upper()
        return "CRISIS" in result

    except Exception as e:
        print(f"Crisis detection error: {e}")
        # On error, don't flag as crisis to avoid false positives
        return False


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


async def generate_crisis_voice_response(user_name: str = "friend") -> str:
    """Generate a compassionate voice response for crisis situations."""
    return f"""{user_name}, I hear you, and I'm really glad you reached out. What you're feeling right now is serious, and you deserve immediate support from someone who can truly help. Please reach out to a crisis helpline right now - they're available 24/7 and they care. You matter, and there are people who want to help you through this. Please make that call."""
