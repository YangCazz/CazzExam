# data / 备考资料

面向**软考高级·系统架构设计师**的大纲与练习题库，已整理为后端可直接导出的格式。

本目录是**题库内容的唯一权威源**（`data/`），承载自产题与经许可/授权外部来源的题目；`backend/scripts/seed_content.py` 已退役题目部分，只保留知识树与关系作兜底。

## 目录结构

```
data/
├── README.md                                      本说明
├── import_materials.py                            幂等灌库脚本（唯一入口）
├── syllabus/
│   └── architecture-syllabus.json                 最新考纲 → knowledge_points 树（136 节点）
├── questions/
│   └── architecture-questions.json                自产练习题库 → questions 表（102 题）
├── materials/                                     外部来源（经 normalize.py / cards.py 解析的 NIF）
│   └── <source_id>/
│       ├── questions.nif.json                     该来源的题目（NIF 格式）
│       ├── cards.nif.json                         该来源的知识点速查卡（NIF 格式，见下文）
│       └── ATTRIBUTION.md                         来源与署名
└── sources/                                       多来源吸收的基础设施
    ├── catalog.json                               外部来源索引（许可/结构/吸收策略）
    ├── normalize.py                               许可门控的标准化解析器（题目）
    ├── cards.py                                   许可门控的速查卡解析器（mind-maps → card）
    └── README.md                                  多来源 schema + 导入策略说明
```

## 来源与依据

