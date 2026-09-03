# data/sources · 多来源素材组织结构

本目录定义「如何把**不同来源**的外部备考资料，结构化地吸收进本 app」。核心是：**先有许可与溯源，再谈导入**。

## 目录结构

```
data/
├── sources/
│   ├── catalog.json            外部来源索引(每个仓库的元数据/许可/内容/吸收策略)
│   ├── README.md               本说明(多来源 schema + 导入策略)
│   └── normalize.py            标准化解析器(按 catalog 许可门控)
├── syllabus/                   考纲 → knowledge_points 树(本 app 自产)
├── questions/                  题库 → questions 表(本 app 自产)
├── materials/                  (可选)按来源组织的素材
├── ref/                        外部克隆仓库(已 gitignore,不进仓库)
└── import_materials.py         灌库脚本
```

## 为什么需要"多来源 + 溯源"

外部仓库形态各异、许可各异。若不经区分直接 `git add` 或照搬进 `data/`，会造成：① 把他人版权内容带进我们公共仓库；② 来源难以追踪；③ 后续无法回填贡献/署名。因此约定：

- **`ref/` 只做本地参考**，已加入 `.gitignore`，永不提交。
- 需要进入 app 的内容，统一转换成 **NIF** 后写入 `data/`，并保留来源字段。

## 标准化中间格式（NIF）

NIF = Normalized Intermediate Format。任何来源的题目/材料，先解析成 NIF，再灌库。NIF 兼容现有 `import_json.py`/`seed_content.py` 的字段，并强化溯源：

```json
{
  "qtype": "choice",                       // choice / case / essay
  "subject": 1,                            // 1综合 2案例 3论文
  "stem": "……",
  "options": ["A", "B", "C", "D"],         // case/essay 可空
  "answer": "A",
  "analysis": "……",
  "difficulty": 3,                         // 1-5
  "source_year": null,
  "knowledge_codes": ["3.1"],              // 关联 data/syllabus/architecture-syllabus.json 的 code
  "items": [{"seq": 1, "stem": "……", "answer": "……", "score": 10}],  // case 子问 / essay 提纲
  "source": {                              // 溯源(必填)
    "repo": "PeterGuy326/senior-software-architect-review",
    "license": "none",                     // 或 MIT / Apache-2.0 …
    "file": "exam-bank/10-architecture-styles.md",
    "ref": "q1",
    "url": "https://github.com/…/blob/main/…"
  }
}
```

## 导入策略（provenance_policy）

来源的 `provenance_policy`（见 `catalog.json`）决定了能否导入：

| 值 | 含义 | 可导入? |
|---|---|---|
| `importable` | 有许可（MIT/Apache/CC-BY 等）或作者已授权 | ✅ 是 |
| `needs_permission` | 无许可但作者可联系（如 peterGuy326） | ⏸️ 先要授权 |
| `reference_only` | 无许可且形态不可结构化 | ❌ 否，仅参考 |
| `limited` | 有许可但内容版权不归仓库（如官方教材 PDF） | ❌ 否，仅参考 |

导入前，`normalize.py` 会检查源在 catalog 中是否允许；**只有允许的来源才会被解析**。对 `needs_permission` 来源，尚未授权时它只打印"跳过"，不产出导入文件。

## 追溯与署名

每一条进入 `data/` 的外部素材，其 `source` 字段都必须能回答：来自哪个仓库、哪个文件、什么许可、出处链接。MIT/CC 来源还应保留版权声明（`normalize.py` 会生成 `data/materials/<id>/ATTRIBUTION.md`）。

## 如何接一个新来源

1. `git clone --depth 1 <repo> ref/<name>`
2. 在 `catalog.json` 追加一条，写清 `license` 与实际内容结构。
3. 判断 `provenance_policy`；若需授权，先联系作者。
4. 在 `normalize.py` 的解析器 `PARSERS` 里加一个 `parse_<source_id>` 适配器，把其格式转成 NIF。
5. 仅对 `importable` 来源执行 `python data/sources/normalize.py <source_id> --out-into data/materials/<source_id>/`。
