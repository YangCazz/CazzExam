import sys, os, json, sqlite3, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.config import DATA_DIR


def main():
    ok = True
    db = DATA_DIR / "study.db"
    print("DB file:", "OK" if db.exists() else "MISSING", db)
    if not db.exists():
        ok = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=3) as r:
            print("Backend :8000:", "OK", json.load(r))
    except Exception as e:
        print("Backend :8000: DOWN -", e)
        ok = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:5173/", timeout=3) as r:
            print("Frontend :5173:", "OK", r.status)
    except Exception as e:
        print("Frontend :5173: DOWN -", e)
        ok = False
    if db.exists():
        conn = sqlite3.connect(db)
        for tbl, label in [("questions", "题目"), ("knowledge_points", "知识点"),
                           ("knowledge_relations", "关联边"), ("wrong_questions", "错题")]:
            try:
                n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                print(f"  {label}: {n}")
            except Exception as e:
                print(f"  {label}: ERROR {e}")
        conn.close()
    print("== 健康检查:", "PASS" if ok else "存在异常 ==")


if __name__ == "__main__":
    main()
