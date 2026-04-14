import os
import tempfile
import config
from groq import Groq

client = Groq(api_key=config.GROQ_API_KEY)

def transcribe(audio_bytes: bytes) -> tuple:
    tmp_path = None
    try:
        # Write bytes to temp file
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=("audio.ogg", audio_file, "audio/ogg"),
                model="whisper-large-v3",
                response_format="verbose_json"
            )

        text = result.text.strip()
        lang = getattr(result, "language", "hi")  # "hi", "mr", "en"

        print(f"[STT] Transcript: {text}")
        print(f"[STT] Detected language: {lang}")

        return text, lang

    except Exception as e:
        print(f"[STT ERROR] {type(e).__name__}: {e}")
        return "", "hi"

    finally:
        # Always clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)