from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models.essay import EssayMaterial, Adr

router = APIRouter(prefix="/api/essay", tags=["essay"])


@router.get("/materials")
def list_materials(db: Session = Depends(get_db)):
    rows = db.scalars(select(EssayMaterial)).all()
    return [{"id": m.id, "category": m.category, "title": m.title, "tags": m.tags} for m in rows]


@router.post("/materials")
def create_material(payload: dict, db: Session = Depends(get_db)):
    m = EssayMaterial(category=payload.get("category", "项目经历"), title=payload.get("title", ""),
                      content=payload.get("content", ""), tags=payload.get("tags", ""))
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id}


@router.get("/adr")
def list_adr(db: Session = Depends(get_db)):
    rows = db.scalars(select(Adr)).all()
    return [{"id": a.id, "title": a.title, "status": a.status,
             "date": a.date.isoformat() if a.date else None} for a in rows]
