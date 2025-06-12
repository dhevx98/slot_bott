import telebot
import sqlite3
import json
import requests
import threading
import time
from datetime import datetime, timedelta
from telebot import types

TOKEN = '7260897874:AAH2hAjrKmuso_u2fWwkJmWZ80FzHNOuMJk'
bot = telebot.TeleBot(TOKEN)

# Path file JSON lokal
JSON_PATH = "slot_data.json"
# URL file JSON online
JSON_URL = "https://yourserver.com/slot_data.json"

# --- AUTO UPDATE JSON SETIAP 1 JAM ---
def auto_update_json():
    while True:
        try:
            r = requests.get(JSON_URL)
            if r.status_code == 200:
                with open(JSON_PATH, "w", encoding="utf-8") as f:
                    f.write(r.text)
                print(f"[AUTO] JSON diperbarui {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"[AUTO] Gagal fetch JSON. Status: {r.status_code}")
        except Exception as e:
            print("[AUTO] Gagal update JSON:", e)
        time.sleep(3600)  # setiap 1 jam

# Mulai auto-update saat bot dijalankan
threading.Thread(target=auto_update_json, daemon=True).start()

# --- DB Setup ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    is_vip INTEGER DEFAULT 0,
    access_until TEXT
)
""")
conn.commit()

# --- Cek Akses ---
def has_access(user_id):
    cursor.execute("SELECT access_until FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        end_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        return datetime.now() <= end_time
    return False

# --- /start ---
@bot.message_handler(commands=['start'])
def start_handler(message):
    user = message.from_user
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()
