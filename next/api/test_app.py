import sqlite3
import unittest

from fastapi.testclient import TestClient

from app import create_app

PREFIX = "/api/v1"


class ContentApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.enterContext(TestClient(self.app))

    def test_explore_without_default_qualification(self):
        data = self.client.get(PREFIX + "/concepts").json()
        self.assertGreaterEqual(len(data["items"]), 7)
        self.assertTrue(data["content_version"])
        self.assertEqual(len({c["id"] for c in data["items"]}), len(data["items"]))
        self.assertTrue(all(c["match_reason"] is None for c in data["items"]))

    def test_search_exact_alias_chinese_question_and_empty(self):
        for q, slug, reason in [
            ("事务一致性", "transaction-consistency", "标题完全匹配"),
            (" ＯＵＴＢＯＸ ", "transactional-outbox", "别名完全匹配"),
            ("服务拆分后为什么会遇到事务一致性？", "service-decomposition", "问题中包含概念标题"),
            ("拆分", "service-decomposition", "标题包含关键词"),
        ]:
            with self.subTest(q=q):
                items = self.client.get(PREFIX + "/concepts", params={"q": q}).json()["items"]
                self.assertEqual(items[0]["slug"], slug)
                self.assertEqual(items[0]["match_reason"], reason)
        for q in ("xyz无匹配xyz", "%", "_", "' OR 1=1 --", "acidity"):
            with self.subTest(q=q):
                self.assertEqual(self.client.get(PREFIX + "/concepts", params={"q": q}).json()["items"], [])
        self.assertEqual(self.client.get(PREFIX + "/concepts", params={"q": "a" * 121}).status_code, 422)

    def test_directional_relation_links_resolve(self):
        first = self.client.get(PREFIX + "/concepts/service-decomposition").json()
        self.assertEqual({section["heading"] for section in first["sections"]},
                         {"核心解释", "实际例子", "边界与取舍"})
        self.assertIn("原创", first["source_label"])
        self.assertEqual(first["relations"][0]["slug"], "transaction-consistency")
        self.assertTrue(first["relations"][0]["reason"])
        second = self.client.get(PREFIX + "/concepts/" + first["relations"][0]["slug"]).json()
        self.assertNotIn(first["slug"], [r["slug"] for r in second["relations"]])
        self.assertEqual(self.client.get(PREFIX + "/concepts/does-not-exist").status_code, 404)

    def test_qualifications_filter_same_concept_with_distinct_editorial_lenses(self):
        items = self.client.get(PREFIX + "/qualifications").json()["items"]
        self.assertEqual(len(items), 5)
        for q in ("architect", "systems-analyst"):
            filtered = self.client.get(PREFIX + "/concepts",
                                       params={"qualification": q, "q": "质量属性场景"}).json()["items"]
            self.assertEqual([row["id"] for row in filtered], ["cx-007"])
        detail = self.client.get(PREFIX + "/concepts/quality-attribute-scenario").json()
        self.assertEqual(len({m["label"] for m in detail["mappings"]}), 2)
        self.assertTrue(all(m["evidence_status"] == "editorial_topic" and m["source_url"] is None
                            for m in detail["mappings"]))
        self.assertEqual(self.client.get(PREFIX + "/concepts?qualification=network-planner").json()["items"], [])
        self.assertEqual(self.client.get(PREFIX + "/concepts?qualification=unknown").status_code, 422)

    def test_separate_startups_have_isolated_read_only_databases(self):
        with TestClient(create_app()) as another:
            self.assertEqual(self.client.get(PREFIX + "/concepts").json(),
                             another.get(PREFIX + "/concepts").json())
            self.assertIsNot(self.app.state.db, another.app.state.db)
        self.assertEqual(self.app.state.db.execute("PRAGMA database_list").fetchone()["file"], "")
        self.assertEqual(self.app.state.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        with self.assertRaises(sqlite3.OperationalError):
            self.app.state.db.execute("DELETE FROM concept")


if __name__ == "__main__":
    unittest.main()
