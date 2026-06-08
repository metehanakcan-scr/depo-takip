import subprocess
import os
from datetime import datetime

YEDEK_KLASOR = r"C:\Users\USER\Documents\depo_api\DEPO_API_YEDEKLERI"

os.makedirs(YEDEK_KLASOR, exist_ok=True)

tarih = datetime.now().strftime("%Y%m%d_%H%M%S")

yedek_dosya = os.path.join(
    YEDEK_KLASOR,
    f"depo_{tarih}.sql"
)

env = os.environ.copy()
env["PGPASSWORD"] = "123456"

subprocess.run([
    r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
    "-U", "postgres",
    "-d", "depo_db",
    "-f", yedek_dosya
], env=env)

print("Yedek oluşturuldu:", yedek_dosya)