import requests
import config

BASE_URL = f"https://graph.facebook.com/v19.0/{config.WHATSAPP_PHONE_ID}"
HEADERS  = {"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"}

def download_media(media_id: str) -> bytes:
    try:
        url_resp = requests.get(
            f"https://graph.facebook.com/v19.0/{media_id}",
            headers=HEADERS,
            timeout=15
        )
        url_resp.raise_for_status()
        media_url = url_resp.json()["url"]

        audio_resp = requests.get(media_url, headers=HEADERS, timeout=15)
        audio_resp.raise_for_status()

        print(f"[WHATSAPP] Downloaded media {media_id} ({len(audio_resp.content)} bytes)")
        return audio_resp.content

    except Exception as e:
        print(f"[WHATSAPP ERROR] download_media: {type(e).__name__}: {e}")
        raise

def upload_media(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/media",
                headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
                files={"file": ("reply.mp3", f, "audio/mpeg")},
                data={"messaging_product": "whatsapp"},
                timeout=20
            )
            resp.raise_for_status()
            media_id = resp.json()["id"]
            print(f"[WHATSAPP] Uploaded media: {media_id}")
            return media_id

    except Exception as e:
        print(f"[WHATSAPP ERROR] upload_media: {type(e).__name__}: {e}")
        raise

def send_audio(to: str, media_id: str):
    try:
        resp = requests.post(
            f"{BASE_URL}/messages",
            headers=HEADERS,
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "audio",
                "audio": {"id": media_id}
            },
            timeout=15
        )
        resp.raise_for_status()
        print(f"[WHATSAPP] Audio sent to {to}")

    except Exception as e:
        print(f"[WHATSAPP ERROR] send_audio: {type(e).__name__}: {e}")
        raise

def send_text(to: str, text: str):
    try:
        resp = requests.post(
            f"{BASE_URL}/messages",
            headers=HEADERS,
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text}
            },
            timeout=15
        )
        resp.raise_for_status()
        print(f"[WHATSAPP] Text sent to {to}")

    except Exception as e:
        print(f"[WHATSAPP ERROR] send_text: {type(e).__name__}: {e}")
        raise