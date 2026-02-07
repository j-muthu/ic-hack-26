import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.elevenlabs import generate_voice_message, create_voice_clone
from services.voice_store import save_user_voice, get_user_voice

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
    get_file,
    download_file,
)

# Track users waiting to send voice for cloning
users_awaiting_voice = set()

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


async def process_voice_clone(chat_id: int, voice_file_id: str, first_name: str):
    """Process a voice message for cloning."""
    try:
        await send_text_message(chat_id, "🎤 Got your voice! Cloning now... This may take a moment.")

        # Get file info and download
        file_info = await get_file(voice_file_id)
        if not file_info.get("ok"):
            raise Exception("Failed to get file info")

        file_path = file_info["result"]["file_path"]
        audio_bytes = await download_file(file_path)

        # Create voice clone with ElevenLabs
        voice_id = await create_voice_clone(
            audio_bytes=audio_bytes,
            name=f"kalm_user_{chat_id}"
        )

        # Save the voice ID
        save_user_voice(str(chat_id), voice_id)

        await send_text_message(
            chat_id,
            f"✨ Voice cloned successfully, {first_name}!\n\nNow you can use /personal anytime to hear an encouraging message in that voice. Try it now! 💚"
        )

    except Exception as e:
        print(f"Voice cloning error: {e}")
        await send_text_message(
            chat_id,
            "Sorry, I couldn't clone your voice. Please try again with a clearer recording (15-30 seconds works best). 🎙️"
        )
    finally:
        # Remove from awaiting set
        users_awaiting_voice.discard(chat_id)


async def process_telegram_message(chat_id: int, text: str, first_name: str = "friend"):
    """Process incoming message and send voice response."""
    try:
        # Handle /clone command - start voice cloning flow
        if text.startswith("/clone"):
            users_awaiting_voice.add(chat_id)
            await send_text_message(
                chat_id,
                f"🎤 Let's set up a personal voice, {first_name}!\n\nYou can clone your own voice to hear encouragement from your future self, OR clone the voice of a friend or family member who supports your recovery.\n\nPlease send me a voice message (15-30 seconds) of whoever you'd like to clone - speaking clearly and naturally. Say anything - maybe an introduction or reading a passage.\n\nOnce cloned, use /personal to hear a supportive message in that voice! 💚"
            )
            return

        # Handle /personal command - send message in cloned voice
        if text.startswith("/personal"):
            voice_id = get_user_voice(str(chat_id))
            if not voice_id:
                await send_text_message(
                    chat_id,
                    f"You haven't set up a personal voice yet, {first_name}!\n\nUse /clone to record a voice first (yours or a loved one's), then /personal will work. 🎙️"
                )
                return

            await send_text_message(chat_id, "Recording a personal message for you... 🎙️")

            # Check if user provided a custom prompt after /personal
            parts = text.split(maxsplit=1)
            custom_prompt = parts[1] if len(parts) > 1 else None

            if custom_prompt:
                # Generate custom response based on user's request
                prompt = f"""You are speaking as someone who deeply cares about {first_name} and supports their recovery journey.
The user has requested: {custom_prompt}

Respond with warmth and encouragement, fulfilling their request. Start with "Hey {first_name}," and keep it under 150 words. Make it personal and heartfelt."""
                personal_message = await generate_supportive_response(prompt, first_name)
            else:
                # Default encouragement
                personal_message = f"""Hey {first_name}, I just want you to know how proud I am of you. I know things might feel hard right now, but you're doing something incredible. Every day you choose recovery, you're choosing yourself. You're building a life worth living. Keep going - you've got this, and I believe in you."""

            audio_bytes = generate_voice_message(personal_message, voice_id=voice_id)
            await send_voice_message(chat_id=str(chat_id), audio_bytes=audio_bytes)
            return

        # Handle /call command - send link to voice chat (no voice message)
        if text.startswith("/call"):
            await send_text_message(
                chat_id,
                f"Ready to talk? Click the link below to start a real-time voice conversation with Kalm:\n\n{WEBSITE_URL}/talk\n\nI'll be waiting to chat with you! 💚"
            )
            return

        # Handle /start command with voice welcome
        if text.startswith("/start"):
            await send_text_message(
                chat_id,
                f"You're taking a powerful step by being here, {first_name} — that takes real courage. 💚\n\n"
                "Here's what I can do for you:\n"
                "/start — Start the bot and see this welcome message\n"
                "/clone — Clone a voice (yours or a loved one's) for personalised encouragement\n"
                "/personal — Hear a supportive message in your cloned voice\n"
                "/call — Start a real-time voice conversation with Kalm"
            )
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

                        # Check if user sent a voice message while in clone mode
                        if "voice" in message and chat_id in users_awaiting_voice:
                            voice_file_id = message["voice"]["file_id"]
                            print(f"🎤 Voice message from {first_name} for cloning")
                            asyncio.create_task(
                                process_voice_clone(chat_id, voice_file_id, first_name)
                            )
                        elif text:
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

            # Check if user sent a voice message while in clone mode
            if "voice" in message and chat_id in users_awaiting_voice:
                voice_file_id = message["voice"]["file_id"]
                background_tasks.add_task(
                    process_voice_clone,
                    chat_id,
                    voice_file_id,
                    first_name
                )
            elif text:
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
