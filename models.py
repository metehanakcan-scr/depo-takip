from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime



class Kategori(Base):
    __tablename__ = "kategoriler"
    id = Column(Integer, primary_key=True)
    ad = Column(String, unique=True, nullable=False)
    urunler = relationship("UrunModel", back_populates="kategori", cascade="all, delete-orphan")

class UrunModel(Base):
    __tablename__ ="urunler"
    id = Column(Integer, primary_key=True, index=True) # ID bazlı eşleşme için eklendi
    barkod = Column(String, index=True)
    isim = Column(String, nullable=False)
    lot = Column(String, nullable=True) 
    miktar = Column(Integer, default=0)
    kategori_id = Column(Integer, ForeignKey("kategoriler.id"))
    kategori = relationship("Kategori", back_populates="urunler")
    yer = Column(String, nullable=True)
    kutu_ici = Column(String, nullable=True)
    

class DepoYeri(Base):
    __tablename__ = "depo_yerleri"
    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String, unique=True, index=True)

class Musteri(Base):
    __tablename__ = "musteriler"
    id = Column(Integer, primary_key=True)
    ad = Column(String, unique=True, nullable=False)

class StokHareketi(Base):
    __tablename__ = "stok_hareketleri"
    id = Column(Integer, primary_key=True)
    urun_barkod = Column(String)
    urun_isim = Column(String)
    urun_lot = Column(String, nullable=True)
    miktar_degisimi = Column(Integer)
    islem_tipi = Column(String)
    musteri_ad = Column(String, ForeignKey("musteriler.id"))
    tarih = Column(DateTime, default=datetime.now)
    islem_no = Column(Integer)
    islem_yapan = Column(String)
    aciklama = Column(String)
    islem_nedeni= Column(String)



class Rol(Base):
    __tablename__ = "roller"
    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String, unique=True, index=True) # "DEPO", "MÜDÜR" vb.
    
    # Yetki Matrisi Burası:
    can_add_stock = Column(Boolean, default=True)    # Stok ekleyebilir mi?
    can_exit_stock = Column(Boolean, default=True)   # Stok çıkarabilir mi?
    can_edit_product = Column(Boolean, default=False) # Ürün düzenleyebilir mi?
    can_delete = Column(Boolean, default=False)       # Silebilir mi?
    can_manage_users = Column(Boolean, default=False) # Kullanıcı yönetebilir mi?
    can_see_logs = Column(Boolean, default=True)      # Logları görebilir mi?

    # Bu role sahip kullanıcılar
    kullanicilar = relationship("Kullanici", back_populates="ait_oldugu_rol")

class Kullanici(Base):
    __tablename__ = "kullanicilar"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(Integer, primary_key=True, index=True, unique=True)
    kullanici_adi = Column(String, index=True)
    sifre = Column(String)
    
    # Rol bağlantısı
    rol_id = Column(Integer, ForeignKey("roller.id"))
    ait_oldugu_rol = relationship("Rol", back_populates="kullanicilar")


class Sayim(Base):
    __tablename__ = "sayimlar"
    id = Column(Integer, primary_key=True, index=True)
    barkod = Column(String)
    urun_adi = Column(String)
    lot_no = Column(String, nullable=True)
    miktar = Column(Float)
    kayit_tarihi = Column(DateTime, default=datetime.utcnow)

class İslem_nedeni(Base):
    __tablename__ = "islem_nedenleri"
    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String, unique=True, index=True) 

