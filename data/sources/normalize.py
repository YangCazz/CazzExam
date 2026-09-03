# -*- coding: utf-8 -*-
"""
多来源素材标准化解析器：把外部仓库的 markdown 题目解析成 NIF，并按许可门控是否落盘。

策略：
- 只有 catalog.json 中 provenance_policy == "importable" 的来源才会被默认写入 data/materials/<id>/。
- 对 needs_permission 来源：默认跳过；只有显式传 --authorized <id>（表示已获作者授权）才准许。
- --dry-run：只解析并打印统计/样本到 stdout，不写任何文件（可用在无许可来源上验证解析逻辑，不搬运内容）。

用法（供已验证授权的来源）：
    python data/sources/normalize.py peterGuy326 --authorized --out-into data/materials/peterGuy326/
校验解析（不落盘）：
    python data/sources/normalize.py peterGuy326 --dry-run
"""
import os, re, json, argparse, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 终端避免 GBK 编码崩溃
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG = os.path.join(REPO, "data", "sources", "catalog.json")

# exam-bank 文件名 -> knowledge code（粗略映射；颗粒度可按需细化）
EXAM_BANK_KP = {
    "01-computer-systems": ["1"], "02-os-concepts": ["1.2"], "03-database": ["1.3"],
    "04-networking": ["1.4"], "05-uml": ["2.3.1"], "06-ip-and-standards": ["5.3"],
    "07-software-engineering": ["2"], "08-project-management": ["2.5"],
    "09-software-metrics": ["2.4"], "10-architecture-styles": ["3.1"],
    "11-quality-attributes": ["3.2"], "12-atam-evaluation": ["3.3"],
    "13-design-patterns": ["2.3.2"], "14-absd-views": ["3.3.3"],
    "15-microservice-cloud-native": ["3.4", "3.6"], "16-middleware": ["3.7"],
    "17-distributed-transactions": ["3.4.3"], "18-cache": ["3.4", "3.2"],
    "19-big-data": ["3.8"], "20-reliability": ["5.2"], "21-security": ["5.1"],
    "22-embedded": ["1.5"], "23-english-reading": ["6"],
    "24-devops-serverless": ["3.6", "2.1.2"], "25-enterprise-integration": ["3.5.1"],
    "26-soa-evolution": ["3.5", "3.4"],
}


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def _repo_blob(base, file):
    return f"{base}/blob/main/{file}"


def _clean(s):
    """去掉 markdown/符号噪音，让选项、答案、解析可被稳定匹配。"""
    s = re.sub(r"[✅❌☑☒※✔✘]", "", s)
    for tok in ("**", "`", "*", "__", "【题干】", "#", "-"):
        s = s.replace(tok, "")
    return s


def _nif_block(block_text, kp, source, source_year, source_type):
    """把清洗后的一块题目解析成 NIF。兼容 exam-bank 与 comprehensive-by-year 两种排版。"""
    cleaned = _clean(block_text)
    # --- 答案：容忍 "**答案**：X"、"答案：X"、"**答案**：X**" ---
    ans_m = re.search(r"答案\s*[：:]\s*([A-D])", cleaned)
    answer = ans_m.group(1) if ans_m else ""
    # --- 解析 ---
    ana_m = re.search(r"解析\s*[：:]\s*(.+)", cleaned, flags=re.S)
    analysis = _clean(ana_m.group(1)).strip() if ana_m else ""
    # --- 选项区：答案之前的所有文本 ---
    region = cleaned.split("答案")[0]
    markers = list(re.finditer(r"(?:^|\s{2,})([A-D])\s*[\.、\)]\s*", region, flags=re.M))
    opts = []
    for i, m in enumerate(markers):
        start, end_m = m.end(), (markers[i + 1].start() if i + 1 < len(markers) else len(region))
        text = re.sub(r"\s{2,}", " ", region[start:end_m]).strip()
        if text:
            opts.append(f"{m.group(1)}. {text}")
    # --- 题干：第一个选项标记之前（或整段）---
    stem = region[: markers[0].start()].strip() if markers else region.strip()
    stem = re.sub(r"\s{2,}", " ", stem).strip()
    return {
        "qtype": "choice", "subject": 1, "stem": stem, "options": opts, "answer": answer,
        "analysis": analysis, "difficulty": 3, "source_year": source_year,
        "source_type": source_type, "knowledge_codes": kp, "items": [],
        "source": {"repo": source["name"], "license": source["license"],
                   "file": source.get("rel_file", ""), "ref": stem[:24],
                   "url": source.get("url", "")},
    }


