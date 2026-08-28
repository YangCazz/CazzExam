import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.question import Question, QuestionItem, QuestionKnowledge

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/json")
def import_json(payload: dict, db: Session = Depends(get_db)):
    """payload: {"questions": [...]} 批量导入"""
    count = 0
    for it in payload.get("questions", []):
        q = Question(
            qtype=it.get("qtype", "choice"), subject=it.get("subject", 1), stem=it["stem"],
            options_json=json.dumps(it.get("options", []), ensure_ascii=False),
            answer_json=json.dumps(it.get("answer", ""), ensure_ascii=False),
            analysis=it.get("analysis", ""), difficulty=it.get("difficulty", 3),
            source_type=it.get("source_type", "self"), source_year=it.get("source_year"))
        db.add(q)
        db.flush()
        for kpid in it.get("knowledge_ids", []):
            db.add(QuestionKnowledge(question_id=q.id, knowledge_id=kpid))
        for item in it.get("items", []):
            db.add(QuestionItem(question_id=q.id, seq=item.get("seq", 1),
                                stem=item.get("stem", ""), answer=item.get("answer", ""),
                                score=item.get("score", 0)))
        count += 1
    db.commit()
    return {"imported": count}
