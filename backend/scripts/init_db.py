import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.database import init_db, SessionLocal
from app.models.knowledge import KnowledgePoint
from app.models.exam import PaperTemplate


def seed():
    db = SessionLocal()
    if db.query(KnowledgePoint).count() == 0:
        roots = [
            {"name": "计算机系统基础", "code": "1", "subject": 1},
            {"name": "软件工程与项目管理", "code": "2", "subject": 1},
            {"name": "系统架构设计（主线）", "code": "3", "subject": 1},
            {"name": "数学与经济管理", "code": "4", "subject": 1},
            {"name": "信息安全与可靠性", "code": "5", "subject": 1},
            {"name": "专业英语", "code": "6", "subject": 1},
        ]
        for r in roots:
            db.add(KnowledgePoint(**r))
        db.commit()
    if db.query(PaperTemplate).count() == 0:
        tpls = [
            {"name": "综合知识（75 单选 / 150min）", "subject": 1, "duration_min": 150,
             "config_json": json.dumps({"rules": [{"qtype": "choice", "count": 75}]})},
            {"name": "案例分析（5 大题 / 90min）", "subject": 2, "duration_min": 90,
             "config_json": json.dumps({"rules": [{"qtype": "case", "count": 5}]})},
            {"name": "论文（多选一 / 120min）", "subject": 3, "duration_min": 120,
             "config_json": json.dumps({"rules": [{"qtype": "essay", "count": 4}]})},
        ]
        for t in tpls:
            db.add(PaperTemplate(**t))
        db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
    seed()
    print("DB initialized and seeded")
