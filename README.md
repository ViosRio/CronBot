
# 🔥 CRONBOT 
### Proxy Destekli, Advanced Cron Job Tetikleyici
#### POWERED BY DEEPSEEK JOBS  

![CronBot Logo](https://raw.githubusercontent.com/ViosRio/CronBot/refs/heads/main/assets/logo.png)  

---

## 🌟 Özellikler 
✔ **Proxy Destekli** → WebShare.io API ile otomatik proxy rotasyonu  
✔ **Multi-CRON Yönetimi** → Aynı anda birden fazla URL tetikleme  
✔ **Log Sistemi** → Tüm tetiklemeler kayıt altında  
✔ **Kullanıcı Dostu UI** → Telegram bot arayüzüyle kolay kontrol  

---

## 🛠️ **Kurulum**  
1. **Gereksinimler**:  
   ```bash
   $ pip install pyrogram requests
   $ git clone https://github.com/ViosRio/CronBot
   ```
2. **Config Ayarları**:  
   `config.py` dosyasını düzenle:  
   ```python
   BOT_TOKEN = " "  # @BotFather'dan al
   WEBSHARE_API_KEY = " "  # webshare.io API key
   ```

3. **Botu Çalıştır**:  
   ```bash
   python bot.py
   ```

---

## 🤖 **Komutlar**  
| Komut | Açıklama |
|-------|----------|
| `/start` | Botu başlatır |
| `/add <url>` | Yeni CRON ekler |
| `/list` | Kayıtlı CRON'ları listeler |
| `/trigger` | Tüm CRON'ları tetikler |
| `/settings` | Proxy ayarlarını yönet |

---

## 💡 **Örnek Kullanım**  
1. Örnek CRON dosyası oluştur:
   ```php
   <?php
   // powered by deepseek
   file_put_contents('cron_log.txt', date('Y-m-d H:i:s')." - CRON çalıştı\n", FILE_APPEND);
   echo "OK";
   ?>
   ```
2. CRON ekle:
   ```bash
   /add https://siteniz.com/cron.php
   ```
3. Tetikle:
   ```bash
   /trigger
   ```

---

## 📜 Lisans
MIT License - Ücretsiz kullanım, değiştirme ve dağıtım! 

---

<div align="center">
  <img src="https://raw.githubusercontent.com/ViosRio/CronBot/refs/heads/main/assets/logo.png" width="150">
  <br>
  <strong>🚀 POWERED BY DEEPSEEK JOBS</strong>  
  <sub></sub>
</div>
```
