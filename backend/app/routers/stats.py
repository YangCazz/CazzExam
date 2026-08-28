from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import select, func
from ..database import get_db
from ..models.wrong import WrongQuestion
from ..models.question import Question, QuestionKnowledge
from ..models.knowledge import KnowledgePoint
from ..models.exam import Attempt, Answer

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/knowledge")
def knowledge_stats(db: Session = Depends(get_db)):
    kps = db.scalars(select(KnowledgePoint)).all()
    result = []
    for kp in kps:
        qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.knowledge_id == kp.id)).all()
        qids = [qk.question_id for qk in qks]
        if not qids:
            result.append({"knowledge_id": kp.id, "name": kp.name, "accuracy": None, "answered": 0})
            continue
        total = db.scalar(select(func.count(Answer.id)).where(Answer.question_id.in_(qids))) or 0
        correct = db.scalar(select(func.count(Answer.id)).where(
            Answer.question_id.in_(qids), Answer.is_correct == 1)) or 0
        result.append({"knowledge_id": kp.id, "name": kp.name,
                       "accuracy": round(correct / total, 4) if total else None,
                       "answered": total})
    return result


@router.get("/trend")
def trend(days: int = 14, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Attempt.started_at, Answer.is_correct).join(Answer, Answer.attempt_id == Attempt.id)
    ).all()
    day_map: dict = {}
    for started_at, is_correct in rows:
        if started_at is None:
            continue
        day = started_at.date().isoformat()
        d = day_map.setdefault(day, [0, 0])
        d[0] += 1
        if is_correct:
            d[1] += 1
    out = []
    today = datetime.now().date()
    for i in range(days - 1, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        d = day_map.get(day, [0, 0])
        out.append({"date": day, "answered": d[0], "correct": d[1],
                    "accuracy": round(d[1] / d[0], 4) if d[0] else None})
    return out


@router.get("/error-dist")
def error_dist(db: Session = Depends(get_db)):
    rows = db.execute(
        select(WrongQuestion.error_type, func.count()).group_by(WrongQuestion.error_type)).all()
    return [{"error_type": k or "未归因", "count": v} for k, v in rows]


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_q = db.scalar(select(func.count(Question.id))) or 0
    total_att = db.scalar(select(func.count(Attempt.id))) or 0
    total_ans = db.scalar(select(func.count(Answer.id))) or 0
    correct_ans = db.scalar(select(func.count(Answer.id)).where(Answer.is_correct == 1)) or 0
    return {
        "total_questions": total_q,
        "total_attempts": total_att,
        "total_answers": total_ans,
        "accuracy": round(correct_ans / total_ans, 4) if total_ans else None,
    }
