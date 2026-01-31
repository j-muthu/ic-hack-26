import os
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Use a calm, supportive voice
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice


def generate_voice_message(text: str) -> bytes:
    """Generate speech audio from text using ElevenLabs."""
    audio_generator = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
    )

    # Collect all audio chunks into bytes
    audio_bytes = b"".join(audio_generator)
    return audio_bytes
