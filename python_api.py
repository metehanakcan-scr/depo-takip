from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

# --- 1. VERİTABANI VE BAĞLANTI AYARLARI ---
URL = "postgresql://postgres:123456@localhost:5432/depo_db"
engine = create_engine(URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --- 2. VERİTABANI MODELLERİ (TABLOLAR) ---
class Kategori(Base):
    __tablename__ = "kategoriler"
    id = Column(Integer, primary_key=True)
    ad = Column(String, unique=True, nullable=False)
    # Kategori silinince bağlı ürünler de gitsin (Senin istediğin Cascade yapısı)
    urunler = relationship("UrunModel", back_populates="kategori", cascade="all, delete-orphan")

class UrunModel(Base):
    __tablename__ ="urunler"
    id = Column(Integer, primary_key=True)
    barkod = Column(String, unique=True, nullable=False)
    isim = Column(String, nullable=False)
    miktar = Column(Integer, default=0)
    kategori_id = Column(Integer, ForeignKey("kategoriler.id"))
    kategori = relationship("Kategori", back_populates="urunler")

# Veritabanında tabloları oluştur
Base.metadata.create_all(bind=engine)

# --- 3. VERİ KALIPLARI (PYDANTIC ŞEMALARI) ---
class UrunSema(BaseModel):
    barkod: str
    isim: str
    miktar: int = Field(gt=0, description="Miktar 0'dan büyük olmalı")
    kategori_ad: str

    class Config:
        from_attributes = True

# --- 4. FASTAPI KURULUMU VE YARDIMCI METODLAR ---
app = FastAPI(title="Depo Yönetim Sistemi")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. HATA YÖNETİMİ (ESTETİK DOKUNUŞLAR) ---

@app.exception_handler(RequestValidationError)
async def hatalı_veri_uyarısı(request: Request, exc: RequestValidationError):
    hatalar = [{"alan": h["loc"][-1], "mesaj": h["msg"]} for h in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"durum": "Geçersiz Veri", "detaylar": hatalar}
    )

@app.exception_handler(404)
async def olu_link_yonlendirme(request: Request, exc: Exception):
    return HTMLResponse(
        status_code=404,
        content=f"""
        <body style="font-family:sans-serif; text-align:center; padding:50px; background:#f4f7f6;">
            <div style="background:white; display:inline-block; padding:40px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
                <h1 style="color:#e74c3c;">404 - Sayfa Bulunamadı</h1>
                <p><strong>{request.url.path}</strong> adresi depomuzda yok.</p>
                <a href="/stok-paneli/" style="color:#3498db;">Panele Dönmek İçin Tıkla</a>
            </div>
        </body>
        """
    )

# --- 6. API METODLARI (ÜRÜN VE KATEGORİ İŞLEMLERİ) ---

@app.post("/urunler/")
def urun_ekle_veya_guncelle(urun_verisi: UrunSema, db: Session = Depends(get_db)):
    try:
        # 1. Kategori Kontrolü
        mevcut_kategori = db.query(Kategori).filter(Kategori.ad == urun_verisi.kategori_ad).first()
        if not mevcut_kategori:
            mevcut_kategori = Kategori(ad=urun_verisi.kategori_ad)
            db.add(mevcut_kategori)
            db.commit()
            db.refresh(mevcut_kategori)

        # 2. Ürün Kontrolü (Barkod Üzerinden)
        mevcut_urun = db.query(UrunModel).filter(UrunModel.barkod == urun_verisi.barkod).first()

        if mevcut_urun:
            mevcut_urun.miktar += urun_verisi.miktar
            db.commit()
            return {"mesaj": "Stok güncellendi", "urun": mevcut_urun.isim, "yeni_miktar": mevcut_urun.miktar}
        else:
            yeni_urun = UrunModel(
                barkod=urun_verisi.barkod,
                isim=urun_verisi.isim,
                miktar=urun_verisi.miktar,
                kategori=mevcut_kategori
            )
            db.add(yeni_urun)
            db.commit()
            return {"mesaj": "Yeni ürün başarıyla eklendi", "urun": yeni_urun.isim}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sistem Hatası: {str(e)}")

@app.delete("/urunler/{barkod}")
def urun_sil(barkod: str, db: Session = Depends(get_db)):
    silinecek_urun = db.query(UrunModel).filter(UrunModel.barkod == barkod).first()
    if not silinecek_urun:
        raise HTTPException(status_code=404, detail="Böyle bir barkod bulunamadı!")

    urun_bilgisi = {"isim": silinecek_urun.isim, "barkod": silinecek_urun.barkod}
    db.delete(silinecek_urun)
    db.commit()
    return {"mesaj": "Ürün silindi", "detay": urun_bilgisi}

