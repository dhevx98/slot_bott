import telebot
import time
import sqlite3
import json
import requests
import threading
from datetime import datetime, timedelta

TOKEN = "7260897874:AAH2hAjrKmuso_u2fWwkJmWZ80FzHNOuMJk"
JSON_URL = "https://raw.githubusercontent.com/USERNAME/REPO/main/slot_data.json"  # Ganti dengan URL raw kamu

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expired_at TEXT,
        is_vip INTEGER DEFAULT 0
    )
""")
conn.commit()

slot_data = {}

def update_slot_data():
    global slot_data
    try:
        r = requests.get(JSON_URL)
        slot_data = r.json()
        print("[✓] Data slot updated.")
    except Exception as e:
        print("[!] Gagal update JSON:", e)

# Auto update tiap 1 jam
def auto_update_loop():
    while True:
        update_slot_data()
        time.sleep(3600)

threading.Thread(target=auto_update_loop, daemon=True).start()

def check_access(user_id):
    cur.execute("SELECT expired_at, is_vip FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        return False, False
    expired_at, is_vip = row
    if datetime.now() < datetime.fromisoformat(expired_at):
        return True, bool(is_vip)
    return False, bool(is_vip)

def add_access(user_id, duration_hours, is_vip=False):
    expired_time = datetime.now() + timedelta(hours=duration_hours)
    cur.execute("REPLACE INTO users (user_id, expired_at, is_vip) VALUES (?, ?, ?)",
                (user_id, expired_time.isoformat(), int(is_vip)))
    conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎰 Selamat datang di *Panel Pola Slot*\n\nKetik /akses untuk beli akses\nKetik /panel untuk buka analisa pola\nKetik /vip untuk upgrade VIP", parse_mode="Markdown")

@bot.message_handler(commands=['akses'])
def send_key_options(message):
    user_id = message.from_user.id
    text = (
        "*Akses Server User Slot Machine*\n\n"
        "6 jam  – Rp30.000\n"
        "24 jam – Rp50.000\n"
        "3 hari – Rp85.000\n"
        "7 hari – Rp100.000\n"
        "14 hari – Rp150.000\n"
        "30 hari – Rp300.000\n\n"
        "_Kirim bukti ke admin setelah transfer QRIS._"
    )
    bot.send_photo(user_id, open("qris_image.jpg", "rb"), caption=text, parse_mode="Markdown")

@bot.message_handler(commands=['vip'])
def send_vip_info(message):
    text = (
        "*Upgrade ke VIP*\n\n"
        "🎯 Fitur lebih lengkap:\n"
        "- Panduan melihat room scatter jackpot\n"
        "- Pola akurat berdasarkan data\n"
        "- Analisa visual room\n\n"
        "*Harga VIP:*\n"
        "- 6 jam: Rp10.000\n"
        "- 24 jam: Rp25.000\n"
        - 3 hari: Rp50.000\n"
        "- 7 hari: Rp75.000\n"
        "- 30 hari: Rp100.000\n"
        "\n🔐 VIP Permanent: Rp500.000"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['panel'])
def send_panel(message):
    user_id = message.from_user.id
    access, is_vip = check_access(user_id)
    if not access:
        bot.reply_to(message, "⛔ Kamu belum punya akses.\nGunakan /akses untuk beli key.")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🎮
