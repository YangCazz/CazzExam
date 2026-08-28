import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from ..database import get_db
from ..models.question import Question, QuestionItem, QuestionKnowledge
from ..models.exam import Attempt, Answer
from ..models.wrong import WrongQuestion
from ..services.grading import grade_choice

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
def list_questions(qtype: str | None = None, subject: int | None = None,
                   source_year: int | None = None, q: str | None = None,
                   skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stmt = select(Question).where(Question.status == "active")
    if qtype:
        stmt = stmt.where(Question.qtype == qtype)
    if subject:
        stmt = stmt.where(Question.subject == subject)
    if source_year:
        stmt = stmt.where(Question.source_year == source_year)
    if q:
        stmt = stmt.where(or_(Question.stem.contains(q), Question.analysis.contains(q)))
    rows = db.scalars(stmt.offset(skip).limit(limit)).all()
    return [
        {"id": x.id, "qtype": x.qtype, "subject": x.subject, "stem": x.stem,
         "options": json.loads(x.options_json or "[]"),
         "difficulty": x.difficulty, "source_year": x.source_year, "source_type": x.source_type}
        for x in rows
    ]


@router.post("/check")
def check_answer(payload: dict, db: Session = Depends(get_db)):
    """练习模式即时判分：返回对错/正确答案/解析，记录作答，答错自动进错题本，并回写掌握度"""
    q = db.get(Question, payload["question_id"])
    if not q:
        raise HTTPException(404, "question not found")
    is_correct = grade_choice(q, payload.get("user_answer")) if q.qtype == "choice" else None
    a = Attempt(mode="practice")
    db.add(a)
    db.flush()
    db.add(Answer(attempt_id=a.id, question_id=q.id,
                  user_answer_json=json.dumps(payload.get("user_answer"), ensure_ascii=False),
                  is_correct=1 if is_correct else 0,
                  time_spent=payload.get("time_spent", 0)))
    if is_correct is False:
        exists = db.scalar(select(WrongQuestion).where(
            WrongQuestion.question_id == q.id,
            WrongQuestion.status.in_(["new", "reviewing"])))
        if not exists:
            db.add(WrongQuestion(question_id=q.id, first_attempt_id=a.id))
    db.commit()
    qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.question_id == q.id)).all()
    from .exams import _recalc_mastery
    _recalc_mastery(db, {qk.knowledge_id for qk in qks})
    return {"is_correct": bool(is_correct),
            "correct_answer": json.loads(q.answer_json) if q.qtype == "choice" and q.answer_json else None,
            "reference": json.loads(q.answer_json) if q.qtype != "choice" and q.answer_json else None,
            "analysis": q.analysis, "attempt_id": a.id}


@router.get("/export")
def export_questions(db: Session = Depends(get_db)):
    """导出全部题目（含子问与知识点关联），用于备份/迁移"""
    rows = db.scalars(select(Question)).all()
    out = []
    for q in rows:
        items = db.scalars(select(QuestionItem).where(QuestionItem.question_id == q.id)
                           .order_by(QuestionItem.seq)).all()
        kps = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.question_id == q.id)).all()
        out.append({
            "id": q.id, "qtype": q.qtype, "subject": q.subject, "stem": q.stem,
            "options": json.loads(q.options_json or "[]"),
            "answer": json.loads(q.answer_json) if q.answer_json else None,
            "analysis": q.analysis, "difficulty": q.difficulty,
            "source_type": q.source_type, "source_year": q.source_year,
            "knowledge_ids": [k.knowledge_id for k in kps],
            "items": [{"seq": i.seq, "stem": i.stem, "answer": i.answer, "score": i.score} for i in items],
        })
    return {"count": len(out), "questions": out}


@router.get("/{qid}")
def get_question(qid: int, db: Session = Depends(get_db)):
    q = db.get(Question, qid)
    if not q:
        raise HTTPException(404, "question not found")
    items = db.scalars(select(QuestionItem).where(QuestionItem.question_id == qid)).all()
    kps = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.question_id == qid)).all()
    return {
        "id": q.id, "qtype": q.qtype, "subject": q.subject, "stem": q.stem,
        "options": json.loads(q.options_json or "[]"), "answer": q.answer_json,
        "analysis": q.analysis, "difficulty": q.difficulty,
        "source_type": q.source_type, "source_year": q.source_year,
        "items": [{"seq": i.seq, "stem": i.stem, "answer": i.answer, "score": i.score} for i in items],
        "knowledge_ids": [k.knowledge_id for k in kps],
    }


@router.post("")
def create_question(payload: dict, db: Session = Depends(get_db)):
    q = Question(
        qtype=payload.get("qtype", "choice"), subject=payload.get("subject", 1),
        stem=payload["stem"],
        options_json=json.dumps(payload.get("options", []), ensure_ascii=False),
        answer_json=json.dumps(payload.get("answer", ""), ensure_ascii=False),
        analysis=payload.get("analysis", ""), difficulty=payload.get("difficulty", 3),
        source_type=payload.get("source_type", "self"), source_year=payload.get("source_year"))
    db.add(q)
    db.flush()
    for kpid in payload.get("knowledge_ids", []):
        db.add(QuestionKnowledge(question_id=q.id, knowledge_id=kpid))
    for it in payload.get("items", []):
        db.add(QuestionItem(question_id=q.id, seq=it.get("seq", 1), stem=it.get("stem", ""),
                            answer=it.get("answer", ""), score=it.get("score", 0)))
    db.commit()
    db.refresh(q)
    return {"id": q.id}
