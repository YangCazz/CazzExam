# -*- coding: utf-8 -*-
"""
解析 ref/senior-software-architect-review/mind-maps/*.md 的 Mermaid 脑图为结构化速查卡,
写入 data/materials/<source_id>/cards.nif.json(NIF 扩展),保留 source 溯源。

策略与门控同 data/sources/normalize.py:
- provenance_policy == "importable" 或 (--authorized and needs_permission) 才写入。
- --dry-run: 只解析打印,不写任何文件。
- 只落盘解析出的结构化 blocks,不逐字搬运整篇脑图;每张卡带 source 溯源。

用法(需对已授权来源):
    tools/python/python.exe data/sources/cards.py peterGuy326 --authorized --out-into data/materials/peterGuy326/
校验解析(不落盘):
    tools/python/python.exe data/sources/cards.py peterGuy326 --dry-run
"""
import os, re, json, argparse, sys, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 终端避免 GBK 编码崩溃
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG = os.path.join(REPO, "data", "sources", "catalog.json")

# mind-maps/*.md -> 考纲 knowledge code(已核实存在于 data/syllabus/architecture-syllabus.json)
MINDMAP_KP = {
    "architecture-styles.md": ["3.1"],
    "database.md": ["1.3"],
    "design-patterns.md": ["2.3.2"],
    "microservice.md": ["3.4"],
    "project-management.md": ["2.5"],
    "quality-attributes.md": ["3.2"],
    "security.md": ["5.1"],
    "uml.md": ["2.3.1"],
    "big-data.md": ["3.8"],
    "00-overall.md": [],  # 整卷总览,无对应离散 code,标记 skip_on_import
}

NODE_RE = re.compile(r"([A-Za-z0-9_]+)\s*(?:\[([^\]]*)\]|\{([^}]*)\}|\(\(([^)]*)\)\))")
EDGE_RE = re.compile(r"\s*([A-Za-z0-9_]+)\s*(-->|-\.->)\s*(?:\|([^|]*)\|\s*)?([A-Za-z0-9_]+)")


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def _blob_url(base, file):
    return f"{base}/blob/main/{file}"


# ---------- 块解析纯函数 ----------

def first_nonblank(s):
    for line in s.splitlines():
        if line.strip():
            return line.strip()
    return ""


def extract_fences(body):
    """返回 [(lang|None, content), ...],识别 ``` 与 ```mermaid 代码围栏。"""
    fences, lines, i = [], body.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^\s*```\s*(\S*)\s*$", lines[i])
        if m:
            lang = m.group(1) or None
            j, content = i + 1, []
            while j < len(lines) and not re.match(r"^\s*```\s*$", lines[j]):
                content.append(lines[j])
                j += 1
            fences.append((lang, "\n".join(content)))
            i = j + 1
        else:
            i += 1
    return fences


def split_sections(text):
    """返回 [(heading, body), ...];heading 为首个 ## 后的文本,section 0 的 heading 为 ''。"""
    sections, cur_head, cur_body = [], "", []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            if cur_head or cur_body:
                sections.append((cur_head, "\n".join(cur_body)))
            cur_head, cur_body = m.group(1).strip(), []
        else:
            cur_body.append(line)
    sections.append((cur_head, "\n".join(cur_body)))
    return sections


def _strip_md(s):
    return re.sub(r"\*\*|\*|`", "", s).strip()


def strip_root(text):
    """mindmap 根节点是 root((标题)),剥掉包裹只留标题。"""
    if text.startswith("root(("):
        inner = text[len("root(("):]
        if inner.endswith("))"):
            inner = inner[:-2]
        return inner
    return text


def parse_mindmap(content):
    lines = [l for l in content.splitlines()
             if l.strip() and not l.lstrip().startswith("%%")]
    if not lines or not lines[0].strip().startswith("mindmap"):
        return None
    lines = lines[1:]
    root, stack = None, []
    for line in lines:
        raw = line.rstrip("\n")
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        text = stripped.strip()
        if "\t" in raw[:indent] or not text:
            continue
        node = {"text": strip_root(text), "children": []}
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            root = node
        else:
            stack[-1][1]["children"].append(node)
        stack.append((indent, node))
    return root


