import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from ..database import get_db
from ..models.wrong import WrongQuestion, ReviewLog
from ..models.question import Question, QuestionKnowledge
from ..models.knowledge import KnowledgePoint
from ..services.sm2 import sm2_schedule

router = APIRouter(prefix="/api/wrong", tags=["wrong"])


def _serialize(w: WrongQuestion, db: Session, with_q: bool = False) -> dict:
    base = {
        "id": w.id, "question_id": w.question_id, "error_type": w.error_type,
        "reflection": w.reflection, "status": w.status, "repetition": w.repetition,
        "interval_days": w.interval_days, "ease_factor": w.ease_factor,
        "next_review_at": w.next_review_at.isoformat() if w.next_review_at else None,
    }
    if with_q:
        q = db.get(Question, w.question_id)
        if q:
            qks = db.scalars(select(QuestionKnowledge).where(
                QuestionKnowledge.question_id == q.id)).all()
            kps = []
            for qk in qks:
                kp = db.get(KnowledgePoint, qk.knowledge_id)
                if kp:
                    kps.append({"id": kp.id, "name": kp.name})
            base["question"] = {
                "id": q.id, "qtype": q.qtype, "subject": q.subject, "stem": q.stem,
                "options": json.loads(q.options_json or "[]"),
                "answer": json.loads(q.answer_json) if q.answer_json else None,
                "analysis": q.analysis, "knowledge": kps,
            }
    return base


@router.get("")
def list_wrong(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(WrongQuestion).order_by(WrongQuestion.created_at.desc())
    if status:
        stmt = stmt.where(WrongQuestion.status == status)
    rows = db.scalars(stmt).all()
    return [_serialize(w, db) for w in rows]


@router.get("/queue")
def review_queue(db: Session = Depends(get_db)):
    """待复习队列：到期的或尚未安排复习时间的错题（带完整题目内容）"""
    now = datetime.now()
    rows = db.scalars(select(WrongQuestion).where(
        WrongQuestion.status.in_(["new", "reviewing"]),
        or_(WrongQuestion.next_review_at <= now, WrongQuestion.next_review_at.is_(None)),
    ).order_by(WrongQuestion.next_review_at.asc().nullsfirst())).all()
    return [_serialize(w, db, with_q=True) for w in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    by_status = dict(db.execute(
        select(WrongQuestion.status, func.count()).group_by(WrongQuestion.status)).all())
    by_error = dict(db.execute(
        select(WrongQuestion.error_type, func.count()).group_by(WrongQuestion.error_type)).all())
    total = db.scalar(select(func.count(WrongQuestion.id))) or 0
    return {"total": total, "by_status": by_status, "by_error": by_error}


@router.post("")
def create_wrong(payload: dict, db: Session = Depends(get_db)):
    w = WrongQuestion(question_id=payload["question_id"],
                      error_type=payload.get("error_type", ""),
                      reflection=payload.get("reflection", ""),
                      next_review_at=datetime.now())
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"id": w.id}


@router.put("/{wid}")
def update_wrong(wid: int, payload: dict, db: Session = Depends(get_db)):
    """归因向导：更新错因类型与反思笔记"""
    w = db.get(WrongQuestion, wid)
    if not w:
        raise HTTPException(404, "not found")
    if "error_type" in payload:
        w.error_type = payload["error_type"]
    if "reflection" in payload:
        w.reflection = payload["reflection"]
    db.commit()
    return {"id": w.id}


@router.post("/{wid}/review")
def review_wrong(wid: int, payload: dict, db: Session = Depends(get_db)):
    """SM-2 复习反馈：quality 0-5"""
    w = db.get(WrongQuestion, wid)
    if not w:
        raise HTTPException(404, "not found")
    quality = payload.get("quality", 3)
    w.repetition, w.ease_factor, w.interval_days, w.next_review_at = sm2_schedule(
        w.repetition, w.ease_factor, w.interval_days, quality)
    w.status = "mastered" if w.repetition >= 3 else "reviewing"
    db.add(ReviewLog(wrong_question_id=wid, recalled=1 if quality >= 3 else 0,
                     note=payload.get("note", "")))
    db.commit()
    return {"status": w.status, "next_review_at": w.next_review_at.isoformat(),
            "repetition": w.repetition, "interval_days": w.interval_days}
