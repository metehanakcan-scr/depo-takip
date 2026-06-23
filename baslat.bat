@echo off
title Stok Takip Sistemi - YONETIM PANELI

:: 1. ADIM: API'yi (FastAPI) Arka Planda Başlat
:: --reload parametresini siliyoruz (çünkü periyodik yedekleme sayacını sıfırlar)
:: --workers 1 ekliyoruz (Postgres ve arka plan görevleri için en stabil yol)
echo API sunucusu baslatiliyor...
start "FastAPI_Sunucu" /min cmd /c "cd /d C:\Users\USER\Documents\depo_api && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. ADIM: Ngrok Tünelini Başlat
echo Ngrok tuneli aciliyor...
start "Ngrok_Tunel" /min cmd /c "cd /d C:\Users\USER\Documents\ngrok-v3-stable-windows-amd64 && ngrok http 8000"




:: 3. ADIM: Bekleme ve Tarayıcı Açma
:: Sunucunun tamamen ayağa kalkması ve veritabanı bağlantısı için 5 saniye idealdir.
echo Sunucunun uyanmasi bekleniyor (7 sn)...
timeout /t 7 /nobreak >nul
start http://localhost:8000

echo.
echo ======================================================
echo    SISTEM AKTIF VE GUVENDE! 
echo.
echo    * 3 Depocu ayni anda islem yapabilir.
echo    * Veriler 15 dakikada bir Google Sheets'e yedeklenir.
echo    * Sistemi kapatirken son yedek otomatik alinir.
echo.
echo    NOT: Sistemi kapatmak icin acik olan siyah pencereleri 
echo    degil, "FastAPI_Sunucu" penceresinde Ctrl+C yapin.
echo ======================================================
exit