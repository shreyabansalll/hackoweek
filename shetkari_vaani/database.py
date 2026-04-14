import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "shetkari_vaani.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            phone        TEXT NOT NULL,
            message_type TEXT,
            transcript   TEXT,
            language     TEXT,
            llm_response TEXT,
            timestamp    TEXT,
            success      INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone              TEXT PRIMARY KEY,
            first_seen         TEXT,
            last_seen          TEXT,
            total_queries      INTEGER DEFAULT 0,
            preferred_language TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized")

def log_conversation(phone: str, msg_type: str, transcript: str,
                     language: str, response: str, success: int = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()

        c.execute("""
            INSERT INTO conversations
            (phone, message_type, transcript, language, llm_response, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (phone, msg_type, transcript, language, response, now, success))

        c.execute("""
            INSERT INTO users (phone, first_seen, last_seen, total_queries, preferred_language)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(phone) DO UPDATE SET
                last_seen          = ?,
                total_queries      = total_queries + 1,
                preferred_language = ?
        """, (phone, now, now, language, now, language))

        conn.commit()
        conn.close()
        print(f"[DB] Logged conversation for {phone}")

    except Exception as e:
        print(f"[DB ERROR] {type(e).__name__}: {e}")