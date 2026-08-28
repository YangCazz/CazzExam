import json
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from ..models.exam import PaperTemplate, Paper, PaperQuestion, Attempt, Answer
from ..models.question import Question, QuestionKnowledge, QuestionItem
from ..models.wrong import WrongQuestion
from ..models.knowledge import KnowledgePoint
from ..services.grading import grade_choice

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    rows = db.scalars(select(PaperTemplate)).all()
    return [{"id": t.id, "name": t.name, "subject": t.subject,
             "duration_min": t.duration_min, "config": json.loads(t.config_json or "{}")} for t in rows]


@router.post("/templates")
def create_template(payload: dict, db: Session = Depends(get_db)):
    t = PaperTemplate(name=payload["name"], subject=payload.get("subject", 1),
                      duration_min=payload.get("duration_min", 150),
                      config_json=json.dumps(payload.get("config", {}), ensure_ascii=False))
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id}


@router.post("/papers")
def create_paper(payload: dict, db: Session = Depends(get_db)):
    """组卷：模板随机抽题；支持 knowledge_ids 过滤（薄弱点专练）；
    question_ids 指定题目（错题重做、章节专练）。"""
    if payload.get("question_ids"):
        p = Paper(template_id=payload.get("template_id") or 1)
        db.add(p)
        db.flush()
        for i, qid in enumerate(payload["question_ids"]):
            db.add(PaperQuestion(paper_id=p.id, question_id=qid, seq=i + 1))
        db.commit()
        return {"id": p.id, "count": len(payload["question_ids"])}
    t = db.get(PaperTemplate, payload["template_id"])
    if not t:
        raise HTTPException(404, "template not found")
    p = Paper(template_id=t.id)
    db.add(p)
    db.flush()
    config = json.loads(t.config_json or "{}")
    rules = config.get("rules", [{"qtype": "choice", "count": 75}])
    kp_ids = payload.get("knowledge_ids")
    total = 0
    for rule in rules:
        stmt = select(Question).where(Question.qtype == rule["qtype"], Question.status == "active")
        if payload.get("subject"):
            stmt = stmt.where(Question.subject == payload["subject"])
        pool = db.scalars(stmt).all()
        if kp_ids:
            qk = db.scalars(select(QuestionKnowledge).where(
                QuestionKnowledge.knowledge_id.in_(kp_ids))).all()
            qid_set = {q.question_id for q in qk}
            pool = [q for q in pool if q.id in qid_set]
        picked = random.sample(pool, min(rule.get("count", 0), len(pool)))
        for i, q in enumerate(picked):
            db.add(PaperQuestion(paper_id=p.id, question_id=q.id, seq=total + i + 1))
        total += len(picked)
    db.commit()
    return {"id": p.id, "count": total}


@router.get("/papers/{pid}")
def get_paper(pid: int, db: Session = Depends(get_db)):
    p = db.get(Paper, pid)
    if not p:
        raise HTTPException(404, "paper not found")
    t = db.get(PaperTemplate, p.template_id)
    rows = db.scalars(select(PaperQuestion).where(PaperQuestion.paper_id == pid)
                      .order_by(PaperQuestion.seq)).all()
    qs = []
    for r in rows:
        q = db.get(Question, r.question_id)
        items = db.scalars(select(QuestionItem).where(QuestionItem.question_id == q.id)
                           .order_by(QuestionItem.seq)).all()
        qs.append({"seq": r.seq, "id": q.id, "qtype": q.qtype, "stem": q.stem,
                   "options": json.loads(q.options_json or "[]"),
                   "items": [{"seq": i.seq, "stem": i.stem, "score": i.score} for i in items]})
    return {"paper_id": pid, "template": t.name if t else "",
            "duration_min": t.duration_min if t else 150, "questions": qs}


@router.post("/attempts")
def start_attempt(payload: dict, db: Session = Depends(get_db)):
    a = Attempt(paper_id=payload.get("paper_id"), mode=payload.get("mode", "practice"))
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id}


