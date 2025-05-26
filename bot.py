import os
import requests
import logging
import json
from random import choice
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

# Global değişken
USE_PROXY = False  # Varsayılan değer

class DataManager:
    @staticmethod
    def save_data(chat_id: int, data: dict):
        os.makedirs('data', exist_ok=True)
        with open(f'data/{chat_id}.json', 'w') as f:
            json.dump(data, f)
    
    @staticmethod
    def load_data(chat_id: int) -> dict:
        try:
            with open(f'data/{chat_id}.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

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
            # Fallback to alternative proxy API if primary fails
            self._try_fallback_proxy_api()

    def _try_fallback_proxy_api(self):
        try:
            response = requests.get(
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
                timeout=10
            )
            response.raise_for_status()
            
            self.proxy_list = [
                f"http://{line.strip()}"
                for line in response.text.split('\n')
                if line.strip()
            ]
            logger.info(f"✅ Fallback: {len(self.proxy_list)} proxy yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Fallback proxy hatası: {str(e)}")
            self.proxy_list = []

    def get_random_proxy(self):
        return choice(self.proxy_list) if self.proxy_list else None

class CronManager:
    def __init__(self):
        self.user_jobs = {}
        
    def add_job(self, user_id: int, cron_url: str):
        if not self._validate_url(cron_url):
            raise ValueError("Geçersiz URL formatı")
            
        if user_id not in self.user_jobs:
            self.user_jobs[user_id] = []
        
        if cron_url not in self.user_jobs[user_id]:
            self.user_jobs[user_id].append(cron_url)
            DataManager.save_data(user_id, {'jobs': self.user_jobs[user_id]})
            return True
        return False
    
    @staticmethod
    def _validate_url(url: str) -> bool:
        return url.startswith(('http://', 'https://'))
    
    def get_user_jobs(self, user_id: int) -> list:
        if user_id not in self.user_jobs:
            data = DataManager.load_data(user_id)
            self.user_jobs[user_id] = data.get('jobs', [])
        return self.user_jobs.get(user_id, [])
    
    def clear_jobs(self, user_id: int):
        if user_id in self.user_jobs:
            del self.user_jobs[user_id]
        DataManager.save_data(user_id, {'jobs': []})
    
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

# UI Elementleri
def get_start_message(user):
    return f"""
**Merhaba {user.first_name}!** 

**WebShare Proxy Destekli Cron Job Tetikleyici**

▸ Proxy İle Güvenli Tetikleme
▸ Zamanlanmış Görev Yönetimi
▸ Kolay Kullanımlı Arayüz


**Demo İçin Aşağıdaki Butonu kullanabilirsiniz:**
"""

START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("⏰ Cron Ekle", callback_data="add_cron")],
    [
        InlineKeyboardButton("📋 Cron Listesi", callback_data="list_cron"),
        InlineKeyboardButton("⚡ Tetikle", callback_data="trigger_cron")
    ],
    [
        InlineKeyboardButton("🔧 Ayarlar", callback_data="settings"),
        InlineKeyboardButton("🗑️ Temizle", callback_data="clear_cron")
    ],
    [InlineKeyboardButton("🛠️ Örnek Cron Dosyası Al", callback_data="get_example")]
])

def get_settings_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Proxy {'✅' if USE_PROXY else '❌'}", callback_data="toggle_proxy"),
            InlineKeyboardButton("🔄 Proxy Yenile", callback_data="refresh_proxy")
        ],
        [InlineKeyboardButton("🔙 Geri", callback_data="back_to_main")]
    ])

# Komutlar
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_message(message.from_user),
        reply_markup=START_BUTTONS
    )

@app.on_message(filters.command("add"))
async def add_cron_command(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Kullanım: /add ceren.xyz/cron.php")
    
    cron_url = message.command[1]
    try:
        if cron_manager.add_job(message.from_user.id, cron_url):
            await message.reply(f"✅ Cron Job Eklendi:\n`{cron_url}`")
        else:
            await message.reply("⚠️ Bu Cron Job Zaten Listenizde!")
    except ValueError as e:
        await message.reply(f"❌ Hata: {str(e)}")

@app.on_message(filters.command("list"))
async def list_cron_command(client, message):
    jobs = cron_manager.get_user_jobs(message.from_user.id)
    if not jobs:
        return await message.reply("📭 Cron Job Listeniz Boş")
    
    await message.reply(
        "📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs)
    )

# Callback Handler
@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    global USE_PROXY
    user = query.from_user
    data = query.data
    
    try:
        if data == "add_cron":
            await query.message.reply(
                "Lütfen Cron URL'sini Gönderin:\nÖrnek: /add ceren/xyz.com/cron.php\n\n"
                "Veya Yest için Aşağıdaki Örnek Dosyayı kullanabilirsiniz.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛠️ Örnek Cron Dosyası Al", callback_data="get_example")]
                ])
            )
        
        elif data == "sandbox/cron.php":
            # Create example cron file
            example_content = """<?php
// Basit Cron Örneği
file_put_contents('cron_log.txt', date('Y-m-d H:i:s') . " - Cron çalıştı\\n", FILE_APPEND);
echo "Cron başarıyla çalıştı!";
?>"""
            
            # Save temporarily
            with open("sandbox/cron.php", "w") as f:
                f.write(example_content)
            
            # Send to user
            await client.send_document(
                chat_id=query.message.chat.id,
                document="sandbox/cron.php",
                caption="📝 Örnek Cron Dosyası. Bu dosyayı Sunucunuza Yükleyip URL'sini Bota Ekleyebilirsiniz."
            )
            os.remove("sandbox/cron.php")
            await query.answer("Örnek Dosya Gönderildi!")
        
        elif data == "list_cron":
            jobs = cron_manager.get_user_jobs(user.id)
            if not jobs:
                return await query.answer("Cron job listeniz boş", show_alert=True)
            
            await query.edit_message_text(
                "📋 Cron Job Listesi:\n\n" + "\n".join(f"▸ `{job}`" for job in jobs),
                reply_markup=START_BUTTONS
            )
        
        elif data == "trigger_cron":
            jobs = cron_manager.get_user_jobs(user.id)
            if not jobs:
                return await query.answer("Tetikleyecek cron job yok", show_alert=True)
            
            await query.edit_message_text("⏳ Cron job'lar tetikleniyor...")
            results = []
            
            for job in jobs:
                success = cron_manager.trigger_job(job)
                results.append(f"{'✅' if success else '❌'} {job}")
                await asyncio.sleep(1)  # Rate limiting
            
            await query.edit_message_text(
                "⚡ Tetikleme Sonuçları:\n\n" + "\n".join(results),
                reply_markup=START_BUTTONS
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
        
        elif data == "clear_cron":
            cron_manager.clear_jobs(user.id)
            await query.answer("🗑️ Tüm cron job'lar temizlendi")
            await query.edit_message_reply_markup(reply_markup=START_BUTTONS)
        
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ Ayarlar\n\n"
                f"Proxy Durumu: {'✅ Açık' if USE_PROXY else '❌ Kapalı'}\n"
                f"Mevcut Proxy Sayısı: {len(proxy_manager.proxy_list)}",
                reply_markup=get_settings_buttons()
            )
        
        elif data == "back_to_main":
            await query.edit_message_text(
                get_start_message(user),
                reply_markup=START_BUTTONS
            )
    
    except Exception as e:
        logger.error(f"Callback hatası: {str(e)}")
        await query.answer("❌ Bir hata oluştu", show_alert=True)

if __name__ == "__main__":
    logger.info("🚀 Bot başlatılıyor...")
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    app.run()