def parse_graph(content):
    lines = [l for l in content.splitlines() if l.strip()]
    if not lines:
        return None
    first = lines[0].strip().split()
    if not first or first[0] != "graph":
        return None
    direction = first[1] if len(first) > 1 else "LR"
    body = "\n".join(lines[1:])
    nodes = {}
    for m in NODE_RE.finditer(body):
        nid = m.group(1)
        if nid in nodes:
            continue
        shape = "[]" if m.group(2) is not None else ("{}" if m.group(3) is not None else "(())")
        label = (m.group(2) or m.group(3) or m.group(4) or "")
        nodes[nid] = {"id": nid, "shape": shape, "label": label.replace("<br/>", "\n").strip()}
    # 去掉节点标签([…]/ {…}/((…)))后,连边的相邻 ID 才能被稳定识别(如 V -.-> PVC[PVC] -.-> PV[PV])
    stripped = NODE_RE.sub(lambda m: m.group(1), body)
    edges, seen = [], set()
    # 用「复用 to 起点」扫描,正确处理 A --> B --> C 这样的连续连边(finditer 会跳过重叠)
    pos = 0
    while pos < len(stripped):
        m = EDGE_RE.match(stripped, pos)
        if not m:
            nxt = re.search(r"[A-Za-z0-9_]+", stripped[pos:])
            if not nxt:
                break
            # 跳到下一个 ID 的起点(若已停在某个无箭头 ID 上则越过它)
            pos += nxt.end() if nxt.start() == 0 else nxt.start()
            continue
        f, rel, lab, t = m.group(1), m.group(2), (m.group(3) or ""), m.group(4)
        key = (f, t, rel, lab)
        if key not in seen:
            seen.add(key)
            edges.append({"from": f, "to": t, "rel": rel, "label": lab.strip(),
                          "from_label": nodes.get(f, {}).get("label", f),
                          "to_label": nodes.get(t, {}).get("label", t)})
        pos = m.start(4)  # 下一次从 to 起点开始,允许它作为下一个 from
    if not nodes and not edges:
        return None
    return {"type": "graph", "direction": direction, "nodes": list(nodes.values()), "edges": edges}


def is_table(body):
    return sum(1 for l in body.splitlines() if l.strip().startswith("|")) >= 2


def parse_table(body):
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        rows.append([_strip_md(c) for c in re.split(r"\s*\|\s*", line.strip("|"))])
    if len(rows) < 2:
        return None
    headers, data = rows[0], []
    for r in rows[1:]:
        if r and all(re.match(r"^:?-{2,}:?$", c.strip()) for c in r):
            continue
        if r:
            data.append(r)
    if not data:
        return None
    return {"type": "table", "headers": headers, "rows": data}


def parse_text(content):
    return {"type": "text", "content": content.strip()}


def parse_mnemonics(body):
    items = []
    for line in body.splitlines():
        m = re.match(r"^\s*[-*]\s*(?:\*\*(.+?)\*\*|(.+?))\s*[：:]\s*(.*)$", line)
        if not m:
            continue
        term = (m.group(1) or m.group(2) or "").strip()
        text = _strip_md(m.group(3) or "").strip()
        if term:
            items.append({"term": term, "text": text})
    return items


def parse_file(text):
    """把一个 .md 解析成有序 blocks:mermaid(mindmap/graph)、纯文本围栏、表格、速记口诀。"""
    blocks = []
    for heading, body in split_sections(text):
        if "速记口诀" in heading:
            mn = parse_mnemonics(body)
            if mn:
                blocks.append({"type": "mnemonic", "items": mn})
            continue
        for lang, content in extract_fences(body):
            first = first_nonblank(content)
            if first.startswith("mindmap"):
                root = parse_mindmap(content)
                if root:
                    blocks.append({"type": "mindmap", "root": root})
            elif first.startswith("graph"):
                b = parse_graph(content)
                if b:
                    blocks.append(b)
            elif lang is None and content.strip():
                # 无语言标识的围栏(如 等保五级 / 类关系强弱排序) -> 纯文本块
                blocks.append(parse_text(content))
            # quadrantChart 等未知 mermaid 类型:忽略
        if is_table(body):
            t = parse_table(body)
            if t:
                blocks.append(t)
    return blocks


