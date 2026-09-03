# -*- coding: utf-8 -*-
"""
把 data/syllabus/architecture-syllabus.json、data/questions/*.json 以及
data/materials/*/questions.nif.json（外部来源经 data/sources/normalize.py 生成的 NIF）
幂等灌入后端数据库（knowledge_points 按 code 去重、questions 按 stem 去重）。

用法（在仓库根目录）：
    tools/python/python.exe data/import_materials.py
"""
import os, sys, json, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(REPO, "backend")
sys.path.insert(0, BACKEND)

from app.database import SessionLocal
from app.models.knowledge import KnowledgePoint, KnowledgeRelation
from app.models.question import Question, QuestionItem, QuestionKnowledge

SYLLABUS = os.path.join(REPO, "data", "syllabus", "architecture-syllabus.json")
QUESTIONS = os.path.join(REPO, "data", "questions", "architecture-questions.json")
MATERIALS_GLOB = os.path.join(REPO, "data", "materials", "*", "questions.nif.json")
CARDS_GLOB = os.path.join(REPO, "data", "materials", "*", "cards.nif.json")


def seed_knowledge(db, code2id):
    with open(SYLLABUS, encoding="utf-8") as f:
        syl = json.load(f)
    added = 0
    for kp in syl["knowledge"]:
        code, name = kp["code"], kp["name"]
        if code in code2id:
            continue
        parent_id = code2id.get(kp.get("parent_code"))  # 父先于子，逐条插入即可
        row = KnowledgePoint(parent_id=parent_id, code=code, name=name,
                             description=kp.get("description", ""), subject=kp.get("subject", 1))
        db.add(row)
        db.flush()
        code2id[code] = row.id
        added += 1
    db.commit()
    print(f"knowledge points added: {added}  (tree total: {len(code2id)})")

    rel_added = 0
    for fc, tc, rt in syl.get("relations", []):
        f, t = code2id.get(fc), code2id.get(tc)
        if not f or not t:
            print("  skip relation (missing code):", fc, tc)
            continue
        dup = db.query(KnowledgeRelation).filter_by(from_id=f, to_id=t, relation_type=rt).first()
        if dup:
            continue
        db.add(KnowledgeRelation(from_id=f, to_id=t, relation_type=rt))
        rel_added += 1
    db.commit()
    print(f"relations added: {rel_added}")


def seed_questions(db, code2id):
    with open(QUESTIONS, encoding="utf-8") as f:
        data = json.load(f)
    existing = {q.stem for q in db.query(Question).all()}
    added = 0
    for q in data["questions"]:
        stem = q["stem"]
        if not stem or stem in existing:
            continue
        row = Question(
            qtype=q.get("qtype", "choice"), subject=q.get("subject", 1), stem=stem,
            options_json=json.dumps(q.get("options", []), ensure_ascii=False),
            answer_json=json.dumps(q.get("answer", ""), ensure_ascii=False),
            analysis=q.get("analysis", ""), difficulty=q.get("difficulty", 3),
            source_type=q.get("source_type", "self"), source_year=q.get("source_year"),
        )
        db.add(row)
        db.flush()
        for kc in q.get("knowledge_codes", []):
            kid = code2id.get(kc)
            if kid:
                db.add(QuestionKnowledge(question_id=row.id, knowledge_id=kid))
            else:
                print("  question has unknown knowledge_code:", kc, "->", stem[:24])
        for seq, item in enumerate(q.get("items", []), 1):
            db.add(QuestionItem(question_id=row.id, seq=item.get("seq", seq),
                                stem=item.get("stem", ""), answer=item.get("answer", ""),
                                score=item.get("score", 0)))
        existing.add(stem)
        added += 1
    db.commit()
    print(f"questions added: {added}")


def seed_materials(db, code2id):
    """导入 data/materials/*/questions.nif.json（外部来源经 normalize.py 生成）。按 stem 去重。"""
    existing = {q.stem for q in db.query(Question).all()}
    total = 0
    for nif_path in sorted(glob.glob(MATERIALS_GLOB)):
        with open(nif_path, encoding="utf-8") as f:
            data = json.load(f)
        src = data.get("source", nif_path)
        added = 0
        for q in data["questions"]:
            stem = q["stem"]
            if not stem or stem in existing:
                continue
            row = Question(
                qtype=q.get("qtype", "choice"), subject=q.get("subject", 1), stem=stem,
                options_json=json.dumps(q.get("options", []), ensure_ascii=False),
                answer_json=json.dumps(q.get("answer", ""), ensure_ascii=False),
                analysis=q.get("analysis", ""), difficulty=q.get("difficulty", 3),
                source_type=q.get("source_type", "real"), source_year=q.get("source_year"),
            )
            db.add(row)
            db.flush()
            for kc in q.get("knowledge_codes", []):
                kid = code2id.get(kc)
                if kid:
                    db.add(QuestionKnowledge(question_id=row.id, knowledge_id=kid))
                else:
                    print("  [%s] 未知知识点 code: %s -> %s" % (src, kc, stem[:22]))
            for seq, item in enumerate(q.get("items", []), 1):
                db.add(QuestionItem(question_id=row.id, seq=item.get("seq", seq),
                                    stem=item.get("stem", ""), answer=item.get("answer", ""),
                                    score=item.get("score", 0)))
            existing.add(stem)
            added += 1
        print(f"  material {os.path.basename(os.path.dirname(nif_path))}: added {added}")
        total += added
    db.commit()
    print(f"materials questions added: {total}")


def seed_cards(db, code2id):
    """把 data/materials/*/cards.nif.json 的结构化速查卡按 code 幂等覆盖到 knowledge_points.card。"""
    total = 0
    for nif_path in sorted(glob.glob(CARDS_GLOB)):
        with open(nif_path, encoding="utf-8") as f:
            data = json.load(f)
        src = data.get("source", nif_path)
        for card in data.get("cards", []):
            if card.get("skip_on_import") or not card.get("knowledge_codes"):
                if card.get("skip_on_import"):
                    print(f"  [{src}] 跳过(无挂点): {card.get('file')}")
                continue
            for kc in card["knowledge_codes"]:
                kid = code2id.get(kc)
                if not kid:
                    print(f"  [{src}] 未知名知识点 code: {kc} -> {card.get('file')}")
                    continue
                kp = db.get(KnowledgePoint, kid)
                if kp:
                    kp.card = json.dumps(card, ensure_ascii=False)
                    total += 1
                else:
                    print(f"  [{src}] 知识点行缺失: {kc}")
    db.commit()
    print(f"cards written: {total}")


def main():
    db = SessionLocal()
    code2id = {k.code: k.id for k in db.query(KnowledgePoint).all()}
    print("existing knowledge points:", len(code2id))
    seed_knowledge(db, code2id)
    seed_questions(db, code2id)
    seed_materials(db, code2id)
    seed_cards(db, code2id)
    db.close()
    print("done.")


if __name__ == "__main__":
    main()
