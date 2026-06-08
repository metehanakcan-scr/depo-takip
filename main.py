import os
import io
import asyncio
import random
import subprocess
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, UploadFile, File, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import (
    create_engine, text, cast, String, func, case, 
    Column, Integer, ForeignKey, DateTime, Boolean
)
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError

# Projenize ait yerel importlar
import models
import schemas
import database
from database import engine, SessionLocal, Base

from urllib.parse import unquote

# ... (Mevcut importlarının altına ekle) ...








# --- AYARLAR VE BAĞLANTI ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# Bağlantı havuzunu 3 kişi için optimize ettim
engine = create_engine(DATABASE_URL, pool_size=15, max_overflow=25)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- YEDEKLEME DÖNGÜSÜ ---
async def periyodik_google_yedekleme():
    # API ilk açıldığında 30 saniye bekle ki sistem kendine gelsin
    await asyncio.sleep(30) 
    while True:
        try:
            bat_yolu = r"C:\Users\USER\Documents\depo_api\yedekleme.bat"
            # Popen kullanıyoruz ki yedekleme yapılırken API donmasın, işlemler aksamasın
            subprocess.Popen([bat_yolu], shell=True)
            print("\n>>> [OTOMATİK] Google Sheets yedeklemesi başlatıldı.")
        except Exception as e:
            print(f"\n>>> [HATA] Yedekleme tetiklenemedi: {e}")
        
        # Yarım saat (1800 saniye) bekle
        await asyncio.sleep(1800)



# --- LIFESPAN (Sistemin Kalbi) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. AÇILIŞ: Yedekleme görevini başlat
    app.mount("/static", StaticFiles(directory="static"), name="static")
    task = asyncio.create_task(periyodik_google_yedekleme())
    print(">>> [SİSTEM] API Başlatıldı ve Yedekleme Aktif.")
    
    yield  # API burada çalışıyor (Depocular işlem yapıyor...)

    # 2. KAPANIŞ: Zorunlu Final Yedeği
    print("\n>>> [SİSTEM] Sunucu kapatılıyor, ZORUNLU final yedeği alınıyor...")
    task.cancel()
    
    try:
        # Burada yeni oluşturduğumuz --force içerikli bat dosyasını çağırıyoruz
        final_bat = r"C:\Users\USER\Documents\depo_api\final_yedek.bat"
        subprocess.run([final_bat], shell=True, check=True) 
        print(">>> [SİSTEM] Final yedeği zamana bakılmaksızın alındı.")
    except Exception as e:
        print(f">>> [HATA] Final yedeği başarısız: {e}")

# Uygulamayı sadece lifespan ile başlat abi, on_event("shutdown")'a gerek kalmadı
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# --- VERİTABANI HAZIRLIK ---
def veritabani_hazirlik():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE urunler DROP CONSTRAINT IF EXISTS urunler_barkod_key"))
            conn.commit()
            print("✅ Barkod benzersizlik kilidi başarıyla kaldırıldı.")
        except Exception as e:
            print(f"⚠️ Kilit kaldırılamadı: {e}")

        for col in ["lot", "yer"]:
            try:
                conn.execute(text(f"ALTER TABLE urunler ADD COLUMN IF NOT EXISTS {col} VARCHAR"))
                conn.commit()
            except: pass

        try:
            conn.execute(text("ALTER TABLE stok_hareketleri ADD COLUMN IF NOT EXISTS urun_lot VARCHAR"))
            conn.commit()
        except: pass

        yetki_sutunlari = ["can_add_stock", "can_exit_stock", "can_edit_product", "can_delete", "can_manage_users", "can_see_logs"]
        for col in yetki_sutunlari:
            try:
                conn.execute(text(f"ALTER TABLE roller ADD COLUMN IF NOT EXISTS {col} BOOLEAN DEFAULT TRUE"))
                conn.commit()
            except: pass

        try:
            conn.execute(text("ALTER TABLE kullanicilar ADD COLUMN IF NOT EXISTS rol_id INTEGER"))
            conn.commit()
        except: pass

        try:
            check = conn.execute(text("SELECT id FROM roller WHERE ad = 'ADMIN'")).fetchone()
            if not check:
                conn.execute(text("""
                    INSERT INTO roller (ad, can_add_stock, can_exit_stock, can_edit_product, can_delete, can_manage_users, can_see_logs)
                    VALUES ('ADMIN', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)
                """))
                conn.commit()
        except: pass

veritabani_hazirlik()

# --- GLOBAL CONTEXT & MIDDLEWARE ---
templates.env.globals.update(
    get_user=lambda request: getattr(request.state, "user", {"kullanici_adi": "GİRİŞ YOK", "rol_adi": "MİSAFİR"})
)