def build_cards(source, clone):
    mm_dir = os.path.join(clone, "mind-maps")
    if not os.path.isdir(mm_dir):
        print("  未找到 mind-maps 目录:", mm_dir)
        return []
    cards = []
    for fn in sorted(os.listdir(mm_dir)):
        if not fn.endswith(".md") or fn == "README.md":
            continue
        p = os.path.join(mm_dir, fn)
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print("  read err", fn, e)
            continue
        blocks = parse_file(text)
        codes = MINDMAP_KP.get(fn, [])
        rel = os.path.relpath(p, source["clone_dir"]).replace(os.sep, "/")
        cards.append({
            "knowledge_codes": codes,
            "title": os.path.splitext(os.path.basename(fn))[0],
            "file": fn,
            "blocks": blocks,
            "skip_on_import": not codes,
            "source": {"repo": source["name"], "license": source["license"],
                       "file": rel, "ref": os.path.splitext(os.path.basename(fn))[0],
                       "url": _blob_url(source["url"], rel)},
        })
    return cards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_id")
    ap.add_argument("--out-into", help="NIF 输出目录(按源生成 material/attribution)")
    ap.add_argument("--authorized", action="store_true", help="声明已获作者授权")
    ap.add_argument("--dry-run", action="store_true", help="只解析打印,不写文件")
    args = ap.parse_args()
    catalog = load_catalog()
    src = next((s for s in catalog["sources"] if s["id"] == args.source_id), None)
    if not src:
        print("catalog 中无此来源 id:", args.source_id)
        sys.exit(1)
    allowed = src["provenance_policy"] == "importable" or (args.authorized and src["provenance_policy"] == "needs_permission")
    clone = os.path.join(REPO, src["clone_dir"])
    cards = build_cards(src, clone)
    total_blocks = sum(len(c["blocks"]) for c in cards)
    print(f"[{src['id']}] 解析出 {len(cards)} 张速查卡,{total_blocks} 个块;policy={src['provenance_policy']}")
    for c in cards:
        print(f"   - {c['file']}: {len(c['blocks'])} blocks; codes={c['knowledge_codes']} skip={c['skip_on_import']}")

    if args.dry_run:
        for c in cards[:1]:
            for b in c["blocks"][:3]:
                print("   样本块:", b.get("type"), (b.get("title") or b.get("root") or ""))
        print("  (dry-run: 未写文件)")
        return
    if not allowed:
        print("  [SKIP] 未授权: provenance_policy=", src["provenance_policy"],
              "，默认拒绝写入。若要导入需先获作者授权,再用 --authorized。")
        sys.exit(2)
    out = args.out_into or os.path.join(REPO, os.path.dirname(src["clone_dir"]).replace("ref", "data/materials"), src["id"])
    os.makedirs(out, exist_ok=True)
    out_path = os.path.join(out, "cards.nif.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"source": src["id"], "generated": datetime.date.today().isoformat(),
                   "origin": f"ref/{src['clone_dir']}/mind-maps/*.md",
                   "count": len(cards), "cards": cards}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "ATTRIBUTION.md"), "a", encoding="utf-8") as f:
        f.write(f"\n本目录另含 mind-maps/* 解析出的速查卡(共 {len(cards)} 张,{total_blocks} 个块),"
                f"保留来源与署名,自用授权({src.get('authorized_for_self_use')})。\n")
    print("  [OK] 已写入:", out_path, f"({len(cards)} cards, {total_blocks} blocks)")


if __name__ == "__main__":
    main()
