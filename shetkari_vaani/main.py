import os
import config
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response, JSONResponse

from handlers.whatsapp import download_media, upload_media, send_audio, send_text
from handlers.stt import transcribe
from handlers.llm import get_response
from handlers.tts import synthesize
from database import init_db, log_conversation

app = FastAPI(title="Shetkari Vaani")

# Initialize database on startup
init_db()

VERIFY_TOKEN = config.VERIFY_TOKEN


# ---------------------------
# WEBHOOK VERIFICATION (GET)
# ---------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode      = request.query_params.get("hub.mode") or request.query_params.get("hub_mode")
    token     = request.query_params.get("hub.verify_token") or request.query_params.get("hub_verify_token")
    challenge = request.query_params.get("hub.challenge") or request.query_params.get("hub_challenge")

    print(f"[VERIFY] Mode: {mode} | Token match: {token == VERIFY_TOKEN}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[VERIFY] Webhook verified successfully")
        return Response(content=challenge)

    return JSONResponse(content={"status": "webhook active"})


# ---------------------------
# RECEIVE MESSAGES (POST)
# ---------------------------
@app.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("\n========== NEW WEBHOOK EVENT ==========")
    print(data)
    background_tasks.add_task(process_message, data)
    return JSONResponse(content={"status": "ok"})


# ---------------------------
# PROCESS MESSAGE
# ---------------------------
async def process_message(data: dict):
    sender     = None
    msg_type   = None
    transcript = ""
    language   = "hindi"
    reply_text = ""

    try:
        entry    = data["entry"][0]["changes"][0]["value"]
        messages = entry.get("messages")

        if not messages:
            print("[INFO] No message found (likely status update)")
            return

        msg      = messages[0]
        sender   = msg["from"]
        msg_type = msg["type"]

        print(f"[INFO] Sender: {sender} | Type: {msg_type}")

        # ── AUDIO MESSAGE ──────────────────────────────────────────────
        if msg_type == "audio":
            mp3_path = None
            try:
                media_id   = msg["audio"]["id"]
                audio_bytes = download_media(media_id)

                transcript, raw_lang = transcribe(audio_bytes)
                reply_text, language = get_response(transcript, raw_lang)


                mp3_path    = synthesize(reply_text, language)
                uploaded_id = upload_media(mp3_path)
                send_audio(sender, uploaded_id)

                log_conversation(sender, "audio", transcript, language, reply_text, success=1)
                print("[SUCCESS] Voice reply sent")

            except Exception as e:
                print(f"[ERROR] Audio pipeline: {type(e).__name__}: {e}")
                log_conversation(sender, "audio", transcript, language, str(e), success=0)
                # Send fallback text so farmer isn't left hanging
                try:
                    send_text(sender, "माफ करा, आवाज संदेश प्रक्रिया करताना समस्या आली. कृपया पुन्हा प्रयत्न करा.")
                except:
                    pass

            finally:
                # ✅ Always clean up temp file
                if mp3_path and os.path.exists(mp3_path):
                    os.unlink(mp3_path)
                    print("[CLEANUP] Temp MP3 deleted")

        # ── TEXT MESSAGE ───────────────────────────────────────────────
        elif msg_type == "text":
            transcript = msg["text"]["body"]
            print(f"[INFO] Text received: {transcript}")

            try:
                reply_text, language = get_response(transcript, "hi")
                send_text(sender, reply_text)
                log_conversation(sender, "text", transcript, language, reply_text, success=1)
                print("[SUCCESS] Text reply sent")

            except Exception as e:
                print(f"[ERROR] Text pipeline: {type(e).__name__}: {e}")
                log_conversation(sender, "text", transcript, language, str(e), success=0)
                try:
                    send_text(sender, "माफ करें, अभी उत्तर देना संभव नहीं है। थोड़ी देर बाद प्रयास करें।")
                except:
                    pass

        else:
            print(f"[INFO] Unsupported message type: {msg_type}")

    except Exception as e:
        print(f"[FATAL ERROR] {type(e).__name__}: {e}")


# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Shetkari Vaani"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=False)