#
import os
import requests
import logging
from pyrogram import Client, idle
from random import choice
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio
from config import *

# Log Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cronbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global değişkenler
USE_PROXY = False
AUTO_TRIGGER_INTERVAL = 5  # Otomatik tetikleme aralığı (saniye)
ANONYMOUS_MODE = True  # Anonim ekleme modu

class ProxyManager:
    def __init__(self):
        self.proxy_list = []
        self.load_proxies()
        
    def load_proxies(self):
        try:
            response = requests.get(
                "https://proxy.webshare.io/api/v2/proxy/list/",
                headers={"Authorization": f"Token {WEBSHARE_API_KEY}"},
                timeout=15
            )
            response.raise_for_status()
            
            self.proxy_list = [
                f"http://{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}"
                for p in response.json().get('results', [])
                if p.get('valid') and p.get('ports', {}).get('http')
            ]
            logger.info(f"✅ {len(self.proxy_list)} geçerli proxy yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Proxy yükleme hatası: {str(e)}")
            self.proxy_list = []

    def get_random_proxy(self):
        if not self.proxy_list:
            self.load_proxies()  # Proxy listesi boşsa yeniden yükle
        return choice(self.proxy_list) if self.proxy_list else None

class CronManager:
    def __init__(self):
        self.user_jobs = {}
        self.global_jobs = []  # Anonim joblar için
        
    def add_job(self, user_id: int, cron_url: str, anonymous=False):
        if not self._validate_url(cron_url):
            raise ValueError("Geçersiz URL formatı")
            
        if anonymous:
            if cron_url not in self.global_jobs:
                self.global_jobs.append(cron_url)
                return True
        else:
            if user_id not in self.user_jobs:
                self.user_jobs[user_id] = []
            
            if cron_url not in self.user_jobs[user_id]:
                self.user_jobs[user_id].append(cron_url)
                return True
        return False
    
    @staticmethod
    def _validate_url(url: str) -> bool:
        return url.startswith(('http://', 'https://'))
    
    def get_user_jobs(self, user_id: int) -> list:
        return self.user_jobs.get(user_id, [])
    
    def get_all_jobs(self, user_id: int) -> list:
        return self.get_user_jobs(user_id) + self.global_jobs
    
    def clear_jobs(self, user_id: int):
        if user_id in self.user_jobs:
            del self.user_jobs[user_id]
    
    def trigger_job(self, cron_url: str) -> bool:
        try:
            proxy = proxy_manager.get_random_proxy() if USE_PROXY else None
            response = requests.get(
                cron_url,
                proxies={"http": proxy, "https": proxy} if proxy else None,
                timeout=15
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Cron tetikleme hatası ({cron_url}): {str(e)}")
            return False

# Yönetici Örnekleri
proxy_manager = ProxyManager()
cron_manager = CronManager()

# Pyrogram Client
app = Client(
    "proxy-cron-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Otomatik Tetikleme Görevi
async def auto_trigger_task():
    while True:
        await asyncio.sleep(AUTO_TRIGGER_INTERVAL)
        if AUTO_TRIGGER_INTERVAL > 0:
            logger.info("⏰ Otomatik tetikleme başlatılıyor...")
            for user_id in list(cron_manager.user_jobs.keys()):
                for job in cron_manager.get_all_jobs(user_id):
                    cron_manager.trigger_job(job)

# UI Elementleri
def get_start_message(user):
    return f"""
**Merhaba {user.first_name}!** 

**WebShare Proxy Destekli Cron Job Tetikleyici**

▸ Proxy ile güvenli tetikleme
▸ Zamanlanmış görev yönetimi
▸ Kolay kullanımlı arayüz
▸ Otomatik tetikleme: {AUTO_TRIGGER_INTERVAL}s
▸ Anonim mod: {'✅' if ANONYMOUS_MODE else '❌'}

🚀 Kullanmaya başlamak için aşağıdaki butonları kullanın!
"""

MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("⏰ Cron Ekle", callback_data="add_cron")],
    [
        InlineKeyboardButton("📋 Cron Listesi", callback_data="list_cron"),
        InlineKeyboardButton("⚡ Tetikle", callback_data="trigger_cron")
    ],
    [
        InlineKeyboardButton("🔧 Ayarlar", callback_data="settings"),
        InlineKeyboardButton("🗑️ Temizle", callback_data="clear_cron"),
        InlineKeyboardButton("👤 Anonim Ekle", callback_data="anonymous_add")
    ]
])

def get_settings_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Proxy {'✅' if USE_PROXY else '❌'}", callback_data="toggle_proxy"),
            InlineKeyboardButton("🔄 Proxy Yenile", callback_data="refresh_proxy")
        ],
        [
            InlineKeyboardButton(f"Otomatik: {AUTO_TRIGGER_INTERVAL}s", callback_data="change_interval"),
            InlineKeyboardButton(f"Anonim: {'✅' if ANONYMOUS_MODE else '❌'}", callback_data="toggle_anonymous")
        ],
        [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
    ])

