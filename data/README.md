# data / 备考资料

面向**软考高级·系统架构设计师**的大纲与练习题库,已整理为后端可直接导出的格式。

## 目录结构

```
data/
├── README.md                                      本说明
├── import_materials.py                            幂等灌库脚本
├── syllabus/
│   └── architecture-syllabus.json                 最新考纲 → knowledge_points 树
└── questions/
    └── architecture-questions.json                练习题库 → questions 表
```

## 来源与依据

- **考纲**:中国计算机技术职业资格网《系统架构设计师考试说明》([ruankao.org.cn](https://www.ruankao.org.cn/article/content/bkzn/03_03.html)),即 2022 年审定的**第二版考试大纲**;知识范围参照《系统架构设计师教程（第 2 版）》各章。
- **题库**:依据该考纲知识范围与历年真题（2009—2024）**真实题型与难度原创整理**,覆盖综合知识/案例分析/论文三科。

## 关于「历年真题」的重要说明

软考真题的完整卷面属于受版权保护的材料,散落在各付费/分享渠道;我**没有**把任何一份真题卷面逐字照搬进仓库。`architecture-questions.json` 里全部是依据官方大纲知识范围、按真题题型与难度**原创**的练习原题,因此在数据里统一标注 `source_type: "self"`,不冒充真题原文。

如果之后想接入市面上「正版真题」:转换管线已就绪,把 PDF/XLSX 走 `backend/scripts/pdf_extract.py`(PDF→逐页文本) 或 `backend/scripts/import_tool.py xlsx2json`(XLSX→JSON),再按本目录 `questions/*.json` 的同一 schema 追加即可 (注意把 `source_type` 改回 `"real"`)。

## 与后端表结构的对应

- `syllabus.json` 的 `knowledge` 数组:字段 `{parent_code, code, name, description, subject}`,与 `backend/scripts/seed_content.py` 的 `KNOWLEDGE` 同构,直接种入 `knowledge_points`(code 去重,父先于子)。
- `questions.json` 的 `questions` 数组:字段 `{qtype, subject, stem, options, answer, analysis, difficulty, source_type, source_year, knowledge_codes, items}`,其中 `knowledge_codes` 指向 `syllabus.json` 的 code,加载时被解析为 `knowledge_points.id` 写入 `question_knowledge` 关联;`items`(case/essay 的子问或写作提纲)写入 `question_items`。

`qtype`: `choice` / `case` / `essay`。`subject`: `1` 综合知识 / `2` 案例分析 / `3` 论文。

## 导入

在仓库根目录,用本项目的解释器运行:

```bash
tools/python/python.exe data/import_materials.py
```

幂等:知识点按 code、题目按 stem 去重,重复执行不会产生重复数据。输出现为知识树合计、关系数、题目新增数。