@app.delete("/kategoriler/{kategori_ad}")
def kategori_sil(kategori_ad: str, db: Session = Depends(get_db)):
    silinecek_kategori = db.query(Kategori).filter(Kategori.ad == kategori_ad).first()
    if not silinecek_kategori:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı!")

    urun_sayisi = len(silinecek_kategori.urunler)
    db.delete(silinecek_kategori)
    db.commit()
    return {"mesaj": f"{kategori_ad} kategorisi ve {urun_sayisi} ürün silindi"}

@app.get("/stok/")
def stok_listesi(db: Session = Depends(get_db)):
    return db.query(UrunModel).all()

# --- 7. GÖRSEL STOK PANELİ ---

@app.get("/stok-paneli/", response_class=HTMLResponse)
def stok_paneli_arayuzu(db: Session = Depends(get_db)):
    urunler = db.query(UrunModel).all()
    
    # Tablo satırlarını oluşturma
    satirlar = ""
    for urun in urunler:
        kat_ad = urun.kategori.ad if urun.kategori else "Yok"
        satirlar += f"""
        <tr>
            <td>{urun.barkod}</td>
            <td>{urun.isim}</td>
            <td><b style="color: #2c3e50;">{urun.miktar}</b></td>
            <td><span style="background:#dfe6e9; padding:3px 8px; border-radius:5px;">{kat_ad}</span></td>
            <td>
                <button onclick="js_urun_sil('{urun.barkod}')" style="background:#ff4757; color:white; border:none; padding:6px 12px; cursor:pointer; border-radius:4px;">🗑️ Sil</button>
            </td>
        </tr>
        """

    return f"""
    <html>
        <head>
            <title>Depo Admin Paneli</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #f1f2f6; padding: 20px; }}
                .container {{ max-width: 1000px; margin: auto; }}
                .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                h2 {{ color: #2f3542; border-bottom: 2px solid #f1f2f6; padding-bottom: 10px; }}
                
                /* Form Tasarımı */
                .form-group {{ display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }}
                input {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; flex: 1; min-width: 150px; }}
                .btn-ekle {{ background: #2ed573; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                .btn-ekle:hover {{ background: #26af60; }}

                /* Tablo Tasarımı */
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background: #2f3542; color: white; padding: 15px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="text-align:center; color:#2f3542;">📦 Depo Kontrol Merkezi</h1>

                <div class="card">
                    <h2>➕ Yeni Ürün Ekle / Stok Güncelle</h2>
                    <div class="form-group">
                        <input type="text" id="ins_barkod" placeholder="Barkod (Örn: ABC123)">
                        <input type="text" id="ins_isim" placeholder="Ürün Adı">
                        <input type="number" id="ins_miktar" placeholder="Miktar">
                        <input type="text" id="ins_kategori" placeholder="Kategori">
                        <button onclick="js_urun_ekle()" class="btn-ekle">Kaydet / Güncelle</button>
                    </div>
                </div>

                <div class="card">
                    <h2>📋 Mevcut Stok Durumu</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Barkod</th>
                                <th>Ürün Adı</th>
                                <th>Miktar</th>
                                <th>Kategori</th>
                                <th>İşlemler</th>
                            </tr>
                        </thead>
                        <tbody>{satirlar}</tbody>
                    </table>
                </div>
            </div>

            <script>
                // ÜRÜN EKLEME FONKSİYONU (API POST isteği atar)
                async function js_urun_ekle() {{
                    const veri = {{
                        barkod: document.getElementById('ins_barkod').value,
                        isim: document.getElementById('ins_isim').value,
                        miktar: parseInt(document.getElementById('ins_miktar').value),
                        kategori_ad: document.getElementById('ins_kategori').value
                    }};

                    const res = await fetch('/urunler/', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(veri)
                    }});

                    if(res.ok) {{
                        alert('İşlem Başarılı!');
                        location.reload();
                    }} else {{
                        const hata = await res.json();
                        alert('Hata: ' + JSON.stringify(hata.detaylar || hata.detail));
                    }}
                }}

                // ÜRÜN SİLME FONKSİYONU (API DELETE isteği atar)
                async function js_urun_sil(barkod) {{
                    if(confirm(barkod + ' barkodlu ürün silinecek. Emin misin?')) {{
                        const res = await fetch('/urunler/' + barkod, {{ method: 'DELETE' }});
                        if(res.ok) {{
                            location.reload();
                        }}
                    }}
                }}
            </script>
        </body>
    </html>
    """