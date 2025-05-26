
```markdown
# 🔥 **CRONBOT**  
### *Proxy Destekli, Advanced Cron Job Tetikleyici*  
#### POWERED BY DEEPSEEK JOBS  

![CronBot Logo](https://raw.githubusercontent.com/ViosRio/CronBot/refs/heads/main/assets/logo.png)  

---

## 🌟 **Özellikler**  
✔ **Proxy Destekli** → WebShare.io API ile otomatik proxy rotasyonu  
✔ **Multi-CRON Yönetimi** → Aynı anda birden fazla URL tetikleme  
✔ **Log Sistemi** → Tüm tetiklemeler kayıt altında  
✔ **Kullanıcı Dostu UI** → Telegram bot arayüzüyle kolay kontrol  

---

## 🛠️ **Kurulum**  
1. **Gereksinimler**:  
   ```bash
   pip install pyrogram requests
   ```
2. **Config Ayarları**:  
   `config.py` dosyasını düzenle:  
   ```python
   API_ID = "12345"          # my.telegram.org'dan al
   API_HASH = "abcdef123..." # my.telegram.org'dan al
   BOT_TOKEN = "123:ABC..."  # @BotFather'dan al
   WEBSHARE_API_KEY = "..."  # webshare.io API key
   START_IMG = "https://example.com/start.jpg"  # Start resmi URL
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

## 📜 **Lisans**  
MIT License - **Ücretsiz kullanım, değiştirme ve dağıtım!**  

---

<div align="center">
  <img src="https://raw.githubusercontent.com/ViosRio/CronBot/refs/heads/main/assets/logo.png" width="150">
  <br>
  <strong>🚀 POWERED BY DEEPSEEK JOBS</strong>  
  <sub>Next Generation Automation</sub>
</div>
```

### Kullanım Talimatları:
1. Bu kodu kopyala
2. GitHub repo'nda `README.md` dosyası oluştur
3. İçine yapıştır
4. Commit yap

Özel not: Ekran görüntüsü linklerini kendi screenshotlarınla değiştirmeyi unutma kanki! 😊
