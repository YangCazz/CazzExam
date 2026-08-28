# 软考·系统架构设计师备考系统

个人本地备考系统（目标 2026-11 考试）。功能：知识库+知识图谱、练习模式、三科模拟考试、错题本（SM-2 间隔复习+归因反思）、论文专项+AI 批改（待 key）、统计画像、学习计划。

## 项目导航
- 项目总纲、目录规划、交接与上下文恢复：[docs/00-项目总纲与交接指南.md](docs/00-项目总纲与交接指南.md)
- 当前产品需求（PRD）：[docs/01-产品需求/PRD-系统架构设计师备考工作台-v1.md](docs/01-产品需求/PRD-系统架构设计师备考工作台-v1.md)
- 当前产品设计：[docs/02-产品设计/核心学习闭环与信息架构-v1.md](docs/02-产品设计/核心学习闭环与信息架构-v1.md)
- P0/P1 用户故事与验收：[docs/02-产品设计/P0-P1-用户故事与验收场景-v1.md](docs/02-产品设计/P0-P1-用户故事与验收场景-v1.md)
- 关键页面线框与交互：[docs/02-产品设计/关键页面线框与交互状态-v1.md](docs/02-产品设计/关键页面线框与交互状态-v1.md)
- 视觉与美术方案：[docs/02-产品设计/视觉与美术方案-v1.md](docs/02-产品设计/视觉与美术方案-v1.md)
- 页面美术概念稿：[docs/02-产品设计/页面美术概念稿索引-v1.md](docs/02-产品设计/页面美术概念稿索引-v1.md)
- P0/P1 软件需求：[docs/03-软件需求/SRS-P0-P1-学习闭环-v1.md](docs/03-软件需求/SRS-P0-P1-学习闭环-v1.md)
- P0/P1 概要技术设计：[docs/04-技术设计/P0-P1-概要技术设计与迁移方案-v1.md](docs/04-技术设计/P0-P1-概要技术设计与迁移方案-v1.md)
- 产品方向探索：[docs/产品设计探索-v2.md](docs/产品设计探索-v2.md)
- 现有实现基线：[docs/软考架构师备考系统-详细设计v1.md](docs/软考架构师备考系统-详细设计v1.md)

## 快速启动
- Windows：双击 start.cmd（自动起后端 :8000 与前端 :5173），访问 http://127.0.0.1:5173
- 手动：backend 起 `uvicorn app.main:app --port 8000`；frontend 起 `npm run dev`
- 健康自检：`python backend/scripts/health_check.py`

## 内容现状
- 55 个大纲知识点 / 26 条关联边 / 74 题（60 单选 + 6 案例 + 8 论文）
- 真题 PDF → 提取 → Excel 模板 → 批量入库（管线已就绪，见 docs/使用指南.md）

## 目录
- backend/  FastAPI + SQLAlchemy + SQLite（数据 backend/data/study.db；脚本 scripts/）
- frontend/ Vue3 + Vite + ECharts
- docs/     详细设计文档、使用指南、导入模板
- tools/    内嵌 Python 与工具脚本

## 测试与备份
- 测试：`python -m pytest backend/tests`（8 项全绿）
- 备份：`python backend/scripts/backup_db.py`（保留最近 20 份）