def parse_exam_bank(path, source):
    """exam-bank/*.md -> NIF 列表。格式：# 主题·N 题 / ### N. 题干 / 选项(✅ 标正确) / **答案**：X / **解析**：…"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"^###\s+\d+\.\s*", text, flags=re.M)
    theme = os.path.splitext(os.path.basename(path))[0]
    kp = EXAM_BANK_KP.get(theme, ["3"])
    rel = os.path.relpath(path, source["clone_dir"]).replace(os.sep, "/")
    src = {**source, "rel_file": rel, "url": _repo_blob(source["url"], rel)}
    out = []
    for block in blocks[1:]:
        if not block.strip():
            continue
        out.append(_nif_block(block, kp, src, None, "self"))
    return out


def parse_comprehensive(path, source):
    """past-papers/comprehensive-by-year/<year>.md -> NIF 列表。含 §N.M 知识标签与年份。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    year_m = re.search(r"#\s*(20\d{2})\s*年", text)
    year = int(year_m.group(1)) if year_m else None
    rel = os.path.relpath(path, source["clone_dir"]).replace(os.sep, "/")
    src = {**source, "rel_file": rel, "url": _repo_blob(source["url"], rel)}
    blocks = re.split(r"^###\s+\d+\.\s*【题干】\s*", text, flags=re.M)
    out = []
    for block in blocks[1:]:
        if not block.strip():
            continue
        kp = [section_map.get(m.group(1), "3") for m in re.finditer(r"§(\d+)", block)]
        kp = sorted(set(kp)) or ["3"]
        out.append(_nif_block(block, kp, src, year, "real"))
    return out


SECTION_MAP = {
    "1": "1", "2": "2.7", "3": "5.1", "4": "2", "5": "1.3", "6": "3", "7": "3.2",
    "8": "5.2", "9": "2.9", "10": "3.11", "11": "5.3", "12": "4", "13": "6",
}
section_map = SECTION_MAP  # 供上面函数引用


def file_ref(source, path):
    rel = os.path.relpath(path, source["clone_dir"]).replace(os.sep, "/")
    return rel


PARSERS = {
    "peterGuy326": lambda s, base: collect_md(s, base),
}


def collect_md(source, clone):
    """扫描 peterGuy326 的结构：exam-bank/ 与 past-papers/comprehensive-by-year/。"""
    items = []
    for sub in ["exam-bank", os.path.join("past-papers", "comprehensive-by-year")]:
        d = os.path.join(clone, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".md") and fn == "README.md":
                continue
            p = os.path.join(d, fn)
            try:
                if sub == "exam-bank":
                    items += parse_exam_bank(p, source)
                else:
                    items += parse_comprehensive(p, source)
            except Exception as e:
                print("  parse err", fn, e)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_id")
    ap.add_argument("--out-into", help="NIF 输出目录（按源生成 material/attribution）")
    ap.add_argument("--authorized", action="store_true", help="声明已获作者授权，允许写入需授权来源")
    ap.add_argument("--dry-run", action="store_true", help="只解析打印，不写任何文件")
    args = ap.parse_args()
    catalog = load_catalog()
    src = next((s for s in catalog["sources"] if s["id"] == args.source_id), None)
    if not src:
        print("catalog 中无此来源 id:", args.source_id)
        sys.exit(1)
    allowed = src["provenance_policy"] == "importable" or (args.authorized and src["provenance_policy"] == "needs_permission")
    clone = os.path.join(REPO, src["clone_dir"])
    items = PARSERS[src["id"]](src, clone) if src["id"] in PARSERS else []
    print(f"[{src['id']}] 解析出 {len(items)} 条 NIF；policy={src['provenance_policy']}")

    if args.dry_run:
        for it in items[:3]:
            print("  样本:", it["qtype"], it["stem"][:30], "| 答案", it["answer"], "| 知识", it["knowledge_codes"])
        print("  (dry-run：未写文件)")
        return

    if not allowed:
        print("  [SKIP] 未授权：provenance_policy=", src["provenance_policy"],
              "，默认拒绝写入。若要导入需先获作者授权，再用 --authorized。")
        sys.exit(2)
    out = args.out_into or os.path.join(REPO, os.path.dirname(src["clone_dir"]).replace("ref", "data/materials"), src["id"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "questions.nif.json"), "w", encoding="utf-8") as f:
        json.dump({"source": src["id"], "count": len(items), "questions": items}, f,
                  ensure_ascii=False, indent=1)
    att = os.path.join(out, "ATTRIBUTION.md")
    with open(att, "w", encoding="utf-8") as f:
        f.write(f"# 来源与署名\n# 仓库: {src['name']} ({src['url']})\n# 许可: {src['license']}\n\n"
                f"本目录内容由 {src['name']} 解析而来，保留其原始版权与署名；如需二次分发请遵循其许可（当前 {src['license']}）。\n")
    print("  [OK] 已写入:", os.path.join(out, "questions.nif.json"))


if __name__ == "__main__":
    main()
