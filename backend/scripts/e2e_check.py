import sys, os, json, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

BASE = "http://127.0.0.1:8000"


def api(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def main():
    results = []

    def check(name, fn):
        try:
            fn()
            results.append((name, True))
            print("PASS", name)
        except Exception as e:
            results.append((name, False))
            print("FAIL", name, "-", e)

    def t_health():
        assert api("/api/health")["status"] == "ok"

    def t_knowledge():
        tr = api("/api/knowledge/tree")
        gr = api("/api/knowledge/graph")
        assert len(tr) >= 50, "knowledge nodes < 50"
        assert len(gr["links"]) >= 20, "graph links < 20"

    def t_bank():
        qs = api("/api/questions?limit=500")
        ex = api("/api/questions/export")
        assert len(qs) >= 70 and ex["count"] == len(qs)

    def t_exam():
        p = api("/api/exams/papers", "POST", {"template_id": 1})
        pp = api("/api/exams/papers/" + str(p["id"]))
        assert len(pp["questions"]) > 0 and pp["duration_min"] > 0
        a = api("/api/exams/attempts", "POST", {"paper_id": p["id"], "mode": "mock"})
        ex = {q["id"]: q for q in api("/api/questions/export")["questions"]}
        answers = []
        for qq in pp["questions"][:5]:
            q = ex.get(qq["id"])
            ans = q["answer"] if q and q["qtype"] == "choice" else ""
            answers.append({"question_id": qq["id"], "user_answer": ans or ""})
        sub = api(f"/api/exams/attempts/{a['id']}/submit", "POST", {"answers": answers})
        rep = api(f"/api/exams/attempts/{a['id']}/report")
        assert sub["total"] == 5 and rep["attempt_id"] == a["id"]

    def t_wrong():
        wq = api("/api/wrong/queue")
        if wq:
            w = wq[0]
            api(f"/api/wrong/{w['id']}/review", "POST", {"quality": 3})
            api(f"/api/wrong/{w['id']}", "PUT", {"error_type": "e2e"})

    def t_stats():
        assert len(api("/api/stats/trend")) == 14
        assert isinstance(api("/api/stats/error-dist"), list)
        assert len(api("/api/stats/knowledge")) >= 50

    def t_plans():
        td = api("/api/plans/today")
        assert "due_reviews" in td and "weak_kps" in td

    def t_ai():
        st = api("/api/ai/status")
        assert "available" in st

    def t_import():
        r = api("/api/import/json", "POST", {"questions": [{
            "qtype": "choice", "subject": 1, "stem": "E2E 测试题(可删除)", "options": ["A", "B"],
            "answer": "A", "analysis": "", "difficulty": 1, "source_type": "self", "knowledge_ids": []}]})
        assert r["imported"] == 1

    for n, f in [("health", t_health), ("knowledge", t_knowledge), ("bank", t_bank),
                 ("exam", t_exam), ("wrong", t_wrong), ("stats", t_stats),
                 ("plans", t_plans), ("ai", t_ai), ("import", t_import)]:
        check(n, f)
    ok = all(x[1] for x in results)
    print("== E2E:", "ALL PASS (" + str(len(results)) + "/" + str(len(results)) + ")" if ok
          else f"{sum(1 for _, b in results if b)}/{len(results)} PASS ==")


if __name__ == "__main__":
    main()
