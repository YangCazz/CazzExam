import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.database import SessionLocal
from app.models.question import Question, QuestionItem, QuestionKnowledge


def main(path: str):
    db = SessionLocal()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for it in data.get("questions", []):
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
        n += 1
    db.commit()
    db.close()
    print("imported", n)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python import_json.py <file.json>")
        sys.exit(1)
    main(sys.argv[1])
