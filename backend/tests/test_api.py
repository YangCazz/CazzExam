def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_knowledge_crud_and_graph(client):
    kid = client.post("/api/knowledge/points",
                      json={"name": "测试知识点", "code": "9.9", "subject": 1}).json()["id"]
    kid2 = client.post("/api/knowledge/points",
                       json={"name": "测试知识点2", "code": "9.8", "subject": 1}).json()["id"]
    r = client.post("/api/knowledge/relations",
                    json={"from_id": kid, "to_id": kid2, "relation_type": "related"})
    assert r.status_code == 200
    g = client.get("/api/knowledge/graph").json()
    assert len(g["nodes"]) >= 2 and len(g["links"]) >= 1
    d = client.get(f"/api/knowledge/points/{kid}").json()
    assert d["name"] == "测试知识点"


def test_question_and_exam_flow(client):
    q = client.post("/api/questions", json={
        "qtype": "choice", "subject": 1, "stem": "测试题：1+1=?",
        "options": ["A. 1", "B. 2", "C. 3", "D. 4"], "answer": "B",
        "analysis": "1+1=2", "difficulty": 1, "source_type": "self", "knowledge_ids": []})
    assert q.status_code == 200
    qid = q.json()["id"]
    tid = client.post("/api/exams/templates", json={
        "name": "测试模板", "subject": 1, "duration_min": 10,
        "config": {"rules": [{"qtype": "choice", "count": 1}]}}).json()["id"]
    p = client.post("/api/exams/papers", json={"template_id": tid}).json()
    assert p["count"] == 1
    a = client.post("/api/exams/attempts", json={"paper_id": p["id"], "mode": "mock"}).json()
    sub = client.post(f"/api/exams/attempts/{a['id']}/submit", json={
        "answers": [{"question_id": qid, "user_answer": "B"}]}).json()
    assert sub["correct"] == 1
    rep = client.get(f"/api/exams/attempts/{a['id']}/report").json()
    assert rep["total"] == 1
    hist = client.get("/api/exams/attempts").json()
    assert len(hist) >= 1


def test_wrong_auto_and_sm2(client):
    q = client.post("/api/questions", json={
        "qtype": "choice", "subject": 1, "stem": "测试错题：地球是方的？",
        "options": ["A. 对", "B. 不对"], "answer": "B", "analysis": "",
        "difficulty": 1, "source_type": "self", "knowledge_ids": []}).json()
    p = client.post("/api/exams/papers", json={"question_ids": [q["id"]]}).json()
    a = client.post("/api/exams/attempts", json={"paper_id": p["id"], "mode": "mock"}).json()
    client.post(f"/api/exams/attempts/{a['id']}/submit", json={
        "answers": [{"question_id": q["id"], "user_answer": "A"}]})
    wl = client.get("/api/wrong/queue").json()
    w = next(w for w in wl if w["question_id"] == q["id"])
    client.put(f"/api/wrong/{w['id']}", json={"error_type": "知识性错误", "reflection": "基础概念"})
    r = client.post(f"/api/wrong/{w['id']}/review", json={"quality": 5}).json()
    assert r["status"] in ("reviewing", "mastered")


def test_ai_offline(client):
    st = client.get("/api/ai/status").json()
    assert "available" in st
    r = client.post("/api/ai/grade-essay", json={"attempt_id": 1}).json()
    assert r["available"] is False


def test_practice_check(client):
    q = client.post("/api/questions", json={
        "qtype": "choice", "subject": 1, "stem": "练习模式测试题：2+2=?",
        "options": ["A. 3", "B. 4", "C. 5"], "answer": "B", "analysis": "2+2=4",
        "difficulty": 1, "source_type": "self", "knowledge_ids": []}).json()
    ok = client.post("/api/questions/check", json={
        "question_id": q["id"], "user_answer": "B"}).json()
    assert ok["is_correct"] is True and ok["correct_answer"] == "B" and ok["analysis"]
    bad = client.post("/api/questions/check", json={
        "question_id": q["id"], "user_answer": "A"}).json()
    assert bad["is_correct"] is False
    wl = client.get("/api/wrong/queue").json()
    assert any(w["question_id"] == q["id"] for w in wl)


def test_import_json(client):
    r = client.post("/api/import/json", json={"questions": [{
        "qtype": "choice", "subject": 1, "stem": "导入测试题", "options": ["A", "B"],
        "answer": "A", "analysis": "", "difficulty": 1, "source_type": "self", "knowledge_ids": []}]})
    assert r.status_code == 200
    assert r.json()["imported"] == 1


def test_plans_generate(client):
    r = client.post("/api/plans/generate", json={"exam_date": "2099-01-01"})
    assert r.status_code == 200
    assert r.json()["created"] == 4
