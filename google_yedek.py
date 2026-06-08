"""
import gspread
from google.oauth2.service_account import Credentials  # Güncel token yapısı
import pandas as pd
from sqlalchemy import create_engine, inspect
import time
import os
import sys

# --- AYARLAR ---
SAYFA_ADI = "veritabani" 
JSON_DOSYASI = "anahtar.json"
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/depo_db"
KONTROL_DOSYASI = "son_yedek_kontrol.txt"
YEDEKLEME_ARALIGI = 3600  # 10 Dakika (Saniye cinsinden)

def tam_yedekle(force=False):
    # --- ZAMAN KONTROLÜ ---
    su_an = time.time()
    okunabilir_zaman = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(su_an))

    # Eğer zorunlu (--force) değilse zaman kilidini kontrol et
    if not force: 
        if os.path.exists(KONTROL_DOSYASI):
            try:
                with open(KONTROL_DOSYASI, "r") as f:
                    icerik = f.read().strip()
                    if icerik:
                        son_vakit_unix = icerik.split(" | ")[0]
                        son_vakit = float(son_vakit_unix)
                        
                        if su_an - son_vakit < YEDEKLEME_ARALIGI:
                            print(f"⚡ Zaman kilidi aktif, yedekleme atlandı. (Son yedek: {okunabilir_zaman})")
                            return
            except Exception as e:
                print(f"⚠️ Kontrol dosyası okunurken hata (Yine de devam ediliyor): {e}")

    try:
        if force:
            print(f">>> [ZORUNLU] Kapanış yedeği başlatıldı... ({okunabilir_zaman})")
        else:
            print(f">>> [OTOMATİK] Google Sheets yedeklemesi başlatıldı... ({okunabilir_zaman})")

        # --- BULUT BAĞLANTI AYARLARI ---
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(JSON_DOSYASI, scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open(SAYFA_ADI)

        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        tablo_isimleri = inspector.get_table_names()

        print(f"🚀 {len(tablo_isimleri)} tablo bulundu.")

        for tablo in tablo_isimleri:
            tablo_lower = tablo.lower().strip()

            # 1. Sorgu Belirleme
            # urunler ve stok_hareketleri şemadaki özel sütunlarıyla çekilir, diğerleri dinamik olarak tüm kolonları (SELECT *) alır.
            if tablo_lower == 'urunler':
                sorgu = 'SELECT "id", "barkod", "isim", "lot", "miktar", "kategori_id", "yer" FROM "urunler"'
            
            
            elif tablo_lower == 'stok_hareketleri':

                SON_ID_DOSYA = "son_stok_hareket_id.txt"

                if os.path.exists(SON_ID_DOSYA):
                    with open(SON_ID_DOSYA, "r") as f:
                        son_id = int(f.read().strip() or 0)
                else:
                    son_id = 0

                sorgu = f'''
                SELECT
                    "tarih",
                    "id",
                    "urun_barkod",
                    "urun_isim",
                    "urun_lot",
                    "miktar_degisimi",
                    "islem_tipi"
                FROM "stok_hareketleri"
                WHERE "id" > {son_id}
                ORDER BY "id"
                '''
            
   
            else:
                sorgu = f'SELECT * FROM "{tablo}"'


            # 2. Veriyi Çek
            df = pd.read_sql(sorgu, engine)

            # 3. Sıralama İşlemleri
            if tablo_lower == 'urunler' and 'isim' in df.columns:
                df = df.sort_values(by=['isim', 'lot'], ascending=[True, True])
                print(f"📊 {tablo_lower} sıralandı.")
            elif tablo_lower == 'stok_hareketleri' and 'tarih' in df.columns:
                df = df.sort_values(by=['tarih'], ascending=[False])
                print(f"📊 {tablo_lower} sıralandı.")

            # Tarih veri tiplerini metne çevirerek Google Sheets uyumlu hale getiriyoruz
            for col in df.select_dtypes(include=['datetime64', 'datetime']).columns:
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

            # Boş değerleri (NaN) boş metinle temizliyoruz
            df = df.fillna("")

            # Google Sheets üzerinde ilgili sekmenin varlığını kontrol ediyoruz
            try:
                worksheet = spreadsheet.worksheet(tablo_lower)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=tablo_lower, rows="100", cols="20")


            # stok_hareketleri sekmesi ilk kez oluşuyorsa başlıkları ekle
            if tablo_lower == "stok_hareketleri":

                mevcut_veri = worksheet.get_all_values()

                if not mevcut_veri and not df.empty:
                    worksheet.append_row(df.columns.tolist())




            
            # Sekmedeki tüm eski verileri tamamen temizliyoruz
            if tablo_lower != "stok_hareketleri":
                worksheet.clear()
            
           

            if tablo_lower == "stok_hareketleri":

                if not df.empty:

                    worksheet.append_rows(
                        df.values.tolist(),
                        value_input_option="RAW"
                    )

                    son_id = int(df["id"].max())

                    with open("son_stok_hareket_id.txt", "w") as f:
                        f.write(str(son_id))

                    print(f"✅ {len(df)} yeni hareket eklendi. Son ID: {son_id}")

            else:

                data_to_send = [df.columns.values.tolist()] + df.values.tolist()

                spreadsheet.values_update(
                    f'{tablo_lower}!A1',
                    params={'valueInputOption': 'RAW'},
                    body={'values': data_to_send}
                )







            print(f"✅ {tablo_lower} tablosu güncellendi. (Satır Sayısı: {len(df)})")
            time.sleep(1)  # Google API kota limitlerine takılmamak için 1 saniye bekle

        # --- KONTROL DOSYASINI GÜNCELLE ---
        with open(KONTROL_DOSYASI, "w") as f:
            f.write(f"{su_an} | {okunabilir_zaman}")

        print(f"\n NİHAYET! YEDEKLEME TAMAM. (Kayıt Zamanı: {okunabilir_zaman})")

    except Exception as e:
        print(f"❌ DETAYLI HATA: {e}")

if __name__ == "__main__":
    try:
        zorla = "--force" in sys.argv
        tam_yedekle(force=zorla)
    except KeyboardInterrupt:
        print("\n🛑 Yedekleme senin isteğinle durduruldu. Sistem kapanıyor...")
        sys.exit(0)


        """