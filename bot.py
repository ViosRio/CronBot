import os
import json
import requests
from pathlib import Path
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import asyncio
import logging
from config import *

# WebShare Proxy Yönetimi
class ProxyManager:
    def __init__(self):
        self.proxy_list = []
        self.current_proxy = None
        self.load_proxies()
        
    def load_proxies(self):
        try:
            response = requests.get(
                f"https://proxy.webshare.io/api/v2/proxy/list/",
                headers={"Authorization": f"Token {WEBSHARE_API_KEY}"}
            )
            if response.status_code == 200:
                self.proxy_list = [
                    f"http://{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}"
                    for p in response.json()['results']
                ]
                logger.info(f"{len(self.proxy_list)} proxy yüklendi")
        except Exception as e:
            logger.error(f"Proxy yükleme hatası: {e}")

    def get_proxy(self):
        if not self.proxy_list:
            return None
        self.current_proxy = choice(self.proxy_list)
        return self.current_proxy

proxy_manager = ProxyManager()

# Cron Job Yöneticisi
class CronManager:
    def __init__(self):
        self.user_jobs = {}
        
    def add_job(self, user_id, cron_url):
        if user_id not in self.user_jobs:
            self.user_jobs[user_id] = []
        self.user_jobs[user_id].append(cron_url)
        
    def get_jobs(self, user_id):
        return self.user_jobs.get(user_id, [])
    
    def trigger_job(self, cron_url):
        try:
            proxy = proxy_manager.get_proxy() if USE_PROXY else None
            response = requests.get(
                cron_url,
                proxies={"http": proxy, "https": proxy} if proxy else None,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cron tetikleme hatası: {e}")
            return False

cron_manager = CronManager()

# Pyrogram Client
app = Client(
    "proxy-cron-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Başlangıç Mesajı
def get_start_message(user):
    return f"""
✨ **Merhaba {user.first_name}!** ✨

{emoji} **WebShare Proxy Destekli Cron Job Tetikleyici**

▸ Proxy ile güvenli tetikleme
▸ Zamanlanmış görev yönetimi
▸ Kolay kullanımlı arayüz

🚀 Kullanmaya başlamak için aşağıdaki butonları kullanın!
"""

# Butonlar
MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("⏰ Cron Ekle", callback_data="add_cron")],
    [
        InlineKeyboardButton("📋 Cron Listesi", callback_data="list_cron"),
        InlineKeyboardButton("⚡ Tetikle", callback_data="trigger_cron")
    ],
    [
        InlineKeyboardButton("🔧 Ayarlar", callback_data="settings"),
        InlineKeyboardButton("❌ Temizle", callback_data="clear_cron")
    ]
])

SETTINGS_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(f"Proxy {'✅' if USE_PROXY else '❌'}", callback_data="toggle_proxy"),
        InlineKeyboardButton("🔄 Proxy Yenile", callback_data="refresh_proxy")
    ],
    [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
])

# Komutlar
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(message.from_user),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.command("add"))
async def add_cron(client, message):
    if len(message.command) > 1:
        cron_url = message.command[1]
        cron_manager.add_job(message.from_user.id, cron_url)
        await message.reply(f"✅ Cron job eklendi: `{cron_url}`")
    else:
        await message.reply("Kullanım: /add <cron_url>")

@app.on_message(filters.command("list"))
async def list_cron(client, message):
    jobs = cron_manager.get_jobs(message.from_user.id)
    if jobs:
        await message.reply("📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs))
    else:
        await message.reply("Cron job listeniz boş")

# Callback Query Handler
@app.on_callback_query()
async def handle_callback(client, query):
    user = query.from_user
    data = query.data
    
    if data == "add_cron":
        await query.message.reply("Lütfen eklemek istediğiniz cron URL'sini gönderin:\nÖrnek: /add http://example.com/cron.php")
    
    elif data == "list_cron":
        jobs = cron_manager.get_jobs(user.id)
        if jobs:
            await query.edit_message_text(
                "📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs),
                reply_markup=MAIN_BUTTONS
            )
        else:
            await query.answer("Cron job listeniz boş", show_alert=True)
    
    elif data == "trigger_cron":
        jobs = cron_manager.get_jobs(user.id)
        if not jobs:
            await query.answer("Tetikleyecek cron job bulunamadı", show_alert=True)
            return
            
        await query.edit_message_text("⏳ Cron job'lar tetikleniyor...")
        results = []
        for job in jobs:
            success = cron_manager.trigger_job(job)
            results.append(f"{'✅' if success else '❌'} {job}")
        
        await query.edit_message_text(
            "⚡ Cron Tetikleme Sonuçları:\n\n" + "\n".join(results),
            reply_markup=MAIN_BUTTONS
        )
    
    elif data == "toggle_proxy":
        global USE_PROXY
        USE_PROXY = not USE_PROXY
        status = "AÇIK" if USE_PROXY else "KAPALI"
        await query.answer(f"Proxy modu {status}", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=SETTINGS_BUTTONS)
    
    elif data == "refresh_proxy":
        proxy_manager.load_proxies()
        await query.answer(f"{len(proxy_manager.proxy_list)} proxy yenilendi", show_alert=True)
    
    elif data == "clear_cron":
        cron_manager.user_jobs[user.id] = []
        await query.answer("Tüm cron job'lar temizlendi", show_alert=True)
        await query.edit_message_reply_markup(reply_markup=MAIN_BUTTONS)
    
    elif data == "settings":
        await query.edit_message_text("⚙️ Ayarlar", reply_markup=SETTINGS_BUTTONS)
    
    elif data == "back_to_main":
        await query.edit_message_text(get_start_message(user), reply_markup=MAIN_BUTTONS)

# Botu Başlat
if __name__ == "__main__":
    print("🚀 Proxy destekli cron bot başlatılıyor...")
    app.run()
