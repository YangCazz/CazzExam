from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from ..database import get_db
from ..models.plan import StudyPlan

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("")
def list_plans(db: Session = Depends(get_db)):
    rows = db.scalars(select(StudyPlan).order_by(StudyPlan.date.desc())).all()
    return [{"id": p.id, "date": p.date.isoformat() if p.date else None, "phase": p.phase,
             "task_type": p.task_type, "target": p.target, "done": p.done} for p in rows]


@router.get("/today")
def today_tasks(db: Session = Depends(get_db)):
    """今日任务：待复习错题数 + 薄弱知识点 Top5（有作答且正确率<60%）"""
    from ..models.wrong import WrongQuestion
    from ..models.exam import Answer
    from ..models.question import QuestionKnowledge
    from ..models.knowledge import KnowledgePoint
    now = datetime.now()
    due = db.scalar(select(func.count(WrongQuestion.id)).where(
        WrongQuestion.status.in_(["new", "reviewing"]),
        or_(WrongQuestion.next_review_at <= now, WrongQuestion.next_review_at.is_(None)))) or 0
    weak = []
    for kp in db.scalars(select(KnowledgePoint)).all():
        qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.knowledge_id == kp.id)).all()
        qids = [qk.question_id for qk in qks]
        if not qids:
            continue
        total = db.scalar(select(func.count(Answer.id)).where(Answer.question_id.in_(qids))) or 0
        correct = db.scalar(select(func.count(Answer.id)).where(
            Answer.question_id.in_(qids), Answer.is_correct == 1)) or 0
        if total and correct / total < 0.6:
            weak.append({"id": kp.id, "name": kp.name,
                         "accuracy": round(correct / total, 4), "answered": total})
    weak.sort(key=lambda x: x["accuracy"])
    return {"date": now.date().isoformat(), "due_reviews": due, "weak_kps": weak[:5]}


@router.post("/generate")
def generate_plan(payload: dict, db: Session = Depends(get_db)):
    """按考试日期倒推生成四阶段计划：基础学习→真题精练→套卷模拟→错题冲刺"""
    exam_date = datetime.strptime(payload["exam_date"], "%Y-%m-%d").date()
    today = datetime.now().date()
    days = (exam_date - today).days
    if days <= 0:
        raise HTTPException(400, "考试日期必须晚于今天")
    db.query(StudyPlan).delete()
    phases = [("基础学习", 0.25), ("真题精练", 0.30), ("套卷模拟", 0.30), ("错题冲刺", 0.15)]
    created = 0
    cursor = today
    for name, ratio in phases:
        span = max(1, int(days * ratio))
        end = cursor + timedelta(days=span - 1)
        db.add(StudyPlan(phase=name, task_type="阶段",
                         target=f"{name}：{cursor.isoformat()} ~ {end.isoformat()}"))
        created += 1
        cursor = end + timedelta(days=1)
    db.commit()
    return {"created": created, "exam_date": exam_date.isoformat(), "total_days": days}


@router.post("")
def create_plan(payload: dict, db: Session = Depends(get_db)):
    p = StudyPlan(phase=payload.get("phase", ""), task_type=payload.get("task_type", ""),
                  target=payload.get("target", ""))
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id}
