import sys, os, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.config import DATA_DIR

backup_dir = DATA_DIR / "backup"
backup_dir.mkdir(parents=True, exist_ok=True)
src = DATA_DIR / "study.db"
if not src.exists():
    print("no db file yet")
    sys.exit(0)
dst = backup_dir / f"study-{datetime.now():%Y%m%d-%H%M%S}.db"
conn = sqlite3.connect(src)
out = sqlite3.connect(dst)
with out:
    conn.backup(out)
out.close()
conn.close()
files = sorted(backup_dir.glob("study-*.db"))
for f in files[:-20]:
    f.unlink()
print("backup saved:", dst, "| kept", len(files[-20:]))