# Komutlar
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(message.from_user),
        reply_markup=MAIN_BUTTONS
    )

@app.on_message(filters.command("add"))
async def add_cron_command(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Kullanım: /add <cron_url>")
    
    cron_url = message.command[1]
    try:
        if cron_manager.add_job(message.from_user.id, cron_url):
            await message.reply(f"✅ Cron job eklendi:\n`{cron_url}`")
        else:
            await message.reply("⚠️ Bu cron job zaten listenizde!")
    except ValueError as e:
        await message.reply(f"❌ Hata: {str(e)}")

@app.on_message(filters.command("alist"))
async def anonymous_add_command(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Kullanım: /alist <cron_url> (Anonim Ekleme)")
    
    cron_url = message.command[1]
    try:
        if cron_manager.add_job(message.from_user.id, cron_url, anonymous=True):
            await message.reply(f"✅ Anonim cron job eklendi:\n`{cron_url}`")
        else:
            await message.reply("⚠️ Bu cron job zaten listeye eklenmiş!")
    except ValueError as e:
        await message.reply(f"❌ Hata: {str(e)}")

@app.on_message(filters.command("list"))
async def list_cron_command(client, message):
    jobs = cron_manager.get_all_jobs(message.from_user.id)
    if not jobs:
        return await message.reply("📭 Cron job listeniz boş")
    
    await message.reply(
        "📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs)
    )

# Callback Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    global USE_PROXY, AUTO_TRIGGER_INTERVAL, ANONYMOUS_MODE
    user = query.from_user
    data = query.data
    
    try:
        if data == "add_cron":
            await query.message.reply("Lütfen cron URL'sini gönderin:\nÖrnek: /add http://example.com/cron.php")
        
        elif data == "anonymous_add":
            await query.message.reply("Lütfen ANONİM cron URL'sini gönderin:\nÖrnek: /alist http://example.com/cron.php")
        
        elif data == "list_cron":
            jobs = cron_manager.get_all_jobs(user.id)
            if not jobs:
                return await query.answer("Cron job listeniz boş", show_alert=True)
            
            await query.edit_message_text(
                "📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs),
                reply_markup=MAIN_BUTTONS
            )
        
        elif data == "trigger_cron":
            jobs = cron_manager.get_all_jobs(user.id)
            if not jobs:
                return await query.answer("Tetikleyecek cron job yok", show_alert=True)
            
            await query.edit_message_text("⏳ Cron job'lar tetikleniyor...")
            results = []
            
            for job in jobs:
                success = cron_manager.trigger_job(job)
                results.append(f"{'✅' if success else '❌'} {job} - {datetime.now().strftime('%H:%M:%S')}")
                await asyncio.sleep(1)  # Rate limiting
            
            await query.edit_message_text(
                "⚡ Tetikleme Sonuçları:\n\n" + "\n".join(results),
                reply_markup=MAIN_BUTTONS
            )
        
        elif data == "toggle_proxy":
            USE_PROXY = not USE_PROXY
            await query.answer(f"Proxy modu {'AÇIK' if USE_PROXY else 'KAPALI'}")
            await query.edit_message_reply_markup(
                reply_markup=get_settings_buttons()
            )
        
        elif data == "refresh_proxy":
            proxy_manager.load_proxies()
            await query.answer(f"🔄 {len(proxy_manager.proxy_list)} proxy yenilendi")
        
        elif data == "change_interval":
            intervals = [5, 10, 30, 60]
            current_index = intervals.index(AUTO_TRIGGER_INTERVAL) if AUTO_TRIGGER_INTERVAL in intervals else 0
            new_index = (current_index + 1) % len(intervals)
            AUTO_TRIGGER_INTERVAL = intervals[new_index]
            await query.answer(f"⏱️ Otomatik tetikleme aralığı: {AUTO_TRIGGER_INTERVAL}s")
            await query.edit_message_reply_markup(
                reply_markup=get_settings_buttons()
            )
        
        elif data == "toggle_anonymous":
            ANONYMOUS_MODE = not ANONYMOUS_MODE
            await query.answer(f"Anonim mod {'AÇIK' if ANONYMOUS_MODE else 'KAPALI'}")
            await query.edit_message_reply_markup(
                reply_markup=get_settings_buttons()
            )
        
        elif data == "clear_cron":
            cron_manager.clear_jobs(user.id)
            await query.answer("🗑️ Tüm cron job'lar temizlendi")
            await query.edit_message_reply_markup(reply_markup=MAIN_BUTTONS)
        
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ Ayarlar",
                reply_markup=get_settings_buttons()
            )
        
        elif data == "back_to_main":
            await query.edit_message_text(
                get_start_message(user),
                reply_markup=MAIN_BUTTONS
            )
    
    except Exception as e:
        logger.error(f"Callback hatası: {str(e)}")
        await query.answer("❌ Bir hata oluştu", show_alert=True)


if __name__ == "__main__":
    logger.info("🚀 Bot başlatılıyor...")
    app.start()
    app.loop.create_task(auto_trigger_task())
    idle()  # Botu çalışır durumda tutar
    app.stop()
