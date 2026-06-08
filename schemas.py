from pydantic import BaseModel
from typing import Optional


class UrunSema(BaseModel):
    barkod: str
    isim: str
    lot: Optional[str] = None
    miktar: int
    kategori_ad: Optional[str] = None
    islem_nedeni: Optional[str] = "Giriş"
    not_alani: Optional[str] = ""
    yer: Optional[str] = None
    musteri_ad: Optional[str] = None
    islem_tipi: Optional[str] = "Giriş"


from pydantic import BaseModel
from typing import Optional, List

class StokCikisSema(BaseModel):
    barkod: str
    miktar: int
    lot: Optional[str] = None

class TopluCikisSema(BaseModel):
    urunler: List[StokCikisSema]
    musteri: str
    aciklama: Optional[str] = ""