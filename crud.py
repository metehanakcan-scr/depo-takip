from sqlalchemy.orm import Session
from models import UrunModel, Kategori, StokHareketi, Musteri
from schemas import UrunSema

def urunleri_getir(db: Session):
    return db.query(UrunModel).all()

def urun_bul_barkod(db: Session, barkod: str):
    return db.query(UrunModel).filter(UrunModel.barkod == barkod).first()

def hareket_kaydet(db: Session, barkod: str, isim: str, miktar: int, tip: str):
    yeni_hareket = StokHareketi(urun_barkod=barkod, urun_isim=isim, miktar_degisimi=miktar, islem_tipi=tip)
    db.add(yeni_hareket)
    db.commit()

def urun_kaydet(db: Session, urun_verisi: UrunSema):
    kategori = db.query(Kategori).filter(Kategori.ad == urun_verisi.kategori_ad).first()
    if not kategori:
        kategori = Kategori(ad=urun_verisi.kategori_ad)
        db.add(kategori)
        db.commit()
        db.refresh(kategori)

    mevcut = urun_bul_barkod(db, urun_verisi.barkod)
    if mevcut:
        mevcut.miktar += urun_verisi.miktar
        mevcut.isim = urun_verisi.isim
        mevcut.lot = urun_verisi.lot
        db.commit()
        return mevcut
    else:
        yeni = UrunModel(barkod=urun_verisi.barkod, isim=urun_verisi.isim, lot=urun_verisi.lot, miktar=urun_verisi.miktar, kategori=kategori)
        db.add(yeni)
        db.commit()
        return yeni