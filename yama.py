from sqlalchemy import create_engine, text

# Bağlantı adresini buraya elinle yazalım, en garantisi bu
# Eğer PostgreSQL kullanıyorsan adresi ona göre düzenle (main.py'deki ile aynı olsun)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost/depo_db"

# NOT: Eğer SQLite kullanıyorsan adres şöyledir: "sqlite:///./depo.db"
# Lütfen main.py dosyasındaki SQLALCHEMY_DATABASE_URL değişkenini kontrol et ve buraya yapıştır.

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def sutun_ekle():
    try:
        with engine.connect() as conn:
            # Sütunu ekle
            conn.execute(text("ALTER TABLE urunler ADD COLUMN yer VARCHAR;"))
            conn.commit()
            print("✅ 'yer' sutunu basariyla eklendi!")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ 'yer' sutunu zaten mevcut.")
        elif "not found" in str(e).lower() or "no such column" in str(e).lower():
             print(f"❌ Baglanti hatasi: {e}")
        else:
            print(f"❌ Hata olustu: {e}")

if __name__ == "__main__":
    sutun_ekle()