- **考纲**：中国计算机技术职业资格网《系统架构设计师考试说明》([ruankao.org.cn](https://www.ruankao.org.cn/article/content/bkzn/03_03.html))，即 2022 年审定的**第二版考试大纲**；知识范围参照《系统架构设计师教程（第 2 版）》各章。已解析为 `syllabus/architecture-syllabus.json` 的 136 节点代码树。
- **自产题（`questions/architecture-questions.json`，`source_type:"self"`）**：依据考纲知识范围与历年真题（2009—2024）**真实题型与难度原创整理**，覆盖综合知识（91 道单选）/案例分析（5 道）/论文（6 道）。这部分也是我手工编写的原题，不冒充真题原文。
- **外部来源（`materials/`，`source_type:"self"/"real"`）**：来自开源备考仓库（见 `sources/catalog.json`）。经授权/许可的来源由 `sources/normalize.py` 解析成 NIF 后写入 `materials/<id>/`，保留 `source` 溯源字段。

## 关于「历年真题」的重要说明

软考真题的完整卷面属于受版权保护的材料，散落在各付费/分享渠道；我**没有**把任何一份真题卷面逐字照搬进仓库。

- `questions/architecture-questions.json` 全部是依据官方大纲知识范围、按真题题型与难度**原创**的原题，标注 `source_type:"self"`。
- `materials/` 里的外部真题由各开源仓库解析而来，且受其**许可/授权门控**约束（见 `sources/README.md` 的 `provenance_policy`）。我是在判断来源可导入后才落盘的，并保留「来源 + 署名」（`ATTRIBUTION.md`）以便追溯。每一题都带了 `source.repo / source.file / source.license` 溯源，不做无出处搬运。

## 知识点速查卡（mind-maps → card）

部分外部来源仓库自带高价值的 Mermaid 思维导图（本仓库引用的 `peterGuy326` 下 `mind-maps/`），经 `source/cards.py` 解析成**结构化速查卡**，挂到具体的 `knowledge_points` 上，供前端在「架构师能力星图」的详情面板里速览。**内容仅自用**（`authorized_for_self_use`），不对外分发，每张卡保留 `source` 溯源 + 仓库级 `ATTRIBUTION.md`。

数据流向（单向，无回写）：

```
ref/<repo>/mind-maps/*.md               本地 `ref/` 已 gitignore，只做源
  → data/sources/cards.py              解析器（复用 catalog 授权门控 + 脑图→块）
  → data/materials/<id>/cards.nif.json 提交产物（含 source 溯源）
  → data/import_materials.py #seed_cards()  按 code 幂等覆盖
  → knowledge_points.card              只读 TEXT（JSON），不入 PUT 白名单
  → GET /api/knowledge/points/{kpid}   返回解析后的 card 对象
  → frontend .../KnowledgeCard.vue     渲染（mindmap 树 / graph 边 / 表格 / 口诀 / 纯文本）
```

`card` 是一张 JSON 对象，字段：`{title, file, blocks, source, skip_on_import, knowledge_codes}`，`blocks` 按类型混排：

| `type` | 内容 | 渲染 |
|---|---|---|
| `mindmap` | `root:{text,children[]}` 递归树 | 可折叠 `<details>` 树 |
| `graph` | `nodes[]` + `edges[]`（`from/to/rel/label/from_label/to_label`） | 紧凑边行 `from —(label)→ to`（窄面板不画图） |
| `table` | `headers[]` + `rows[][]` | `<table>` |
| `mnemonic` | `items:[{term,text}]` 速记口诀 | `<dl>` |
| `text` | `content` 纯文本 | `<pre>` |

### 脑图 → 知识点 code 映射

`00-overall.md`（整卷复习总览，无离散 code、唯一内容是 `quadrantChart`）标为 `knowledge_codes:[]` + `skip_on_import:true`，放入产物但**不挂点**；其余 9 张各挂 1 个 code：

| 文件 | code | 考纲名称 |
|---|---|---|
| architecture-styles.md | 3.1 | 架构风格与复用 |
| database.md | 1.3 | 数据库系统 |
| design-patterns.md | 2.3.2 | 设计模式 |
| microservice.md | 3.4 | 微服务与分布式架构 |
| project-management.md | 2.5 | 项目管理 |
| quality-attributes.md | 3.2 | 质量属性 |
| security.md | 5.1 | 网络安全技术 |
| uml.md | 2.3.1 | UML 建模 |
| big-data.md | 3.8 | 大数据架构 |

用法（与题目同款门控）：

```bash
tools/python/python.exe data/sources/cards.py peterGuy326 --dry-run              # 试跑，只打印统计
tools/python/python.exe data/sources/cards.py peterGuy326 --authorized --out-into data/materials/peterGuy326/
tools/python/python.exe data/import_materials.py                                  # 幂等灌入 card 列
```

## 与后端表结构的对应

- `syllabus.json` 的 `knowledge` 数组：字段 `{parent_code, code, name, description, subject}`，种入 `knowledge_points`（code 去重，父先于子）。
- `questions.json` / `*.nif.json` 的 `questions` 数组：字段 `{qtype, subject, stem, options, answer, analysis, difficulty, source_type, source_year, knowledge_codes, items, source?}`，其中 `knowledge_codes` 指向 `syllabus.json` 的 code，加载时被解析为 `knowledge_points.id` 写入 `question_knowledge`；`items`（case 子问 / essay 提纲）写入 `question_items`；`source`（仅 NIF 有）为溯源对象。

`qtype`：`choice` / `case` / `essay`。`subject`：`1` 综合知识 / `2` 案例分析 / `3` 论文。

## 导入

在仓库根目录，用本项目的解释器运行（**唯一入口**，一次灌入自产题 + 外部来源）：

```bash
tools/python/python.exe data/import_materials.py
```

幂等：知识点按 `code`、题目按 `stem` 去重，重复执行不会产生重复数据。输出：知识树合计、关系数、自产题新增数、各外部来源新增数。

> 历史遗留：旧版 `backend/scripts/seed_content.py` 曾硬编码题目，与 `data/questions/` 构成双源，导致 case/essay 主题重复。现已将其中独有 44 道单选题合并进 `data/questions/`（102 题），`seed_content.py` 只保留知识树与关系。以后题库唯一定义在 `data/` 下。

## 接新来源

1. `git clone --depth 1 <repo> ref/<name>`（`ref/` 已 gitignore，只做本地参考）。
2. 在 `sources/catalog.json` 追加一条，写清 `license` 与实际内容结构、判断 `provenance_policy`。
3. 在 `sources/normalize.py` 的 `PARSERS` 里加一个 `parse_<source_id>` 适配器。
4. 对 `importable`（或已授权 `needs_permission` + `--authorized`）来源执行：
   `python data/sources/normalize.py <source_id> --out-into data/materials/<source_id>/`。
5. 再跑一次 `import_materials.py` 导入。

详细 schema 与许可策略见 `data/sources/README.md`。
