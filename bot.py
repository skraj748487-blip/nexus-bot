import telebot
import os
import yt_dlp
import threading
from flask import Flask

# Dummy web server for Render Free Web Service
app = Flask('')

@app.route('/')
def home():
    return "NexusDrop is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Telegram Bot Setup
TOKEN = '8675102863:AAHmwX0vYSYiG945LXfvx794isMPxRGCeNs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"Salaam {user_name}! 🚀\n\n"
        "Main hu NexusDrop Engine.\n"
        "Kisi bhi video ya reel ka link bhejo, direct video mil jayegi!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        bot.reply_to(message, "Kripya valid video link bhejein.")
        return

    status_msg = bot.reply_to(message, "⚡ Processing... Video download ho rahi hai.")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("📤 Uploading...", chat_id=message.chat.id, message_id=status_msg.message_id)

        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="Downloaded via NexusDrop ⚡")

        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Error aaya: Link support nahi kiya ya file 50MB se badi hai.", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == '__main__':
    # Start web server in background thread
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Start bot polling
    bot.infinity_polling()
