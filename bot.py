#
#
#-----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
# Powered by DeepSeek ❤️‍🔥

import os
import json
from pathlib import Path
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import asyncio
from random import choice
import logging
from config import *

# 1. CLIENT TANIMI (EN ÜSTTE)
app = Client(
    "roxy-mask",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Başlangıç Mesajı
def get_start_message(user):
    return f"""
✨ **SELAM** ✨

{emoji} **Panelinizin Görev Zamanlayıcı Derdi Olan Cron Job Tetikleyicisi**

▸ **AUTO** TEKRARLAYAN ZAMANLAMA
▸ **PROXY** PROXY DESTEKLİ MASKELEME
▸ **NOTEPAD** NOT DEFTERİ GİBİ KAYDET

 Powered by DeepSeek ❤️‍🔥
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🌟 EŞLEŞ", callback_data="find_partner")],
    [
        InlineKeyboardButton("📜 Yardım", callback_data="help"),
        InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings")
    ],
    [
        InlineKeyboardButton("👥 Arkadaşlar", callback_data="friends"),
        InlineKeyboardButton("👤 Kurucu", url=f"https://t.me/{OWNER_USERNAME}")
    ],
    [InlineKeyboardButton("❌ İşlemi durdur", callback_data="end_chat")]
])

SETTINGS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔒 PROXY Mod Aç/Kapat", callback_data="toggle_private")],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

HELP_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔍 Komutlar", callback_data="commands"),
        InlineKeyboardButton("💡 Nasıl Kullanılır?", callback_data="how_to_use")
    ],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

# Handler'lar
@app.on_message(filters.command("start"))
async def start(client, message):
    global total_users
    user = message.from_user
    if user.id not in user_friends:
        user_friends[user.id] = []
        total_users += 1
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(user),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.command("settings"))
async def settings(client, message):
    await message.reply("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)

@app.on_message(filters.command("private"))
async def toggle_private(client, message):
    user_id = message.from_user.id
    private_mode[user_id] = not private_mode.get(user_id, False)
    status = "açıldı" if private_mode[user_id] else "kapatıldı"
    await message.reply(f"🔒 Gizli mod {status}!")

@app.on_message(filters.command("add"))
async def add_friend(client, message):
    if len(message.command) > 1:
        friend_id = message.command[1]
        if message.from_user.id not in user_friends:
            user_friends[message.from_user.id] = []
        if friend_id not in user_friends[message.from_user.id]:
            user_friends[message.from_user.id].append()
            await message.reply(f"✅ Cron Job eklendi: ")
        else:
            await message.reply("⚠️ Bu Zamanlama Zaten listenizde!")
    else:
        await message.reply("Kullanım: /add viosrio.serv00.net/cron.php")

@app.on_message(filters.command("list"))
async def list_friends(client, message):
    friends = user_friends.get(message.from_user.id, [])
    if friends:
        await message.reply(f"👥 :\n NOTLAR" + "\n".join())
    else:
        await message.reply("Jobs listeniz boş 😢")

# Callback Query Handler
    
    elif data == "end_chat":
        if user.id in active_chats:
            partner_id = active_chats[user.id]
            await client.send_message(partner_id, "❌ işlem sonlandırıldı!", reply_markup=MAIN_BUTTONS)
            del active_chats[partner_id]
            del active_chats[user.id]
            await query.answer("işlem sonlandırıldı!", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=MAIN_BUTTONS)
        else:
            await query.answer("TEKRARLAYAN!", show_alert=True)
    
    elif data == "settings":
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "toggle_private":
        private_mode[user.id] = not private_mode.get(user.id, False)
        status = "açıldı" if private_mode[user.id] else "Proxy kapatıldı"
        await query.answer(f"Gizli mod {status}!")
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "friends":
        await query.edit_message_text("👥 **Notlar**", reply_markup=FRIENDS_BUTTONS)
    
    elif data == "add_friend":
        await query.answer("Arkadaş eklemek için: /add viosrio.serv00.net/cronjob.php", show_alert=True)
    
    elif data == "list_friends":
        friends = user_friends.get(user.id, [])
        if friends:
            await query.edit_message_text(f"👥 Notlar:\n" + "\n".join())
        else:
            await query.answer("Not listeniz boş 😢", show_alert=True)
    
    elif data == "help":
        await query.edit_message_text(
            "📚 **Yardım Menüsü**\n\n"
            "• /start = Botu başlat\n"
            "• /private = Vpn modu aç/kapat\n"
            "• /add serv.net/cron.php = Ekle\n"
            "• /list = Cron listesi\n"
            "• /settings = Ayarlar\n\n"
            reply_markup=HELP_BUTTONS
        )
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)

def is_not_command(_, __, m: Message):
    return not m.text.startswith('/')


# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