@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    oturum = request.cookies.get("oturum")
    user = None
    if oturum:
        db = SessionLocal()
        try:
            user_db = db.query(models.Kullanici).filter(models.Kullanici.kullanici_adi == oturum).first()
            if user_db and user_db.ait_oldugu_rol:
                r = user_db.ait_oldugu_rol
                user = {
                    "id": user_db.id,
                    "kullanici_adi": user_db.kullanici_adi,
                    "rol_adi": r.ad,
                    "can_add_stock": r.can_add_stock,
                    "can_exit_stock": r.can_exit_stock,
                    "can_edit_product": r.can_edit_product,
                    "can_delete": r.can_delete,
                    "can_manage_users": r.can_manage_users,
                    "can_see_logs": r.can_see_logs
                }
            elif user_db:
                user = {"kullanici_adi": user_db.kullanici_adi, "rol_adi": "YETKİSİZ", "can_add_stock": False}
        except Exception:
            user = {"kullanici_adi": oturum, "rol_adi": "HATA", "can_add_stock": True}
        finally:
            db.close()
    
    # GİRİŞ YAPMAMIŞ KULLANICILAR İÇİN İZİN VERİLEN BEYAZ LİSTE (MİDDLEWARE)
    if not user and request.url.path not in ["/login", "/kayit", "/static"] and not request.url.path.startswith("/sifre-yenileme") and not request.url.path.startswith("/static"):
        return RedirectResponse(url="/login")
    
    request.state.user = user if user else {"kullanici_adi": "GİRİŞ YOK", "rol_adi": "MİSAFİR"}
    response = await call_next(request)
    return response

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- GİRİŞ / ÇIKIŞ ---
@app.get("/login", response_class=HTMLResponse)
def login_sayfasi(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_islem(response: Response, kullanici_adi: str = Form(...), sifre: str = Form(...), db: Session = Depends(get_db)):
    k_adi = kullanici_adi.strip().upper()
    user = db.query(models.Kullanici).filter(models.Kullanici.kullanici_adi == k_adi, models.Kullanici.sifre == sifre).first()
    if not user: return RedirectResponse(url="/login?hata=1", status_code=303)
    res = RedirectResponse(url="/stok-paneli/", status_code=303)
    res.set_cookie(key="oturum", value=user.kullanici_adi)
    return res

@app.get("/logout")
def logout():
    res = RedirectResponse(url="/login")
    res.delete_cookie("oturum")
    return res



# 1. Kullanıcıyı kayıt formuna yönlendiren link (GET)
@app.get("/kayit", response_class=HTMLResponse)
async def kayit_sayfasi(request: Request):
    # 'hata' parametresini de ekledik ki HTML şablonu hata vermesin
    return templates.TemplateResponse("kayit.html", {"request": request, "hata": None})

# 2. Form doldurulup gönderildiğinde çalışacak işlem (POST)
@app.post("/kayit")
async def kayit_islemi(
    request: Request,
    username: str = Form(...), 
    password: str = Form(...),
    email:    str = Form(...), 
    db: Session = Depends(get_db)
):
    # Sizin login mantığınızla eşleşmesi için kullanıcı adını temizleyip büyük harfe çeviriyoruz
    k_adi = username.strip().upper()
    
    # Kullanıcı veritabanında var mı kontrolü
    mevcut_user = db.query(models.Kullanici).filter(models.Kullanici.kullanici_adi == k_adi).first()
    
    if mevcut_user:
        return templates.TemplateResponse("kayit.html", {"request": request, "hata": "Bu kullanıcı adı zaten alınmış!"})
    
    # Yeni kullanıcıyı projenizin kurallarına göre oluşturuyoruz
    # NOT: Yeni kayıt olanlara varsayılan bir rol ID'si (Örn: rol_id=2 veya projenize göre neyse) eklemek isteyebilirsiniz.
    yeni_kullanici = models.Kullanici(
        kullanici_adi=k_adi,
        sifre=password,
        email=email,      # 2. Veritabanındaki NOT NULL kuralını bu satırla besliyoruz
        rol_id=3  # Projenizde şifreleme varsa fonksiyonunuzu buraya uygulayın
    )
    
    db.add(yeni_kullanici)
    db.commit()
    
    # Kayıt başarılı! Kullanıcıyı giriş yapabilmesi için login sayfasına yönlendiriyoruz
    return RedirectResponse(url="/login?kayit=basarili", status_code=303)

# --- SAYFA ROTALARI ---
@app.get("/")
def root(): return RedirectResponse(url="/stok-paneli/")

@app.get("/stok-paneli/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    urunler = db.query(models.UrunModel).all()
    istatistik = {"cesit": len(urunler), "adet": sum(u.miktar for u in urunler), "kritik": len([u for u in urunler if u.miktar < 10])}
    return templates.TemplateResponse("index.html", {"request": request, "istatistik": istatistik, "urunler": urunler})

@app.get("/urun-listesi/", response_class=HTMLResponse)
def urun_listesi(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("urunler.html", {"request": request, "urunler": db.query(models.UrunModel).all()})

@app.get("/urun-yonetimi/", response_class=HTMLResponse)
def urun_yonetimi_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user.get("can_add_stock"): raise HTTPException(status_code=403)
    return templates.TemplateResponse("ekle.html", {"request": request, "urunler": db.query(models.UrunModel).all(), "kategoriler": db.query(models.Kategori).all(), "yerler": db.query(models.DepoYeri).all()})

@app.get("/stok-cikisi-sayfasi/", response_class=HTMLResponse)
def stok_cikisi_sayfasi(request: Request, db: Session = Depends(get_db)):
    if not request.state.user.get("can_exit_stock"): raise HTTPException(status_code=403)
    return templates.TemplateResponse("cikis.html", {"request": request, "urunler": db.query(models.UrunModel).all(), "musteriler": db.query(models.Musteri).all()})

@app.get("/stok-hareketleri/", response_class=HTMLResponse)

def hareket_sayfasi(
    request: Request, 
    f_islem_no: str = None, 
    f_urun: str = None, 
    f_lot: str = None, 
    f_islem: str = None, 
    f_musteri: str = None, 
    f_tarih: str = None, 
    f_not: str = None, 
    db: Session = Depends(get_db)
):
    user = request.state.user
    if not user.get("can_see_logs") and user.get("rol_adi") != "ADMIN":
        return RedirectResponse(url="/stok-paneli/?hata=yetki")
        
    query = db.query(models.StokHareketi)
    
    # Canlı filtreleme koşulları
    if f_islem_no: 
        temiz_no = f_islem_no.replace("#", "").strip()
        query = query.filter(models.StokHareketi.islem_no.ilike(f"%{temiz_no}%"))
    if f_urun: query = query.filter(models.StokHareketi.urun_isim.ilike(f"%{f_urun}%"))
    if f_lot: query = query.filter(models.StokHareketi.urun_lot.ilike(f"%{f_lot}%"))
    if f_islem: query = query.filter(models.StokHareketi.islem_tipi.ilike(f"%{f_islem}%"))
    if f_musteri: 
        query = query.filter(
            (models.StokHareketi.musteri_ad.ilike(f"%{f_musteri}%")) | 
            (models.StokHareketi.islem_nedeni.ilike(f"%{f_musteri}%"))
        )
    if f_tarih: query = query.filter(func.to_char(models.StokHareketi.tarih, 'DD.MM.YYYY HH24:MI').ilike(f"%{f_tarih}%"))
    if f_not: query = query.filter(models.StokHareketi.aciklama.ilike(f"%{f_not}%"))
    
    # Önce ham fitrelenmiş hareketleri çekiyoruz
    filtreli_hareketler = query.order_by(models.StokHareketi.id.desc()).all()
    
    # --- KRİTİK NOKTA: İşlem Numarasına Göre Gruplama Mantığı ---
    # Eğer kullanıcı bir arama yaptıysa (örn: CRAFT), o arama sonucuna eşleşen İŞLEM NUMARALARINI topluyoruz.
    # Ardından o işlem numaralarına ait TÜM alt kalemleri getiriyoruz ki kart bozulmasın, diğer ürünler de görünsün.
    if f_urun or f_lot or f_islem or f_musteri or f_tarih or f_not or f_islem_no:
        eslesen_islem_nolar = {h.islem_no for h in filtreli_hareketler if h.islem_no}
        # Esleşen tüm işlem numaralarının altındaki bütün kalemleri temizce çekiyoruz
        tum_kalemler = db.query(models.StokHareketi).filter(models.StokHareketi.islem_no.in_(eslesen_islem_nolar)).order_by(models.StokHareketi.id.desc()).all()
    else:
        # Arama yoksa direkt son hareketleri alıyoruz (Performans için sınırlandırılabilir, limit 300)
        tum_kalemler = db.query(models.StokHareketi).order_by(models.StokHareketi.id.desc()).limit(300).all()

    # Bellekte gruplama işlemi
    gruplanmis = {}
    for h in tum_kalemler:
        no = h.islem_no if h.islem_no else f"KAYIT-{h.id}"
        if no not in gruplanmis:
            gruplanmis[no] = {
                "islem_no": h.islem_no or "-",
                "tarih": h.tarih,
                "islem_tipi": h.islem_tipi or "DİĞER",
                "musteri_ad": h.musteri_ad,
                "islem_nedeni": h.islem_nedeni,
                "aciklama": h.aciklama or "-",
                "islem_yapan": h.islem_yapan or "SİSTEM",
                "kalemler": []
            }
        gruplanmis[no]["kalemler"].append({
            "urun_isim": h.urun_isim,
            "urun_lot": h.urun_lot or "-",
            "miktar_degisimi": h.miktar_degisimi
        })

    # Kartları tarihe göre en yeni en üstte olacak şekilde listeye çeviriyoruz
    kart_listesi = sorted(gruplanmis.values(), key=lambda x: x["tarih"] if x["tarih"] else datetime.min, reverse=True)

    return templates.TemplateResponse("hareketler.html", {
        "request": request, 
        "kart_listesi": kart_listesi, # Şablona artık düz tablo değil gruplanmış kart yapısı gidiyor
        "filtreler": {
            "islem_no": f_islem_no or "",
            "urun": f_urun or "", 
            "lot": f_lot or "", 
            "islem": f_islem or "", 
            "musteri": f_musteri or "", 
            "tarih": f_tarih or "",
            "not": f_not or ""
        }
    })

@app.get("/hizli-sayim", response_class=HTMLResponse)
async def hizli_sayim_sayfasi(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user.get("can_edit_product"): return RedirectResponse(url="/stok-paneli/")
    return templates.TemplateResponse("hizli_sayim.html", {"request": request, "user": user})

@app.post("/api/hizli-sayim-kaydet")
async def hizli_sayim_kaydet(data: dict, db: Session = Depends(get_db)):
    try:
        barkod_no = str(data.get('barkod', ''))
        gelen_isim = data.get('urun_adi', 'BİLİNMEYEN ÜRÜN').strip().upper()
        gelen_lot = data.get('lot_no', '').strip().upper()
        gelen_miktar = float(data.get('miktar', 0))

        # 1. Ürün/Lot kontrolü ve yeni tanım (Mevcut mantığını bozmadık)
        urun_lot_kontrol = db.query(models.UrunModel).filter(
            models.UrunModel.barkod == barkod_no, 
            models.UrunModel.lot == gelen_lot
        ).first()

        if not urun_lot_kontrol:
            yeni_tanim = models.UrunModel(
                barkod=barkod_no, 
                isim=gelen_isim, 
                miktar=0, 
                lot=gelen_lot, 
                yer="SAYIMDA TANIMLANDI"
            )
            db.add(yeni_tanim)
            db.flush()
        else:
            # Eğer ürün zaten varsa ama ismi değişmişse/yoksa ismi güncelle
            urun_lot_kontrol.isim = gelen_isim

        # 2. Sayım tablosuna kayıt
        mevcut_sayim = db.query(models.Sayim).filter(
            models.Sayim.barkod == barkod_no, 
            models.Sayim.lot_no == gelen_lot
        ).first()

        if mevcut_sayim:
            mevcut_sayim.miktar += gelen_miktar
            # Sayım tablosunda urun_adi sütunu varsa orayı da güncelle
            if hasattr(mevcut_sayim, 'urun_adi'):
                mevcut_sayim.urun_adi = gelen_isim
            mevcut_sayim.kayit_tarihi = datetime.now()
        else:
            # YENİ SAYIM KAYDI: Burada urun_adi sütunu varsa onu da ekliyoruz
            # Eğer models.Sayim içinde urun_adi tanımlı değilse hata vermemesi için kwargs kullanıyoruz
            sayim_verisi = {
                "barkod": barkod_no,
                "lot_no": gelen_lot,
                "miktar": gelen_miktar,
                "kayit_tarihi": datetime.now()
            }
            
            # Eğer Sayim modelinde urun_adi sütunu varsa ekle
            if hasattr(models.Sayim, 'urun_adi'):
                sayim_verisi["urun_adi"] = gelen_isim
            
            yeni_sayim = models.Sayim(**sayim_verisi)
            db.add(yeni_sayim)

        db.commit()
        return {"status": "ok", "message": "Miktar güncellendi."}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


        
@app.post("/api/sayimlari-sifirla")
async def sayimlari_sifirla(data: dict, db: Session = Depends(get_db)):
    if data.get("sifre") == "1881":
        try:
            db.query(models.Sayim).delete(); db.commit()
            return {"status": "ok", "message": "Sıfırlandı."}
        except Exception as e:
            db.rollback(); return {"status": "error", "message": str(e)}
    return {"status": "wrong_password", "message": "Hatalı şifre."}

@app.get("/api/sayim-indir")
async def sayim_indir(db: Session = Depends(get_db)):
    query = db.query(models.Sayim).all()
    data = [{"Barkod": s.barkod, "Ürün Adı": getattr(s, 'urun_adi', ""), "Lot No": s.lot_no, "Miktar": s.miktar, "Kayıt Tarihi": s.kayit_tarihi.strftime("%Y-%m-%d %H:%M") if s.kayit_tarihi else ""} for s in query]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sayımlar')
    output.seek(0)
    return StreamingResponse(output, headers={'Content-Disposition': 'attachment; filename="sayim_listesi.xlsx"'}, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/stok-hareket-excel/")
async def stok_hareket_excel(search: str = "", islem_tipi: str = "", db: Session = Depends(get_db)):
    query = db.query(models.StokHareketi)
    if search: query = query.filter((models.StokHareketi.urun_barkod.contains(search)) | (models.StokHareketi.urun_isim.contains(search.upper())))
    if islem_tipi: query = query.filter(models.StokHareketi.islem_tipi.contains(islem_tipi))
    hareketler = query.order_by(models.StokHareketi.id.desc()).all()
    data = [{"Tarih/Saat": h.tarih.strftime("%Y-%m-%d %H:%M") if h.tarih else "-", "Barkod": h.urun_barkod, "Ürün İsmi": h.urun_isim, "Miktar Değişimi": h.miktar_degisimi, "İşlem Türü": h.islem_tipi} for h in hareketler]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Stok_Hareketleri')
    output.seek(0)
    return StreamingResponse(output, headers={"Content-Disposition": f"attachment; filename=stok_hareketleri.xlsx"}, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/yonetim/", response_class=HTMLResponse)
def yonetim_sayfasi(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user.get("can_manage_users") and user.get("rol_adi") != "ADMIN": return RedirectResponse(url="/stok-paneli/")
    return templates.TemplateResponse("yonetim.html", {"request": request, "kategoriler": db.query(models.Kategori).all(), "musteriler": db.query(models.Musteri).all(), "yerler": db.query(models.DepoYeri).all(), "kullanicilar": db.query(models.Kullanici).all(), "roller": db.query(models.Rol).order_by(models.Rol.id).all()})

@app.get("/stok-guncelleme-sablonu")
def stok_guncelleme_sablonu(tip: str = "sablon" , db: Session = Depends(get_db)):
    urunler = db.query(models.UrunModel).all()
    data = [{"ID": u.id, "BARKOD": u.barkod, "ISIM": u.isim, "LOT": u.lot, "MIKTAR": u.miktar, "KATEGORI": u.kategori.ad if u.kategori else "GENEL", "YER": u.yer} for u in urunler]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Stok_Guncelleme')
        worksheet = writer.sheets['Stok_Guncelleme']
        # worksheet.protect()
        worksheet.set_column('A:A', 10, writer.book.add_format({'locked': True, 'bg_color': "#C00101", 'font_color': 'white'}))
        worksheet.set_column('B:D', 20, writer.book.add_format({'locked': False}))
        worksheet.set_column('F:G', 20, writer.book.add_format({'locked': False}))
        worksheet.set_column('E:E', 15, writer.book.add_format({'locked': False, 'num_format': '0'}))
    output.seek(0)
    headers = {'Content-Disposition': f'attachment; filename="stok_listesi.xlsx"'}
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.post("/toplu-guncelle/")
async def toplu_guncelle_api(file: UploadFile = File(...), db: Session = Depends(get_db), request: Request = None):
    yapan = request.state.user.get("kullanici_adi") or request.state.user.get("username") or "SİSTEM"
    yeni_no = yeni_islem_no_al(db)
    
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents), dtype=str).fillna("")
    
    degisen = 0    # Gerçekten değişenler (Hareket kaydı atılanlar)
    degismeyen = 0 # Hiç dokunulmayanlar
    hata = 0       # Hata alanlar
    
    for index, row in df.iterrows():
        try:
            u_id = row.get('ID')
            if not u_id: continue
            
            urun = db.query(models.UrunModel).filter(models.UrunModel.id == int(u_id)).first()
            if urun:
                # 1. Eski değerleri sakla
                eski_barkod = str(urun.barkod).strip()
                eski_isim = str(urun.isim).upper().strip()
                eski_lot = str(urun.lot).strip()
                eski_miktar = urun.miktar
                eski_yer = str(urun.yer).upper().strip()
                eski_kat_id = urun.kategori_id

                # 2. Yeni değerleri al
                yeni_barkod = str(row.get('BARKOD', '')).strip()
                yeni_isim = str(row.get('ISIM', '')).upper().strip()
                yeni_lot = str(row.get('LOT', '')).strip()
                yeni_miktar = int(float(str(row.get('MIKTAR', '0')).replace(',', '.')))
                yeni_yer = str(row.get('YER', '')).upper().strip()
                
                kat_ad = str(row.get('KATEGORI', '')).upper().strip()
                yeni_kat_id = eski_kat_id
                if kat_ad:
                    kategori = db.query(models.Kategori).filter(models.Kategori.ad == kat_ad).first()
                    if kategori: yeni_kat_id = kategori.id

                # 3. Değişim Kontrolü
                degisim_var = (
                    yeni_barkod != eski_barkod or
                    yeni_isim != eski_isim or
                    yeni_lot != eski_lot or
                    yeni_miktar != eski_miktar or
                    yeni_yer != eski_yer or
                    yeni_kat_id != eski_kat_id
                )

                if degisim_var:
                    # Güncelle
                    urun.barkod = yeni_barkod
                    urun.isim = yeni_isim
                    urun.lot = yeni_lot
                    urun.miktar = yeni_miktar
                    urun.yer = yeni_yer
                    urun.kategori_id = yeni_kat_id

                    # Hareket kaydı oluştur
                    miktar_farki = yeni_miktar - eski_miktar
                    hareket_tipi = "GÜNCELLEME"
                    if miktar_farki > 0: hareket_tipi = "GİRİŞ (GÜNCELLEME)"
                    elif miktar_farki < 0: hareket_tipi = "ÇIKIŞ (GÜNCELLEME)"

                    yeni_hareket = models.StokHareketi(
                        urun_barkod=str(urun.barkod),
                        urun_isim=str(urun.isim),
                        urun_lot=str(urun.lot if urun.lot else "-"),
                        miktar_degisimi=int(miktar_farki),
                        islem_tipi=str(hareket_tipi),
                        musteri_ad="EXCEL TOPLU GÜNCELLEME",
                        islem_no=int(yeni_no),
                        islem_yapan=str(yapan),
                        aciklama=f"Miktar {eski_miktar}->{yeni_miktar}"
                    )
                    db.add(yeni_hareket)
                    degisen += 1
                else:
                    degismeyen += 1
            else:
                hata += 1
        except Exception as e:
            print(f"Hata detayı: {e}")
            hata += 1
            
    db.commit() 
    return {"message": f"✅ {degisen} Değişti, ⚪ {degismeyen} Aynı kaldı, ❌ {hata} Hata."}

@app.post("/rol-ekle/")
def rol_ekle_api(ad: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user = request.state.user
    if user.get("rol_adi") != "ADMIN" and not user.get("can_manage_users"): raise HTTPException(status_code=403)
    if not db.query(models.Rol).filter(models.Rol.ad == ad.upper()).first():
        db.add(models.Rol(ad=ad.upper(), can_add_stock=False, can_exit_stock=False, can_edit_product=False, can_delete=False, can_manage_users=False, can_see_logs=False))
        db.commit()
    return RedirectResponse(url="/yonetim/", status_code=303)

@app.post("/rol-yetki-guncelle/{rol_id}")
async def rol_yetki_guncelle(rol_id: int, data: dict, db: Session = Depends(get_db)):
    rol = db.query(models.Rol).filter(models.Rol.id == rol_id).first()
    if rol: setattr(rol, data['alan'], data['deger']); db.commit()
    return {"status": "ok"}

@app.post("/kullanici-rol-ata/{kullanici_id}")
async def kullanici_rol_ata(kullanici_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(models.Kullanici).filter(models.Kullanici.id == kullanici_id).first()
    if user: user.rol_id = int(data['rol_id']); db.commit()
    return {"status": "ok"}







@app.post("/kullanici-sifre-admin-guncelle/{id}")
async def sifre_admin_guncelle(id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(models.Kullanici).filter(models.Kullanici.id == id).first()
    
    if user:
        # 1. E-posta verisini temizleyip saf küçük harfe çeviriyoruz (Veritabanındaki gibi kalması için)
        if 'email' in data and data['email']:
            user.mail_adresi = data['email'].strip().lower()
            
        # 2. Kullanıcı adını temizleyip HER ZERDE BÜYÜK HARF yapıyoruz
        if 'kullanici_adi' in data and data['kullanici_adi']:
            user.kullanici_adi = data['kullanici_adi'].strip().upper()
            
        # 3. Şifre alanı doldurulduysa güncelliyoruz, boş bırakıldıysa eski şifre korunuyor
        if 'sifre' in data and data['sifre'] and data['sifre'].strip():
            user.sifre = data['sifre'].strip()
            
        db.commit()
        
    return {"status": "ok"}

@app.post("/urunler/")
def urun_ekle_api(u: schemas.UrunSema, db: Session = Depends(get_db), request: Request = None):
    user = request.state.user
    if not user.get("can_add_stock"): raise HTTPException(status_code=403)
    
    kullanici_adi = user.get("kullanici_adi","SİSTEM")
    yeni_no = yeni_islem_no_al(db)
    
    # Barkod/Lot kontrolü ve ürün güncelleme kısmı aynı...
    mevcut = db.query(models.UrunModel).filter(models.UrunModel.barkod == u.barkod, models.UrunModel.lot == u.lot).first()
    if mevcut:
        mevcut.miktar += u.miktar
        if u.yer: mevcut.yer = u.yer.upper()
    else:
        kat = db.query(models.Kategori).filter(models.Kategori.ad == u.kategori_ad.upper()).first()
        if not kat: 
            kat = models.Kategori(ad=u.kategori_ad.upper()); db.add(kat); db.commit(); db.refresh(kat)

        db.add(models.UrunModel(
            barkod=u.barkod,
            isim=u.isim.upper(),
            lot=u.lot.upper() if u.lot else "-",
            miktar=u.miktar,
            kategori_id=kat.id,
            yer=u.yer.upper() if u.yer else "BELİRTİLMEDİ",
            
        ))

    
    # BURASI ÇOK ÖNEMLİ:
    # Notu ve yapan kişiyi birleştiriyoruz (u.not_alani schemas'ından geliyor)
    
    
    db.add(models.StokHareketi(

        urun_barkod=u.barkod,
        urun_isim=u.isim.upper(),
        urun_lot=u.lot.upper() if u.lot else "-",
        miktar_degisimi=u.miktar,
        islem_tipi="GİRİŞ",
        islem_nedeni=u.islem_nedeni,
        islem_no=yeni_no,
        islem_yapan=kullanici_adi,
        aciklama=u.not_alani
    ))    

    db.commit()
    return {"status": "ok"}

@app.post("/stok-cikisi-toplu")
def stok_cikisi_toplu_api(v: schemas.TopluCikisSema, db: Session = Depends(get_db), request: Request = None):
    user = request.state.user
    if not user.get("can_exit_stock"): raise HTTPException(status_code=403)
    kullanici_adi = user.get("kullanici_adi","SİSTEM") # JWT'den gelen isim
    yeni_no = yeni_islem_no_al(db)
    # Müşteri verisi boş gelirse "BELİRTİLMEDİ" yaz
    musteri_adi = v.musteri if v.musteri and v.musteri.strip() != "" else "BELİRTİLMEDİ"
    
    for item in v.urunler:
        u = db.query(models.UrunModel).filter(
            models.UrunModel.barkod == item.barkod, 
            models.UrunModel.lot == (item.lot if item.lot else None)
        ).first()
        
        if not u or u.miktar < item.miktar:
            raise HTTPException(status_code=400, detail=f"{item.barkod} için stok yetersiz!")
            
        u.miktar -= item.miktar
        
        db.add(models.StokHareketi(
            urun_barkod=u.barkod, 
            urun_isim=u.isim, 
            urun_lot=item.lot if item.lot else "-", 
            miktar_degisimi=-item.miktar, 
            islem_tipi="ÇIKIŞ",
            musteri_ad=musteri_adi, # YENİ SÜTUNUNA EKLENDİ
            islem_no=yeni_no,
            islem_yapan = kullanici_adi,
            aciklama=v.aciklama
        ))
    db.commit()
    return {"status": "ok", "islem_no": yeni_no}

def yeni_islem_no_al(db: Session):
    # En son kayıtlı islem_no'yu bul, yoksa 1'den başlat
    son = db.query(models.StokHareketi.islem_no).order_by(models.StokHareketi.id.desc()).first()
    return (son[0] + 1) if son and son[0] else 1



@app.post("/kategori-ekle/")
def kategori_ekle(ad: str = Form(...), db: Session = Depends(get_db)):
    f_ad = ad.upper().strip()
    if not db.query(models.Kategori).filter(models.Kategori.ad == f_ad).first():
        db.add(models.Kategori(ad=f_ad)); db.commit()
    return RedirectResponse(url="/yonetim/", status_code=303)

@app.delete("/kategori-sil/{kat_id}")
async def kategori_sil_api(kat_id: int, request: Request, db: Session = Depends(get_db)):
    if request.state.user["rol_adi"] != "ADMIN": raise HTTPException(status_code=403)
    db.query(models.UrunModel).filter(models.UrunModel.kategori_id == kat_id).update({"kategori_id": None})
    kat = db.query(models.Kategori).filter(models.Kategori.id == kat_id).first()
    if kat: db.delete(kat); db.commit(); return {"status": "ok"}
    raise HTTPException(status_code=404)

@app.delete("/musteri-sil/{m_id}")
async def musteri_sil_api(m_id: int, request: Request, db: Session = Depends(get_db)):
    if request.state.user["rol_adi"] != "ADMIN": raise HTTPException(status_code=403)
    db.query(models.Musteri).filter(models.Musteri.id == m_id).delete(); db.commit()
    return {"status": "ok"}

@app.delete("/yer-sil/{yer_id}")
async def yer_sil_api(yer_id: int, request: Request, db: Session = Depends(get_db)):
    if request.state.user["rol_adi"] != "ADMIN": raise HTTPException(status_code=403)
    yer_obj = db.query(models.DepoYeri).filter(models.DepoYeri.id == yer_id).first()
    if yer_obj:
        db.query(models.UrunModel).filter(models.UrunModel.yer == yer_obj.ad).update({"yer": "BELİRTİLMEYİ"})
        db.delete(yer_obj); db.commit(); return {"status": "ok"}
    raise HTTPException(status_code=404)

@app.delete("/kullanici-sil/{id}")
def kullanici_sil_api(id: int, db: Session = Depends(get_db)):
    k = db.query(models.Kullanici).filter(models.Kullanici.id == id).first()
    if k: db.delete(k); db.commit(); return {"status": "ok"}
    raise HTTPException(status_code=404)

@app.delete("/urunler/{barkod}")
def urun_sil_api(barkod: str, request: Request, db: Session = Depends(get_db)):
    if not request.state.user.get("can_delete"): raise HTTPException(status_code=403)
    db.query(models.StokHareketi).filter(models.StokHareketi.urun_barkod == barkod).delete()
    u = db.query(models.UrunModel).filter(models.UrunModel.barkod == barkod).first()
    if u: db.delete(u); db.commit(); return {"status": "ok"}
    raise HTTPException(status_code=404)

@app.post("/kullanici-ekle/")
def kullanici_ekle_api(k: dict, db: Session = Depends(get_db)):
    k_mail = k.get("email", "").strip()
    k_adi = k.get("kullanici_adi", "").strip().upper()
    if db.query(models.Kullanici).filter(models.Kullanici.kullanici_adi == k_adi).first(): raise HTTPException(status_code=400)
    if db.query(models.Kullanici).filter(models.Kullanici.email == k_mail).first(): raise HTTPException(status_code=400)
    db.add(models.Kullanici(email = k_mail,kullanici_adi=k_adi, sifre=k.get("sifre"), rol_id=None)); db.commit(); return {"status": "ok"}

@app.post("/urun-guncelle/{barkod}")
async def urun_guncelle_api(barkod: str, v: schemas.UrunSema, request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user.get("can_edit_product") and user.get("rol_adi") != "ADMIN": 
        raise HTTPException(status_code=403)
    

    # 1. Eski lotu query parametresinden al (JS'ten gönderiyoruz)
    eski_lot = request.query_params.get("eski_lot")
    
    # 2. Ürünü eski lot ve barkod ile bul
    u = db.query(models.UrunModel).filter(
        models.UrunModel.barkod == barkod,
        models.UrunModel.lot == eski_lot
    ).first()
    
    if not u:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # 3. Bilgileri güncelle
    u.isim = v.isim.upper().strip()
    u.lot = v.lot.strip() if v.lot else None

    u.yer = v.yer.upper() if v.yer else "-"
    
    if v.kategori_ad:
        kat = db.query(models.Kategori).filter(models.Kategori.ad == v.kategori_ad.upper()).first()
        if kat: u.kategori_id = kat.id
        

    # 4. Stok Hareketini kaydet

    db.add(models.StokHareketi(
        urun_barkod=barkod, 
        urun_isim=u.isim, 
        urun_lot=v.lot, 
        miktar_degisimi=0, 

        islem_tipi=f"BİLGİ GÜNCELLEME | {v.islem_nedeni} | YAPAN: {user['kullanici_adi']}"

    ))
    
    db.commit()
    return {"status": "ok"}

@app.post("/musteri-ekle/")
async def musteri_ekle_api(ad: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.Musteri).filter(models.Musteri.ad == ad.upper()).first(): raise HTTPException(status_code=400)
    db.add(models.Musteri(ad=ad.upper())); db.commit(); return {"status": "ok"}

@app.post("/yer-ekle/")
async def yer_ekle_api(ad: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.DepoYeri).filter(models.DepoYeri.ad == ad.upper()).first(): raise HTTPException(status_code=400)
    db.add(models.DepoYeri(ad=ad.upper())); db.commit(); return {"status": "ok"}

@app.post("/sistemi-sifirla")
async def sistemi_sifirla_api(request: Request, db: Session = Depends(get_db)):
    if request.state.user["rol_adi"] != "ADMIN": raise HTTPException(status_code=403)
    db.query(models.StokHareketi).delete(); db.query(models.UrunModel).delete(); db.query(models.İslem_nedeni).delete(); db.query(models.Sayim).delete(); db.query(models.Kategori).delete(); db.query(models.Musteri).delete(); db.query(models.DepoYeri).delete()
    db.commit(); return {"status": "ok"}

@app.get("/barkod-detay/{barkod}")
async def barkod_detay_getir(barkod: str, db: Session = Depends(get_db)):
    urunler = db.query(models.UrunModel).filter(models.UrunModel.barkod == barkod).all()
    if not urunler: return {"hata": "Ürün yok", "liste": []}
    return {"isim": urunler[0].isim, "liste": [{"lot": u.lot, "miktar": u.miktar, "yer": u.yer, "isim": u.isim} for u in urunler]}




@app.get("/urun-detay/{barkod}/{lot:path}", response_class=HTMLResponse)
async def urun_detay(request: Request, barkod: str, lot: str, db: Session = Depends(get_db)):

    lot = unquote(lot)

    urun = db.query(models.UrunModel).filter(
        models.UrunModel.barkod == barkod,
        models.UrunModel.lot == lot
    ).first()

    if not urun:
        return RedirectResponse(url="/urun-listesi/?hata=urun_bulunamadi")

    hareketler = db.query(models.StokHareketi).filter(
        models.StokHareketi.urun_barkod == barkod,
        models.StokHareketi.urun_lot == lot
    ).order_by(models.StokHareketi.tarih.desc()).all()


    kategoriler = db.query(models.Kategori).all()
    yerler = db.query(models.DepoYeri).all()

    return templates.TemplateResponse(
        "urun_detay.html",
        {
            "request": request,
            "urun": urun,
            "hareketler": hareketler,
            "kategoriler": kategoriler,
            "yerler": yerler
        }
    )




@app.get("/api/hizli-sayim-barkod/{barkod}")
async def hizli_sayim_barkod_detay(barkod: str, db: Session = Depends(get_db)):
    urun = db.query(models.UrunModel).filter(models.UrunModel.barkod == barkod).first()
    stok_lotlar = db.query(models.UrunModel).filter(models.UrunModel.barkod == barkod).all()
    sayim_lotlar = db.query(models.Sayim).filter(models.Sayim.barkod == barkod).all()
    birlesik = {s.lot: {"lot": s.lot, "miktar": s.miktar, "kaynak": "STOK", "tarih": "Depo"} for s in stok_lotlar if s.lot}
    for g in sayim_lotlar: birlesik[g.lot_no] = {"lot": g.lot_no, "miktar": g.miktar, "kaynak": "SAYIM", "tarih": g.kayit_tarihi.strftime("%H:%M")}
    if not urun and not sayim_lotlar: return {"isim": "YENİ ÜRÜN", "liste": [], "yeni_urun": True}
    return {"isim": urun.isim if urun else "Bilinmeyen Ürün", "liste": list(birlesik.values()), "yeni_urun": not urun, "mevcut_yer": urun.yer if urun else "Tanımsız"}

@app.get("/excel-sablonu-indir")
def excel_sablonu_indir():
    df = pd.DataFrame(columns=['BARKOD', 'ISIM', 'LOT', 'MIKTAR', 'KATEGORI', 'YER'])
    df.loc[0] = ["'8690000000", "ÖRNEK ÜRÜN", "'002", "100", "GENEL", "A-1"]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False); worksheet = writer.sheets['Sheet1']
        worksheet.set_column('A:F', 13, writer.book.add_format({'num_format': '@'}))
    output.seek(0)
    return StreamingResponse(output, headers={'Content-Disposition': 'attachment; filename="sablon.xlsx"'}, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.post("/toplu-urun-yukle/")
async def toplu_urun_yukle(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    # Kullanıcı adını al
    yapan = request.state.user.get("kullanici_adi", "SİSTEM")

    df = pd.read_excel(
        io.BytesIO(await file.read()),
        dtype=str
    ).fillna("")

    df.columns = df.columns.str.strip().str.upper()

    yeni = 0
    guncel = 0
    hata = 0

    # Toplu işlem için tek bir işlem numarası al
    yeni_no = yeni_islem_no_al(db)

    for idx, row in df.iterrows():
        try:
            b = str(row["BARKOD"]).strip()
            isim = str(row["ISIM"]).upper().strip()
            lot = str(row["LOT"]).strip()
            miktar = int(float(row["MIKTAR"]))

            if not b or not isim:
                continue

            kategori_id = None
            kat_ad = str(row.get("KATEGORI", "")).upper().strip()

            if kat_ad:
                mevcut_kat = db.query(models.Kategori).filter(models.Kategori.ad == kat_ad).first()
                if mevcut_kat:
                    kategori_id = mevcut_kat.id
                else:
                    yeni_kat = models.Kategori(ad=kat_ad)
                    db.add(yeni_kat)
                    db.flush()
                    kategori_id = yeni_kat.id

            mevcut = db.query(models.UrunModel).filter(
                models.UrunModel.barkod == b,
                models.UrunModel.lot == lot
            ).first()

            if mevcut:
                mevcut.miktar += miktar
                if kategori_id is not None:
                    mevcut.kategori_id = kategori_id
                guncel += 1
            else:
                yeni_urun = models.UrunModel(
                    barkod=b,
                    isim=isim,
                    lot=lot,
                    miktar=miktar,
                    yer=str(row.get("YER", "")).upper().strip(),
                    kategori_id=kategori_id
                )
                db.add(yeni_urun)
                yeni += 1

            # --- DÜZENLİ STOK HAREKETİ KAYDI ---
            # Tek bir db.add ile tüm bilgileri doğru kaydediyoruz
            db.add(models.StokHareketi(
                urun_barkod=b,
                urun_isim=isim,
                urun_lot=lot if lot else "-",
                miktar_degisimi=miktar,
                islem_tipi="GİRİŞ",
                musteri_ad="EXCEL TOPLU YÜKLEME", # İsteğin üzerine "Müşteri" alanına bu yazılacak
                islem_no=yeni_no,
                islem_yapan=yapan,
                aciklama=""
            ))

        except Exception as e:
            print(f"HATA SATIR {idx+1}: {e}")
            hata += 1

    db.commit()

    return {
        "message": f"✅ {yeni} Yeni, 🔄 {guncel} Güncel, ❌ {hata} Hata."
    }


@app.delete("/rol-sil/{rol_id}")
def rol_sil(rol_id: int, request: Request, db: Session = Depends(get_db)):
    if request.state.user["rol_adi"] != "ADMIN": raise HTTPException(status_code=403)
    rol = db.query(models.Rol).filter(models.Rol.id == rol_id).first()
    if rol and rol.ad != "ADMIN":
        db.query(models.Kullanici).filter(models.Kullanici.rol_id == rol_id).update({"rol_id": None})
        db.delete(rol); db.commit(); return {"status": "ok"}
    return {"hata": "Silinemez."}



# Geçici kodları sunucu hafızasında tutmak için basit bir sözlük
gecici_kodlar = {}

# SMTP Mail Ayarlarınız (Buraları kendi mail bilgilerinize göre doldurmalısınız)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "akcanmetehanis@gmail.com"  # Gönderici mail adresi
SMTP_PASSWORD = "cacw sqes ajzm cwsp"          # Gmail kullanıyorsanız "Uygulama Şifresi"

def mail_gonder(alici_mail: str, kod: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = alici_mail
        msg['Subject'] = "🔒 Depo Pro v3 - Şifre Sıfırlama Talebi"
        
        # PROJEYE UYGUN CANLI VE MODERN HTML E-POSTA ŞABLONU
        html_icerik = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Şifre Sıfırlama</title>
            <style>
                body {{ margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .email-container {{ max-width: 500px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }}
                .content {{ padding: 40px 30px; text-align: center; color: #1e293b; }}
                .content p {{ font-size: 15px; line-height: 1.6; color: #64748b; margin-bottom: 30px; }}
                .code-box {{ background-color: #f8fafc; border: 2px dashed #6366f1; border-radius: 12px; padding: 16px; font-size: 32px; font-weight: 800; color: #4f46e5; letter-spacing: 8px; display: inline-block; margin-bottom: 30px; padding-left: 24px; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
                .warning {{ font-size: 12px; color: #94a3b8; margin-top: 20px; padding-top: 20px; border-top: 1px dashed #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Depo Pro v3</h1>
                </div>
                <div class="content">
                    <h2 style="margin-bottom: 15px; font-weight: 700;">Şifre Sıfırlama Talebi</h2>
                    <p>Hesabınız için şifre sıfırlama talebinde bulundunuz. Aşağıdaki 6 haneli doğrulama kodunu kullanarak yeni güçlü şifrenizi belirleyebilirsiniz.</p>
                    
                    <div class="code-box">{kod}</div>
                    
                    <p class="warning">Eğer bu talebi siz yapmadıysanız, bu e-postayı güvenle göz ardı edebilirsiniz. Hesabınız güvendedir.</p>
                </div>
                <div class="footer">
                    © 2026 Depo Pro v3. Tüm Hakları Saklıdır.<br>
                    Bu otomatik bir sistem e-postasıdır, lütfen yanıtlamayınız.
                </div>
            </div>
        </body>
        </html>
        """
        
        # İçeriği düz yazı (plain) yerine 'html' formatında bağlıyoruz
        msg.attach(MIMEText(html_icerik, 'html', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, alici_mail, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Mail gonderme hatasi:", e)
        return False

# --- ŞİFRE YENİLEME SİSTEMİ (EN ALT KISIM - KESİN SÜRÜM) ---

# 1. Şifre Yenileme Sayfası Ana Giriş Yeri (GET)
@app.get("/sifre-yenileme", response_class=HTMLResponse)
def sifre_yenileme_sayfasi(request: Request, email: str = None, kod_gonderildi: bool = False, hata: str = None, mesaj: str = None):
    return templates.TemplateResponse("sifre_yenileme.html", {
        "request": request, 
        "kod_gonderildi": kod_gonderildi,
        "email": email,
        "hata": hata,
        "mesaj": mesaj
    })

# 2. E-posta adresine 6 haneli kod üretip gönderme (POST)
@app.post("/sifre-yenileme/kod-gonder")
def kod_gonder_islem(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    e_posta = email.strip().lower()
    
    # EĞER E-POSTA YOKSA BURASI ÇALIŞIR VE SAĞ ÜSTTE KIRMIZI BİLDİRİM TETİKLENİR
    user = db.query(models.Kullanici).filter(models.Kullanici.email == e_posta).first()
    if not user:
        return RedirectResponse(url="/sifre-yenileme?hata=Bu e-posta adresine ait kullanici bulunamadi!", status_code=303)
    
    # Kullanıcı varsa 6 haneli kod üret ve hafızaya al
    kod = str(random.randint(100000, 999999))
    gecici_kodlar[e_posta] = kod
    
    # Mail gönderme motorunu tetikle
    if mail_gonder(e_posta, kod):
        return RedirectResponse(url=f"/sifre-yenileme?kod_gonderildi=True&email={e_posta}&mesaj=6 haneli dogrulama kodu basariyla mail adresinize gonderildi.", status_code=303)
    else:
        return RedirectResponse(url="/sifre-yenileme?hata=Mail gonderilirken sunucu hatasi olustu. SMTP ayarlarinizi kontrol edin!", status_code=303)

# 3. Kodu ve Yeni Şifreyi Onaylayıp Girişe Gönderme (POST)
@app.post("/sifre-yenileme/onayla")
def sifre_onayla_islem(
    request: Request, 
    email: str = Form(...), 
    kod: str = Form(...), 
    yeni_sifre: str = Form(...), 
    db: Session = Depends(get_db)
):
    e_posta = email.strip().lower()
    gelen_kod = kod.strip()
    
    # Kod yanlışsa hata fırlat
    if e_posta not in gecici_kodlar or gecici_kodlar[e_posta] != gelen_kod:
        return RedirectResponse(url=f"/sifre-yenileme?kod_gonderildi=True&email={e_posta}&hata=Girdiniz 6 haneli kod yanlis veya suresi dolmus!", status_code=303)
    
    user = db.query(models.Kullanici).filter(models.Kullanici.email == e_posta).first()
    if user:
        user.sifre = yeni_sifre
        db.commit()
        gecici_kodlar.pop(e_posta, None)
        
        # Her şey başarılı! Giriş ekranına gönder
        return RedirectResponse(url="/login", status_code=303)
        
    return RedirectResponse(url="/sifre-yenileme?hata=Sistem hatasi olustu!", status_code=303)



# --- ADMIN RAPORLAR PANELİ ROTASI (KESİN SÜRÜM) ---
@app.get("/raporlar", response_class=HTMLResponse)
def raporlar_sayfasi(request: Request, db: Session = Depends(get_db)):
    # 1. Adım: Kullanıcı bilgisini tam olarak sizin sisteminizdeki gibi request.state üzerinden çekiyoruz
    user = getattr(request.state, "user", None)
    
    # Eğer kullanıcı oturum açmamışsa doğrudan giriş ekranına fırlat
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    # 2. Adım: Rol yetki kontrolü (Sadece ADMIN görebilir)
    # Sizin yapınızda user bir sözlük (dict) olduğu için ['rol_adi'] kuralını güvenle işletiyoruz
    rol = user.get("rol_adi") if isinstance(user, dict) else getattr(user, "rol_adi", None)
    
    if not rol or str(rol).upper() != "ADMIN":
        # Yetkisiz personeli paneli görmemesi için ana stok paneline geri fırlatıyoruz
        return RedirectResponse(url="/stok-paneli/", status_code=303)
        
    # 3. Adım: Her şey yolundaysa hazırladığımız şık raporlar.html şablonunu render et
    return templates.TemplateResponse("raporlar.html", {"request": request})




@app.get("/api/raporlar-verisi")
def raporlar_verisi_api(
    request: Request,
    db: Session = Depends(get_db),
    giris_goster: bool = True,
    cikis_goster: bool = True,
    arama_kelimesi: str = "",
    secili_kategori: str = "hepsi",
    secili_urun_barkod: str = "hepsi",
    secili_depo_yeri: str = "hepsi",
    olu_stok_gun: int = 60,
    tarih_araligi: str = "hepsi"
):
    # 1. Yetki Kontrolü (Orijinal state.user kontrol mimariniz)
    user = getattr(request.state, "user", None)
    if not user or str(user.get("rol_adi", "")).upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Bu operasyonel rapora sadece Admin erişebilir.")
        
    try:
        # Zaman Sınırları Hesaplama
        su_an = datetime.now()
        olu_stok_esigi = su_an - timedelta(days=olu_stok_gun)
        son_30_gun_esigi = su_an - timedelta(days=30)
        
        # 2. TABAN ORM SORGUSU: İlişkisel Tabloları JOIN ile Bağlama
        sorgu = db.query(models.StokHareketi).join(
            models.UrunModel, models.StokHareketi.urun_barkod == models.UrunModel.barkod
        ).join(
            models.Kategori, models.UrunModel.kategori_id == models.Kategori.id
        )
        
        # --- Dinamik Filtre Yönetim Katmanı ---
        if giris_goster and not cikis_goster:
            sorgu = sorgu.filter(models.StokHareketi.islem_tipi.ilike("%GİRİŞ%") | models.StokHareketi.islem_tipi.ilike("%GIRIS%") | models.StokHareketi.islem_tipi.ilike("%KAYIT%"))
        elif cikis_goster and not giris_goster:
            sorgu = sorgu.filter(models.StokHareketi.islem_tipi.ilike("%ÇIKIŞ%") | models.StokHareketi.islem_tipi.ilike("%CIKIS%"))
        elif not giris_goster and not cikis_goster:
            sorgu = sorgu.filter(models.StokHareketi.id == -1)

        if secili_kategori != "hepsi":
            sorgu = sorgu.filter(models.Kategori.ad == secili_kategori)
            
        if secili_urun_barkod != "hepsi":
            sorgu = sorgu.filter(models.StokHareketi.urun_barkod == secili_urun_barkod)
            
        if secili_depo_yeri != "hepsi":
            sorgu = sorgu.filter(models.UrunModel.yer == secili_depo_yeri)

        if arama_kelimesi and arama_kelimesi.strip() != "":
            kelime = f"%{arama_kelimesi.strip()}%"
            sorgu = sorgu.filter(models.StokHareketi.urun_isim.ilike(kelime) | models.StokHareketi.urun_barkod.ilike(kelime))

        if tarih_araligi == "bugun":
            sorgu = sorgu.filter(func.date(models.StokHareketi.tarih) == func.current_date())

        # Verileri Hafızaya Çekme (Performans İndeksli)
        hareketler = sorgu.order_by(models.StokHareketi.id.desc()).all()

        # 3. Operasyonel ve Metrik Hesaplamalar
        toplam_giris = 0
        toplam_cikis = 0
        toplam_iade = 0
        kategori_hacimler = {}
        islem_nedenleri = {"SATIŞ/SEVK HAREKETİ": 0, "MÜŞTERİ İADESİ": 0, "FİRE / ZAYİAT": 0, "DİĞER TRANSFERLER": 0}
        
        for h in hareketler:
            m_degisim = abs(h.miktar_degisimi) if h.miktar_degisimi else 0
            islem_metni = str(h.islem_tipi).upper()
            
            # Giriş / Çıkış Ayrımı (Veritabanı döküm adlarına tam uyumlu)
            is_giris = any(k in islem_metni for k in ["GİRİŞ", "GIRIS", "KAYIT"])
            if is_giris:
                toplam_giris += m_degisim
                if "İADE" in islem_metni or "IADE" in islem_metni:
                    toplam_iade += m_degisim
                    islem_nedenleri["MÜŞTERİ İADESİ"] += m_degisim
                else:
                    islem_nedenleri["DİĞER GİRİŞLER" if "DİĞER GİRİŞLER" in islem_nedenleri else "DİĞER TRANSFERLER"] += m_degisim
            else:
                toplam_cikis += m_degisim
                if "FİRE" in islem_metni or "FIRE" in islem_metni or "ZAYİAT" in islem_metni or "SAYIM" in islem_metni:
                    islem_nedenleri["FİRE / ZAYİAT"] += m_degisim
                else:
                    islem_nedenleri["SATIŞ/SEVK HAREKETİ"] += m_degisim
            
            # Kategori Lojistik Dağılım Map'leme
            kat_bul = db.query(models.Kategori.ad).join(models.UrunModel).filter(models.UrunModel.barkod == h.urun_barkod).scalar() or "GENEL"
            kat_bul = kat_bul.upper()
            if kat_bul not in kategori_hacimler:
                kategori_hacimler[kat_bul] = {"giris": 0, "cikis": 0, "iade": 0}
            
            if is_giris:
                if "İADE" in islem_metni or "IADE" in islem_metni:
                    kategori_hacimler[kat_bul]["iade"] += m_degisim
                else:
                    kategori_hacimler[kat_bul]["giris"] += m_degisim
            else:
                kategori_hacimler[kat_bul]["cikis"] += m_degisim

        # 4. ÜRÜN SİRKÜLASYON HIZI VE ÖLÜ STOK DETAY ANALİZİ (Scatter Plot Verisi)
        urunler_havuzu = db.query(models.UrunModel).all()
        scatter_verisi = []
        olu_stok_adedi = 0
        kritik_stok_sayisi = 0
        
        for u in urunler_havuzu:
            # Kritik stok kontrolü (Örn: miktar < 10 ise)
            if u.miktar < 10:
                kritik_stok_sayisi += 1
                
            # Son işlem tarihini çekme
            son_hareket_tarihi = db.query(models.StokHareketi.tarih).filter(
                models.StokHareketi.urun_barkod == u.barkod
            ).order_by(models.StokHareketi.id.desc()).first()
            
            hareketsiz_gun = (su_an - son_hareket_tarihi[0]).days if son_hareket_tarihi else 99
            if hareketsiz_gun >= olu_stok_gun:
                olu_stok_adedi += u.miktar
                
            # Son 30 günlük çıkış adedi
            son_30_gun_cikis = db.query(func.sum(models.StokHareketi.miktar_degisimi)).filter(
                models.StokHareketi.urun_barkod == u.barkod,
                models.StokHareketi.tarih >= son_30_gun_esigi,
                models.StokHareketi.islem_tipi.ilike("%ÇIKIŞ%") | models.StokHareketi.islem_tipi.ilike("%CIKIS%")
            ).scalar() or 0
            
            scatter_verisi.append({
                "x": hareketsiz_gun,
                "y": abs(son_30_gun_cikis),
                "label": u.isim.upper()
            })

        # Donut Grafik İçin Fiziksel Hacimsel Doluluk Dağılımı (Miktar * 0.05 m³ varsayımıyla)
        hacim_sorgu = db.query(models.Kategori.ad, func.sum(models.UrunModel.miktar)).join(
            models.UrunModel, models.Kategori.id == models.UrunModel.kategori_id
        ).group_by(models.Kategori.ad).all()
        
        pie_labels = [r[0].upper() for r in hacim_sorgu if r[0]]
        pie_values = [round(int(r[1]) * 0.04, 2) for r in hacim_sorgu if r[1]] # m³ dönüştürme rasyosu

        # Filtreleri ve SelectBox Elemanlarını Dolduracak Dinamik Listeler
        kategori_isimleri = [k[0].upper() for k in db.query(models.Kategori.ad).distinct().all() if k[0]]
        urun_kartela = [{"barkod": ur.barkod, "isim": ur.isim.upper()} for ur in db.query(models.UrunModel.barkod, models.UrunModel.isim).all()]
        depo_raflar = [r[0].upper() for r in db.query(models.UrunModel.yer).distinct().all() if r[0]]

        toplam_stok_adeti = db.query(func.sum(models.UrunModel.miktar)).scalar() or 0
        toplam_cesit = db.query(func.count(models.UrunModel.id)).scalar() or 0
        iade_orani_yuzde = round((toplam_iade / toplam_cikis * 100), 1) if toplam_cikis > 0 else 0

    except Exception as e:
        print("Lojistik BI Sorgu Hatası:", e)
        return {"error": str(e)}

    # UI Tablosuna Gönderilecek Liste (Filtreye Duyarlı Son 10 İşlem)
    detay_listesi = []
    for h in hareketler[:10]:
        t_tarih = h.tarih.strftime("%d.%m.%Y %H:%M") if h.tarih else "04.06.2026 15:00"
        islem_tipi_raw = str(h.islem_tipi).upper()
        
        # Son hareket tarihine göre ürün hareketsiz gün hesabı
        u_son_hrk = db.query(models.StokHareketi.tarih).filter(models.StokHareketi.urun_barkod == h.urun_barkod).order_by(models.StokHareketi.id.desc()).first()
        h_gun = (su_an - u_son_hrk[0]).days if u_son_hrk else 0
        
        detay_listesi.append({
            "tarih": t_tarih,
            "tip": str(h.islem_tipi).upper(),
            "evrak": f"HRK-{h.id}",
            "cari": h.urun_isim,
            "miktar": f"{abs(h.miktar_degisimi)} ADET",
            "hareketsiz_gun": h_gun
        })

    return {
        "kpi": {
            "total_volume": f"{toplam_stok_adeti:,} Tane".replace(",", "."),
            "in_hacim": f"{toplam_giris:,} Adet".replace(",", "."),
            "out_hacim": f"{toplam_cikis:,} Adet".replace(",", "."),
            "customers": f"{toplam_cesit} Çeşit",
            "kritik_sayi": kritik_stok_sayisi,
            "olu_stok_total": f"{olu_stok_adedi} Adet ({round((olu_stok_adedi/toplam_stok_adeti*100),1) if toplam_stok_adeti > 0 else 0}%)",
            "iade_orani": f"% {iade_orani_yuzde}"
        },
        "charts": {
            "multi_bar_labels": list(kategori_hacimler.keys()),
            "multi_bar_giris": [v["giris"] for v in kategori_hacimler.values()],
            "multi_bar_cikis": [v["cikis"] for v in kategori_hacimler.values()],
            "multi_bar_iade": [v["iade"] for v in kategori_hacimler.values()],
            "pie_labels": pie_labels,
            "pie_values": pie_values,
            "scatter_data": scatter_verisi,
            "reason_labels": list(islem_nedenleri.keys()),
            "reason_values": list(islem_nedenleri.values())
        },
        "kategoriler": kategori_isimleri,
        "urunler": urun_kartela,
        "raflar": depo_raflar,
        "table": detay_listesi
    }