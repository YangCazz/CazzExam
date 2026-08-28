from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models.knowledge import KnowledgePoint, KnowledgeRelation
from ..models.question import Question, QuestionKnowledge

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/tree")
def get_tree(db: Session = Depends(get_db)):
    kps = db.scalars(select(KnowledgePoint).order_by(KnowledgePoint.code)).all()
    return [
        {"id": k.id, "parent_id": k.parent_id, "name": k.name, "code": k.code,
         "subject": k.subject, "mastery": k.mastery}
        for k in kps
    ]


@router.get("/graph")
def get_graph(db: Session = Depends(get_db)):
    kps = db.scalars(select(KnowledgePoint)).all()
    rels = db.scalars(select(KnowledgeRelation)).all()
    return {
        "nodes": [{"id": k.id, "name": k.name, "mastery": k.mastery, "subject": k.subject} for k in kps],
        "links": [{"source": r.from_id, "target": r.to_id, "type": r.relation_type} for r in rels],
    }


@router.get("/points/{kpid}")
def point_detail(kpid: int, db: Session = Depends(get_db)):
    kp = db.get(KnowledgePoint, kpid)
    if not kp:
        raise HTTPException(404, "not found")
    children = db.scalars(select(KnowledgePoint).where(KnowledgePoint.parent_id == kpid)).all()
    qks = db.scalars(select(QuestionKnowledge).where(QuestionKnowledge.knowledge_id == kpid)).all()
    qids = [qk.question_id for qk in qks]
    questions = db.scalars(select(Question).where(Question.id.in_(qids))).all() if qids else []
    rels_out = db.scalars(select(KnowledgeRelation).where(KnowledgeRelation.from_id == kpid)).all()
    rels_in = db.scalars(select(KnowledgeRelation).where(KnowledgeRelation.to_id == kpid)).all()
    return {
        "id": kp.id, "name": kp.name, "code": kp.code, "subject": kp.subject,
        "description": kp.description, "memo": kp.memo, "mastery": kp.mastery,
        "children": [{"id": c.id, "name": c.name} for c in children],
        "questions": [{"id": q.id, "qtype": q.qtype, "stem": q.stem} for q in questions],
        "related": [{"id": r.to_id, "type": r.relation_type} for r in rels_out]
                  + [{"id": r.from_id, "type": r.relation_type} for r in rels_in],
    }


@router.put("/points/{kpid}")
def update_point(kpid: int, payload: dict, db: Session = Depends(get_db)):
    kp = db.get(KnowledgePoint, kpid)
    if not kp:
        raise HTTPException(404, "not found")
    for k in ("name", "code", "subject", "description", "memo", "parent_id"):
        if k in payload:
            setattr(kp, k, payload[k])
    db.commit()
    return {"id": kp.id}


@router.post("/points")
def create_point(payload: dict, db: Session = Depends(get_db)):
    kp = KnowledgePoint(**{k: v for k, v in payload.items()
                           if k in {"parent_id", "name", "code", "subject", "description", "memo"}})
    db.add(kp)
    db.commit()
    db.refresh(kp)
    return {"id": kp.id}


@router.post("/relations")
def create_relation(payload: dict, db: Session = Depends(get_db)):
    rel = KnowledgeRelation(
        from_id=payload["from_id"], to_id=payload["to_id"],
        relation_type=payload.get("relation_type", "related"), note=payload.get("note", ""))
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return {"id": rel.id}
