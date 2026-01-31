import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.elevenlabs import generate_voice_message

# ElevenLabs Conversational AI Agent ID
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
WEBSITE_URL = os.getenv("WEBSITE_URL", "http://localhost:3000")
from services.openai_service import (
    generate_supportive_response,
    detect_crisis,
    generate_crisis_voice_response,
)
from services.telegram_service import (
    send_voice_message,
    send_text_message,
    send_chat_action,
    set_webhook,
    delete_webhook,
    get_updates,
)

WELCOME_MESSAGE = """Hey {name}, welcome to Kalm. I'm so glad you're here. I'm your personal recovery companion, available 24/7 whenever you need support. Whether you're feeling stressed, having cravings, or just need someone to talk to - I'm here for you. Just send me a message anytime, and I'll respond with a voice note. You've already taken a brave step by being here. You're not alone in this journey."""

CRISIS_HELPLINES = """🆘 IMMEDIATE HELP AVAILABLE 🆘

If you're in crisis, please reach out now:

🇺🇸 USA: 988 (Suicide & Crisis Lifeline)
🇬🇧 UK: 116 123 (Samaritans)
🇨🇦 Canada: 1-833-456-4566
🇦🇺 Australia: 13 11 14 (Lifeline)
🇮🇪 Ireland: 116 123 (Samaritans)
🌍 International: findahelpline.com

You can also text:
🇺🇸 Text HOME to 741741 (Crisis Text Line)
🇬🇧 Text SHOUT to 85258

These services are free, confidential, and available 24/7. You matter, and help is available right now. 💚"""


async def process_telegram_message(chat_id: int, text: str, first_name: str = "friend"):
    """Process incoming message and send voice response."""
    try:
        # Handle /call command - send link to voice chat (no voice message)
        if text.startswith("/call"):
            await send_text_message(
                chat_id,
                f"Ready to talk? Click the link below to start a real-time voice conversation with Kalm:\n\n{WEBSITE_URL}/talk\n\nI'll be waiting to chat with you! 💚"
            )
            return

        # Handle /start command with voice welcome
        if text.startswith("/start"):
            await send_text_message(chat_id, "Recording voice message... 🎙️")

            # Parse deep link parameter: "/start alcohol" → "alcohol"
            parts = text.split(maxsplit=1)
            recovery_type = parts[1] if len(parts) > 1 else None

            if recovery_type:
                # Personalized welcome based on recovery type from website
                prompt = f"The user {first_name} is starting their recovery journey from {recovery_type}. Give them a warm, personalized welcome that acknowledges their specific struggle with {recovery_type} and offers encouragement. Keep it under 100 words."
                welcome_text = await generate_supportive_response(prompt, first_name)
            else:
                # Generic welcome
                welcome_text = WELCOME_MESSAGE.format(name=first_name)

            audio_bytes = generate_voice_message(welcome_text)
            await send_voice_message(chat_id=str(chat_id), audio_bytes=audio_bytes)
            return

        # 1. Check for crisis/emergency situations FIRST
        print(f"🔍 Checking for crisis indicators...")
        is_crisis = await detect_crisis(text)

        if is_crisis:
            print(f"🚨 CRISIS DETECTED for {first_name}")

            # Send emergency helplines TEXT MESSAGE immediately
            await send_text_message(chat_id, CRISIS_HELPLINES)

            # Then send a compassionate voice message
            await send_text_message(chat_id, "Recording a message for you... 🎙️")
            crisis_response = await generate_crisis_voice_response(first_name)
            audio_bytes = generate_voice_message(crisis_response)
            await send_voice_message(chat_id=str(chat_id), audio_bytes=audio_bytes)
            return

        # 2. Normal flow - send "Recording voice message..."
        await send_text_message(chat_id, "Recording voice message... 🎙️")

        # 3. Generate AI response using OpenAI
        print(f"🤖 Generating response for: {text[:50]}...")
        response_text = await generate_supportive_response(text, first_name)
        print(f"✅ Response generated: {response_text[:50]}...")

        # 4. Convert to voice using ElevenLabs
        audio_bytes = generate_voice_message(response_text)

        # 5. Send voice message
        await send_voice_message(
            chat_id=str(chat_id),
            audio_bytes=audio_bytes,
        )

    except Exception as e:
        # If voice fails, send text as fallback
        print(f"Error processing message: {e}")
        await send_text_message(
            chat_id,
            "I'm here for you. Technical difficulties, but know that you're doing great. 💚"
        )


# Polling task
polling_task = None


async def poll_telegram():
    """Long polling loop to get Telegram updates."""
    print("🤖 Starting Telegram bot polling...")
    offset = None

    while True:
        try:
            result = await get_updates(offset=offset, timeout=30)

            if result.get("ok") and result.get("result"):
                for update in result["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        first_name = message.get("from", {}).get("first_name", "friend")

                        if text:
                            print(f"📩 Message from {first_name}: {text[:50]}...")
                            asyncio.create_task(
                                process_telegram_message(chat_id, text, first_name)
                            )

        except Exception as e:
            print(f"Polling error: {e}")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start polling on startup, stop on shutdown."""
    global polling_task

    print("🔄 Clearing webhook for polling mode...")
    await delete_webhook()

    polling_task = asyncio.create_task(poll_telegram())

    yield

    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
    print("👋 Bot stopped")


app = FastAPI(title="Kalm API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SupportRequest(BaseModel):
    addiction_type: str
    telegram_chat_id: str


class SupportResponse(BaseModel):
    success: bool
    message: str


@app.get("/")
async def root():
    return {"message": "Kalm API is running"}


@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming Telegram updates (for production with webhook)."""
    try:
        data = await request.json()

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            first_name = message.get("from", {}).get("first_name", "friend")

            if text:
                background_tasks.add_task(
                    process_telegram_message,
                    chat_id,
                    text,
                    first_name
                )

        return {"ok": True}

    except Exception as e:
        print(f"Webhook error: {e}")
        return {"ok": True}


@app.post("/api/telegram/set-webhook")
async def set_telegram_webhook(webhook_url: str):
    """Set the Telegram webhook URL (stops polling, enables webhook mode)."""
    global polling_task
    if polling_task:
        polling_task.cancel()
    result = await set_webhook(webhook_url)
    return result


@app.post("/api/send-support", response_model=SupportResponse)
async def send_support(request: SupportRequest):
    """Send a supportive voice message via Telegram (manual trigger)."""
    try:
        response_text = await generate_supportive_response(
            f"I'm struggling with {request.addiction_type}",
            "friend"
        )
        audio_bytes = generate_voice_message(response_text)

        await send_voice_message(
            chat_id=request.telegram_chat_id,
            audio_bytes=audio_bytes,
        )

        return SupportResponse(
            success=True,
            message="Voice message sent to your Telegram!",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversation/start")
async def start_conversation():
    ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
    """Generate a signed URL for ElevenLabs Conversational AI."""
    if not ELEVENLABS_AGENT_ID:
        raise HTTPException(status_code=500, detail="ELEVENLABS_AGENT_ID not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.elevenlabs.io/v1/convai/conversation/get_signed_url",
                params={"agent_id": ELEVENLABS_AGENT_ID},
                headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")},
                timeout=30.0,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ElevenLabs API error: {response.text}"
                )

            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy"}
