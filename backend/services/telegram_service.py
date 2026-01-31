import os
import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_voice_message(chat_id: str, audio_bytes: bytes, caption: str = None) -> dict:
    """Send a voice message via Telegram Bot API.

    Args:
        chat_id: Telegram chat ID or username
        audio_bytes: Audio file bytes (MP3 will be converted by Telegram)
        caption: Optional caption for the voice message
    """
    async with httpx.AsyncClient() as client:
        files = {"voice": ("message.mp3", audio_bytes, "audio/mpeg")}
        data = {"chat_id": chat_id}

        if caption:
            data["caption"] = caption

        response = await client.post(
            f"{TELEGRAM_API_URL}/sendVoice",
            files=files,
            data=data,
            timeout=30.0
        )

        result = response.json()

        if not result.get("ok"):
            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")

        return result


async def send_text_message(chat_id: str, text: str) -> dict:
    """Send a text message via Telegram Bot API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=30.0
        )

        result = response.json()

        if not result.get("ok"):
            raise Exception(f"Telegram API error: {result.get('description', 'Unknown error')}")

        return result
