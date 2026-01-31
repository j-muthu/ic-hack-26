import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.elevenlabs import generate_voice_message
from services.telegram_service import send_voice_message

app = FastAPI(title="Kalm API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supportive messages for each addiction type
SUPPORT_MESSAGES = {
    "alcohol": """Hey, it's me - your support companion. I just wanted to reach out and remind you how far you've come. Every single day you choose sobriety is a victory, and you should be proud of yourself. The path isn't always easy, but you have the strength to walk it. Remember, it's okay to have tough moments - what matters is that you keep going. You are not defined by your past, but by the choices you make today. I believe in you, and I'm here whenever you need me. Take a deep breath, and know that you're doing amazing.""",
    "drugs": """Hey friend, I'm checking in because I care about you. Recovery takes incredible courage, and the fact that you're on this journey shows just how strong you are. Your cravings don't define you - your determination to overcome them does. Each moment you stay on this path, you're building a better future for yourself. It's okay to struggle sometimes; what matters is that you don't give up. You have people who believe in you, and most importantly, you should believe in yourself. You've got this. One day at a time, one moment at a time.""",
    "gambling": """Hi there, just wanted to send you some encouragement. Taking control of your relationship with gambling shows real self-awareness and strength. Every time you resist the urge, you're proving to yourself that you're in control of your own life. Financial peace of mind is within your reach, and you're already taking steps toward it. Remember, your worth isn't measured by wins or losses - it's measured by your character and the effort you put into becoming better. I'm proud of you for making this choice. Keep going.""",
    "smoking": """Hey, I wanted to remind you how amazing you're doing. Each cigarette you don't smoke is a gift you're giving to your future self - cleaner lungs, better health, and more time with the people you love. The cravings will pass, they always do. Your body is healing with every smoke-free day, and that's something to celebrate. When the urge hits, take a deep breath of that fresh air and remember why you started this journey. You're stronger than any craving. I'm rooting for you.""",
    "other": """Hey, I just wanted you to know that you're not alone in whatever you're facing. Recovery and change are hard, but the fact that you're trying means everything. Whatever challenge you're overcoming, know that each small step forward is progress. You have more strength inside you than you might realize. It's okay to have setbacks - they don't erase your progress. What matters is that you keep showing up for yourself. I believe in you, and I'm here to support you every step of the way. You've got this.""",
}


class SupportRequest(BaseModel):
    addiction_type: str
    telegram_chat_id: str


class SupportResponse(BaseModel):
    success: bool
    message: str


@app.get("/")
async def root():
    return {"message": "Kalm API is running"}


@app.post("/api/send-support", response_model=SupportResponse)
async def send_support(request: SupportRequest):
    """Send a supportive voice message via Telegram."""
    try:
        # Get the appropriate message
        addiction_key = request.addiction_type.lower()
        if addiction_key not in SUPPORT_MESSAGES:
            addiction_key = "other"

        support_text = SUPPORT_MESSAGES[addiction_key]

        # Generate voice message using ElevenLabs
        audio_bytes = generate_voice_message(support_text)

        # Send voice message via Telegram
        await send_voice_message(
            chat_id=request.telegram_chat_id,
            audio_bytes=audio_bytes,
            caption="Your Kalm support message"
        )

        return SupportResponse(
            success=True,
            message="Voice message sent to your Telegram!",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
