# 软考架构师备考系统 - 后端

## 环境
- Python 3.12（工作区 tools/python 内嵌版，或系统 Python）
- 依赖：pip install -r requirements.txt

## 启动
```
python scripts/init_db.py      # 初始化数据库 + 种子数据
uvicorn app.main:app --port 8000
```

## API 一览（前缀 /api）
- GET /api/health
- GET /api/knowledge/tree | /graph | POST /points /relations
- GET/POST /api/questions
- GET/POST /api/exams/templates | POST /papers | GET /papers/{id} | POST /attempts | POST /attempts/{id}/submit
- GET/POST /api/wrong | POST /api/wrong/{id}/review
- GET/POST /api/plans
- GET /api/stats/overview
- GET/POST /api/essay/materials | GET /api/essay/adr
- POST /api/import/json

## 数据文件
- SQLite 数据库位于 backend/data/study.db（自动创建）
