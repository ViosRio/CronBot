<?php
/* 
  🚀 powered by deepseek 
  🔒 Güvenli & Otomatik Dizin Tarayıcı Cron Sistemi
  📂 Tüm alt klasörleri ve dosyaları listeler, log tutar.
*/

// === KULLANICI AYARLARI (Bu kısmı değiştirebilirsin) ===
$log_file = __DIR__ . '/cron_log.txt';  // Log dosyası yolu
$max_log_size = 2 * 1024 * 1024;       // Max log boyutu (2MB)
$allowed_ips = ['127.0.0.1'];           // İzin verilen IP'ler (CRON için)
$password_protect = false;              // Şifre koruması (Opsiyonel)
$cron_password = "deepseek123";         // Şifre (Aktifse gerekli)

// === GÜVENLİK KONTROLLERİ ===
header('Content-Type: text/plain');

// 1. Şifre koruması (Opsiyonel)
if ($password_protect && (!isset($_GET['pass']) || $_GET['pass'] !== $cron_password) {
    die("❌ Yetkisiz Erişim! Geçerli bir şifre girin.\nÖrnek: cron.php?pass=deepseek123");
}

// 2. Sadece CRON/localhost erişebilir (Ekstra güvenlik)
if (!in_array($_SERVER['REMOTE_ADDR'], $allowed_ips) && php_sapi_name() !== 'cli') {
    die("❌ Sadece sunucu üzerinden CRON ile çalıştırılabilir!\n");
}

// === FONKSİYONLAR ===
function scanDirectory($dir, &$results = []) {
    $files = scandir($dir);
    foreach ($files as $file) {
        if ($file == '.' || $file == '..') continue;
        $path = $dir . '/' . $file;
        $results[] = $path;
        if (is_dir($path)) scanDirectory($path, $results);
    }
    return $results;
}

function clearIfLarge($file, $max_size) {
    if (file_exists($file) && filesize($file) > $max_size) {
        file_put_contents($file, "🔄 Log temizlendi @" . date('Y-m-d H:i:s') . "\n---\n");
    }
}

// === CRON İŞLEMLERİ ===
clearIfLarge($log_file, $max_log_size);

try {
    $log_content = "⏰ CRON Çalıştı: " . date('d.m.Y H:i:s') . "\n";
    $all_files = scanDirectory(__DIR__);
    
    $log_content .= "📋 TOPLAM " . count($all_files) . " DOSYA/KLASÖR:\n";
    $log_content .= implode("\n", $all_files) . "\n\n";
    
    file_put_contents($log_file, $log_content, FILE_APPEND);
    echo "✅ Başarılı! Tüm dosyalar log'a kaydedildi.\n";
    
} catch (Exception $e) {
    file_put_contents($log_file, "❌ HATA: " . $e->getMessage() . "\n", FILE_APPEND);
    echo "⚠️ Hata: " . $e->getMessage() . "\n";
}
?>
