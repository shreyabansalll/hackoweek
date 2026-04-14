import os
import tempfile
from gtts import gTTS

LANG_CODE_MAP = {
    "marathi": "mr",
    "hindi":   "hi",
    "english": "en",
}

def synthesize(text: str, language: str) -> str:
    try:
        lang_code = LANG_CODE_MAP.get(language.lower(), "hi")

        tts = gTTS(text=text, lang=lang_code, slow=False)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        temp_file.close()

        print(f"[TTS] Audio saved: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"[TTS ERROR] {type(e).__name__}: {e}")
        raise