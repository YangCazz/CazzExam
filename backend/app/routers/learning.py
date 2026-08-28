from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.learning import StudyProfile, LearningTask
from ..models.wrong import WrongQuestion
from ..models.knowledge import KnowledgePoint
from ..models.question import QuestionKnowledge, Question
from ..models.exam import Answer
from ..models.essay import EssayMaterial

router = APIRouter(prefix="/api/learning", tags=["learning"])


def _today():
    return datetime.now().date().isoformat()


def _profile(db):
    p = db.get(StudyProfile, 1)
    if not p:
        p = StudyProfile(id=1)
        db.add(p); db.commit(); db.refresh(p)
    return p


def _task_dict(t):
    return {"id": t.id, "date": t.task_date, "type": t.task_type, "subject": t.subject,
            "target_id": t.target_id, "title": t.title, "reason": t.reason,
            "completion_hint": t.completion_hint, "estimated_minutes": t.estimated_minutes,
            "status": t.status, "skip_reason": t.skip_reason}


def _risk_summary(db):
    labels = {1: "综合知识", 2: "案例分析", 3: "论文写作"}
    rows = []
    for subject, name in labels.items():
        qids = list(db.scalars(select(Question.id).where(Question.subject == subject)))
        total = db.scalar(select(func.count(Answer.id)).where(Answer.question_id.in_(qids))) if qids else 0
        correct = db.scalar(select(func.count(Answer.id)).where(Answer.question_id.in_(qids), Answer.is_correct == 1)) if qids else 0
        total = total or 0; correct = correct or 0
        if total < 3:
            level, evidence = "数据不足", "完成几次针对性训练后可形成可靠判断"
        else:
            accuracy = correct / total
            level = "安全" if accuracy >= .7 else ("临界" if accuracy >= .5 else "高风险")
            evidence = f"近期有效作答 {total} 次，正确率 {accuracy * 100:.0f}%"
        rows.append({"subject": subject, "name": name, "level": level, "evidence": evidence,
                     "accuracy": round(correct / total, 4) if total else None, "answered": total})
    return rows


def _ensure_tasks(db, minutes=None):
    today = _today()
    active = list(db.scalars(select(LearningTask).where(
        LearningTask.task_date == today, LearningTask.status.in_(["generated", "in_progress"]))))
    if active:
        return active
    p = _profile(db); budget = minutes or min(60, max(15, p.weekly_minutes // 5))
    used = 0; tasks = []
    due = db.scalars(select(WrongQuestion).where(WrongQuestion.status.in_(["new", "reviewing"]),
        or_(WrongQuestion.next_review_at <= datetime.now(), WrongQuestion.next_review_at.is_(None))).limit(1)).first()
    if due and budget >= 10:
        tasks.append(LearningTask(task_date=today, task_type="review", subject=0, target_id=due.id,
            title="到期复习 · 错题回忆", reason="今天到期，先回忆再查看答案", completion_hint="重新作答并记录回忆结果", estimated_minutes=10)); used += 10
    kp = db.scalars(select(KnowledgePoint).where(KnowledgePoint.mastery < 60).order_by(KnowledgePoint.mastery.asc())).first()
    if kp and budget - used >= 15:
        has_question = db.scalar(select(func.count(QuestionKnowledge.id)).where(QuestionKnowledge.knowledge_id == kp.id)) or 0
        if has_question:
            tasks.append(LearningTask(task_date=today, task_type="practice", subject=kp.subject or 1, target_id=kp.id,
                title=f"针对练习 · {kp.name}", reason=f"当前掌握度 {kp.mastery:.0f}%，优先补齐薄弱点", completion_hint="完成关联题并查看解析", estimated_minutes=15)); used += 15
    material_count = db.scalar(select(func.count(EssayMaterial.id))) or 0
    if material_count == 0 and budget - used >= 10:
        tasks.append(LearningTask(task_date=today, task_type="material", subject=3, target_id=None,
            title="论文素材 · 建立第一张项目事实卡", reason="论文素材不足，先沉淀真实项目经历", completion_hint="填写背景、职责、决策和结果", estimated_minutes=10))
    if not tasks:
        tasks.append(LearningTask(task_date=today, task_type="practice", subject=1, target_id=None,
            title="自由练习 · 综合知识", reason="暂未发现到期复习或可定位薄弱点", completion_hint="完成一组综合练习", estimated_minutes=min(15, budget)))
    db.add_all(tasks); db.commit()
    return tasks


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    p = _profile(db)
    return {"certification": p.certification, "target_date": p.target_date, "weekly_minutes": p.weekly_minutes, "timezone": p.timezone}


@router.put("/profile")
def update_profile(payload: dict, db: Session = Depends(get_db)):
    p = _profile(db)
    for key in ("certification", "target_date", "timezone"):
        if key in payload: setattr(p, key, str(payload[key]).strip())
    if "weekly_minutes" in payload:
        p.weekly_minutes = max(30, min(2400, int(payload["weekly_minutes"])))
    db.commit()
    return get_profile(db)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    tasks = _ensure_tasks(db)
    week_start = datetime.now().date().replace(day=max(1, datetime.now().day - datetime.now().weekday())).isoformat()
    completed = db.scalar(select(func.count(LearningTask.id)).where(LearningTask.task_date >= week_start, LearningTask.status == "completed")) or 0
    return {"date": _today(), "profile": get_profile(db), "tasks": [_task_dict(t) for t in tasks],
            "risks": _risk_summary(db), "week": {"completed_tasks": completed, "action": "优先完成到期复习，再补齐薄弱知识点"}}


@router.post("/tasks/replan")
def replan(payload: dict, db: Session = Depends(get_db)):
    today = _today()
    db.query(LearningTask).filter(LearningTask.task_date == today, LearningTask.status == "generated").update({"status": "expired"})
    return {"tasks": [_task_dict(t) for t in _ensure_tasks(db, int(payload.get("minutes", 30)))]}


@router.post("/tasks/{task_id}/{action}")
def task_action(task_id: int, action: str, payload: dict | None = None, db: Session = Depends(get_db)):
    t = db.get(LearningTask, task_id)
    if not t: raise HTTPException(404, "任务不存在")
    if action == "start": t.status = "in_progress"
    elif action == "complete": t.status = "completed"; t.completed_at = datetime.now()
    elif action == "skip": t.status = "skipped"; t.skip_reason = (payload or {}).get("reason", "用户跳过")
    else: raise HTTPException(422, "未知任务操作")
    db.commit(); return _task_dict(t)