@router.post("/attempts/{aid}/submit")
def submit_attempt(aid: int, payload: dict, db: Session = Depends(get_db)):
    a = db.get(Attempt, aid)
    if not a:
        raise HTTPException(404, "attempt not found")
    a.finished_at = datetime.now()
    correct = 0
    touched_kps: set = set()
    for ans in payload.get("answers", []):
        q = db.get(Question, ans["question_id"])
        is_correct = grade_choice(q, ans.get("user_answer")) if q.qtype == "choice" else None
        if is_correct:
            correct += 1
        db.add(Answer(attempt_id=aid, question_id=ans["question_id"],
                      user_answer_json=json.dumps(ans.get("user_answer"), ensure_ascii=False),
                      is_correct=1 if is_correct else 0,
                      time_spent=ans.get("time_spent", 0)))
        qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.question_id == q.id)).all()
        touched_kps.update(qk.knowledge_id for qk in qks)
        # 选择题答错 → 自动进错题本（未掌握的同类错题已存在则不重复）
        if is_correct is False:
            exists = db.scalar(select(WrongQuestion).where(
                WrongQuestion.question_id == q.id,
                WrongQuestion.status.in_(["new", "reviewing"])))
            if not exists:
                db.add(WrongQuestion(question_id=q.id, first_attempt_id=aid))
    a.total_score = float(correct)
    db.commit()
    _recalc_mastery(db, touched_kps)
    return {"correct": correct, "total": len(payload.get("answers", [])),
            "score": a.total_score, "attempt_id": aid}


@router.get("/attempts/{aid}/report")
def attempt_report(aid: int, db: Session = Depends(get_db)):
    a = db.get(Attempt, aid)
    if not a:
        raise HTTPException(404, "attempt not found")
    answers = db.scalars(select(Answer).where(Answer.attempt_id == aid)).all()
    total = len(answers)
    correct = sum(1 for x in answers if x.is_correct)
    by_kp: dict = {}
    wrongs = []
    for ans in answers:
        q = db.get(Question, ans.question_id)
        qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.question_id == q.id)).all()
        for qk in qks:
            kp = db.get(KnowledgePoint, qk.knowledge_id)
            b = by_kp.setdefault(qk.knowledge_id, {
                "knowledge_id": qk.knowledge_id,
                "name": kp.name if kp else str(qk.knowledge_id),
                "correct": 0, "total": 0})
            b["total"] += 1
            if ans.is_correct:
                b["correct"] += 1
        if q.qtype == "choice" and not ans.is_correct:
            wrongs.append({
                "question_id": q.id, "stem": q.stem,
                "user_answer": json.loads(ans.user_answer_json or "null"),
                "correct_answer": json.loads(q.answer_json) if q.answer_json else None,
                "analysis": q.analysis,
            })
    for b in by_kp.values():
        b["accuracy"] = round(b["correct"] / b["total"], 4) if b["total"] else 0
    # 主观题（案例/论文）：返回作答与参考答案供自评 / AI 批改
    subjective = []
    for ans in answers:
        q = db.get(Question, ans.question_id)
        if q.qtype != "choice":
            subjective.append({
                "question_id": q.id, "qtype": q.qtype, "stem": q.stem,
                "user_answer": json.loads(ans.user_answer_json or "null"),
                "reference": json.loads(q.answer_json) if q.answer_json else None,
                "analysis": q.analysis,
            })
    return {"attempt_id": aid, "score": a.total_score, "correct": correct, "total": total,
            "by_knowledge": sorted(by_kp.values(), key=lambda x: x["accuracy"]),
            "wrongs": wrongs, "subjective": subjective}


def _recalc_mastery(db: Session, kp_ids):
    """根据全部作答记录重算知识点掌握度（0-100）并写回，供图谱/知识树实时展示"""
    for kid in set(kp_ids):
        qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.knowledge_id == kid)).all()
        qids = [qk.question_id for qk in qks]
        if not qids:
            continue
        total = db.scalar(select(func.count(Answer.id)).where(Answer.question_id.in_(qids))) or 0
        correct = db.scalar(select(func.count(Answer.id)).where(
            Answer.question_id.in_(qids), Answer.is_correct == 1)) or 0
        kp = db.get(KnowledgePoint, kid)
        if kp and total:
            kp.mastery = round(correct / total * 100, 1)
    db.commit()


@router.get("/attempts")
def list_attempts(db: Session = Depends(get_db)):
    """考试历史：最近的作答记录"""
    rows = db.scalars(select(Attempt).order_by(Attempt.started_at.desc()).limit(50)).all()
    out = []
    for a in rows:
        p = db.get(Paper, a.paper_id) if a.paper_id else None
        t = db.get(PaperTemplate, p.template_id) if p else None
        answered = db.scalar(select(func.count(Answer.id)).where(Answer.attempt_id == a.id)) or 0
        out.append({
            "id": a.id, "mode": a.mode, "template": t.name if t else "",
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "finished_at": a.finished_at.isoformat() if a.finished_at else None,
            "score": a.total_score, "answered": answered,
        })
    return out
