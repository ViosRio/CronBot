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

# Veritabanı klasörü
DATA_DIR = Path("data")
LIST_DIR = DATA_DIR / "list"
LIST_DIR.mkdir(parents=True, exist_ok=True)

# Global değişkenler
active_chats = {}
waiting_users = {}
private_mode = {}
user_friends = {}  # Arkadaş listesi için
total_users = 0    # Toplam kullanıcı sayısı

# Başlangıç Mesajı
def get_start_message(user):
    global total_users
    emoji = choice(["🔥", "❤️", "🌹", "🎯"])
    private_status = "✅ AÇIK" if private_mode.get(user.id, False) else "❌ KAPALI"
    return f"""
✨ **RoxyMask - Anonim Sohbet Botu** ✨
👥 **Toplam Kullanıcılar:** {total_users}

{emoji} **Gizlilik Ve Eğlence Bir Arada!**

▸ **Eşleş** Butonuyla Rastgele Biriyle Sohbet Et
▸ **Gizli Mod:** {private_status}
▸ **Arkadaş Sayısı:** {len(user_friends.get(user.id, []))}

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
    [InlineKeyboardButton("❌ Sohbeti Bitir", callback_data="end_chat")]
])

SETTINGS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔒 Gizli Mod Aç/Kapat", callback_data="toggle_private")],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

FRIENDS_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Arkadaş Ekle", callback_data="add_friend")],
    [InlineKeyboardButton("📋 Arkadaş Listesi", callback_data="list_friends")],
    [InlineKeyboardButton("📨 Arkadaşa Mesaj Gönder", callback_data="message_friend")],
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
            user_friends[message.from_user.id].append(friend_id)
            await message.reply(f"✅ Arkadaş eklendi: {friend_id}")
        else:
            await message.reply("⚠️ Bu kullanıcı zaten arkadaş listenizde!")
    else:
        await message.reply("Kullanım: /add <kullanıcı_id>")

@app.on_message(filters.command("list"))
async def list_friends(client, message):
    friends = user_friends.get(message.from_user.id, [])
    if friends:
        await message.reply(f"👥 Arkadaşlarınız:\n" + "\n".join(friends))
    else:
        await message.reply("Arkadaş listeniz boş 😢")

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    user = query.from_user
    data = query.data
    
    if data == "find_partner":
        if user.id in active_chats:
            await query.answer("Zaten bir sohbettesiniz!", show_alert=True)
            return
        
        # Eşleşme işlemi
        if waiting_users:
            partner_id = next(iter(waiting_users))
            active_chats[user.id] = partner_id
            active_chats[partner_id] = user.id
            del waiting_users[partner_id]
            
            await client.send_message(partner_id, "✅ Eşleşme bulundu! Artık sohbet edebilirsiniz.", reply_markup=MAIN_BUTTONS)
            await query.answer("✅ Eşleşme bulundu! Artık sohbet edebilirsiniz.", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=MAIN_BUTTONS)
        else:
            waiting_users[user.id] = True
            await query.answer("🔎 Eşleşme aranıyor... Lütfen bekleyin.", show_alert=True)
    
    elif data == "end_chat":
        if user.id in active_chats:
            partner_id = active_chats[user.id]
            await client.send_message(partner_id, "❌ Sohbet sonlandırıldı!", reply_markup=MAIN_BUTTONS)
            del active_chats[partner_id]
            del active_chats[user.id]
            await query.answer("Sohbet sonlandırıldı!", show_alert=True)
            await query.edit_message_reply_markup(reply_markup=MAIN_BUTTONS)
        else:
            await query.answer("Aktif bir sohbetiniz yok!", show_alert=True)
    
    elif data == "settings":
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "toggle_private":
        private_mode[user.id] = not private_mode.get(user.id, False)
        status = "açıldı" if private_mode[user.id] else "kapatıldı"
        await query.answer(f"Gizli mod {status}!")
        await query.edit_message_text("⚙️ **Ayarlar**", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "friends":
        await query.edit_message_text("👥 **Arkadaşlar**", reply_markup=FRIENDS_BUTTONS)
    
    elif data == "add_friend":
        await query.answer("Arkadaş eklemek için: /add CEREN", show_alert=True)
    
    elif data == "list_friends":
        friends = user_friends.get(user.id, [])
        if friends:
            await query.edit_message_text(f"👥 Arkadaşlarınız:\n" + "\n".join(friends))
        else:
            await query.answer("Arkadaş listeniz boş 😢", show_alert=True)
    
    elif data == "message_friend":
        friends = user_friends.get(user.id, [])
        if friends:
            buttons = []
            for friend in friends:
                buttons.append([InlineKeyboardButton(f"📨 {friend}", callback_data=f"msg_{friend}")])
            buttons.append([InlineKeyboardButton("🔙 Geri", callback_data="friends")])
            await query.edit_message_text(
                "👥 Arkadaşını seç ve mesaj gönder:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await query.answer("Arkadaş listeniz boş 😢", show_alert=True)
    
    elif data.startswith("msg_"):
        friend_id = data[4:]
        await query.answer(f"Arkadaşınıza mesaj göndermek için: /msg {friend_id} <mesaj>", show_alert=True)
    
    elif data == "help":
        await query.edit_message_text(
            "📚 **Yardım Menüsü**\n\n"
            "• /start = Botu başlat\n"
            "• /private = Gizli modu aç/kapat\n"
            "• /add CEREN = Arkadaş ekle\n"
            "• /list = Arkadaş listesi\n"
            "• /settings = Ayarlar\n\n"
            "🌟 **Eşleş** butonuyla rastgele biriyle sohbet et!",
            reply_markup=HELP_BUTTONS
        )
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)

def is_not_command(_, __, m: Message):
    return not m.text.startswith('/')

@app.on_message(filters.text & filters.create(is_not_command))
async def forward_msg(client, message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            if private_mode.get(user_id, False):
                await client.send_message(partner_id, f"❤️ GİZLİ: {message.text}")
            else:
                await client.send_message(partner_id, f"@{message.from_user.username}: {message.text}")
        except Exception as e:
            logger.error(f"Mesaj iletme hatası: {e}")

# Botu Başlat
if __name__ == "__main__":
    print("✨ Bot başlatılıyor...")
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
