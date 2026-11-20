"""Read-only HTTP API for a small, versioned concept library."""
from contextlib import asynccontextmanager, closing
import json
import sqlite3
from threading import Lock
import unicodedata

from fastapi import FastAPI, HTTPException, Query

from content import CONCEPTS, MAPPINGS, QUALIFICATIONS, RELATIONS, SOURCE_LABEL, VERSION

SCHEMA = """
CREATE TABLE concept (
    id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    aliases TEXT NOT NULL,
    sections TEXT NOT NULL
);
CREATE TABLE qualification (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE mapping (
    concept_id TEXT REFERENCES concept(id) NOT NULL,
    qualification_id TEXT REFERENCES qualification(id) NOT NULL,
    label TEXT NOT NULL,
    PRIMARY KEY (concept_id, qualification_id)
);
CREATE TABLE relation (
    source_id TEXT REFERENCES concept(id) NOT NULL,
    target_id TEXT REFERENCES concept(id) NOT NULL,
    kind TEXT NOT NULL,
    reason TEXT NOT NULL,
    PRIMARY KEY (source_id, target_id),
    CHECK (source_id <> target_id)
);
"""


def populate(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    headings = ("核心解释", "实际例子", "边界与取舍")
    with conn:
        conn.executemany(
            "INSERT INTO concept VALUES (?, ?, ?, ?, ?, ?)",
            [
                (cid, slug, title, summary, json.dumps(aliases), json.dumps([
                    {"heading": heading, "body": body}
                    for heading, body in zip(headings, paragraphs, strict=True)
                ]))
                for cid, slug, title, summary, aliases, paragraphs in CONCEPTS
            ],
        )
        conn.executemany("INSERT INTO qualification VALUES (?, ?)", QUALIFICATIONS.items())
        conn.executemany("INSERT INTO mapping VALUES (?, ?, ?)", MAPPINGS)
        conn.executemany("INSERT INTO relation VALUES (?, ?, ?, ?)", RELATIONS)
    conn.execute("PRAGMA query_only = ON")


def normalized(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def match(row, query):
    if not query:
        return 0, None
    title = normalized(row["title"])
    aliases = list(map(normalized, json.loads(row["aliases"])))
    if query == title:
        return 100, "标题完全匹配"
    if query in aliases:
        return 90, "别名完全匹配"
    if query in title:
        return 80, "标题包含关键词"
    if any(query in alias for alias in aliases):
        return 70, "别名包含关键词"
    # Questions such as “为什么要做服务拆分？” find their explicit terms.
    # Avoid matching ASCII inside longer words, e.g. ACID in "acidity".
    import re
    def mentioned(term):
        if term.isascii():
            return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", query)
        return len(term) >= 2 and term in query

    if mentioned(title):
        return 60, "问题中包含概念标题"
    if any(mentioned(alias) for alias in aliases):
        return 50, "问题中包含概念别名"
    if query in normalized(row["summary"]):
        return 40, "摘要包含关键词"
    return -1, None


def card(row, reason=None):
    return {
        "id": row["id"], "slug": row["slug"], "title": row["title"],
        "summary": row["summary"], "aliases": json.loads(row["aliases"]),
        "match_reason": reason,
    }


def create_app():
    # One disposable database per application lifecycle. It never opens an
    # on-disk database (old or new). Requests are reads after startup.
    @asynccontextmanager
    async def lifespan(application):
        with closing(sqlite3.connect(":memory:", check_same_thread=False)) as conn:
            conn.row_factory = sqlite3.Row
            populate(conn)
            application.state.db = conn
            application.state.db_lock = Lock()
            yield

    application = FastAPI(title="CazzExam Next API", version=VERSION, lifespan=lifespan)

    def read(sql, params=()):
        with application.state.db_lock:
            return application.state.db.execute(sql, params).fetchall()

    @application.get("/api/v1/qualifications")
    def qualifications():
        rows = read("""
            SELECT q.*, EXISTS(SELECT 1 FROM mapping m WHERE m.qualification_id=q.id) AS has_content
            FROM qualification q ORDER BY q.rowid
        """)
        return {"items": [{**dict(row), "has_content": bool(row["has_content"])} for row in rows],
                "content_version": VERSION}

    @application.get("/api/v1/concepts")
    def concepts(q: str = Query(default="", max_length=120),
                 qualification: str | None = Query(default=None, max_length=40)):
        if qualification is not None and qualification not in QUALIFICATIONS:
            raise HTTPException(422, "未知的考试视角")
        if qualification is not None:
            rows = read("""
                SELECT c.* FROM concept c JOIN mapping m ON c.id=m.concept_id
                WHERE m.qualification_id=? ORDER BY c.id
            """, (qualification,))
        else:
            rows = read("SELECT * FROM concept ORDER BY id")
        query = normalized(q)
        ranked = []
        for row in rows:
            score, reason = match(row, query)
            if score >= 0:
                ranked.append((score, card(row, reason)))
        ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
        return {"items": [item for _, item in ranked], "content_version": VERSION}

    @application.get("/api/v1/concepts/{slug}")
    def concept(slug: str):
        rows = read("SELECT * FROM concept WHERE slug=?", (slug,))
        if not rows:
            raise HTTPException(404, "没有找到这个概念")
        row, = rows
        relations = read("""
            SELECT c.slug, c.title, r.kind, r.reason
            FROM relation r JOIN concept c ON c.id=r.target_id
            WHERE r.source_id=? ORDER BY r.rowid
        """, (row["id"],))
        mappings = read("""
            SELECT qualification_id AS qualification, label
            FROM mapping WHERE concept_id=? ORDER BY rowid
        """, (row["id"],))
        return {
            **card(row), "sections": json.loads(row["sections"]),
            "relations": [dict(item) for item in relations],
            "mappings": [{**dict(item), "evidence_status": "editorial_topic", "source_url": None}
                         for item in mappings],
            "content_version": VERSION, "source_label": SOURCE_LABEL,
        }
    return application


app = create_app()
