# CazzExam Next

一个从问题出发、顺着概念关系学下去的软考备考工作台。**考试是可切换的阅读视角，不是每天要完成的任务。**

这是 `dev/cazzexam-next` 分支的运行说明。旧版仍在 [`master`](https://github.com/YangCazz/CazzExam/tree/master)；试卷来源与缺口独立维护在 [题源核验分支](https://github.com/YangCazz/CazzExam/tree/docs/question-bank-audit)。新版不会读取或迁移旧版学习数据库。

## 现在能用什么

| 能力 | 状态 |
| --- | --- |
| 探索首页、搜索、概念阅读、关联跳转 | 已实现首个流程。可试「拆分」「ACID」「一致性」 |
| 五类高级资格视角、知识关系浏览 | 已提供示例入口；内容为 7 个原创概念、10 条关系，不是完整或官方考纲 |
| 可选自由练习、论文与案例、个人笔记、收藏 | 后续里程碑，不在本次实现范围 |
| 历年真题、考纲全量、考频趋势 | 不随本版分发；尚未核实的材料不参与计分 |
| 正式部署、旧版迁移 | 未进行 |

沿用浅底、现代蓝紫风，首页不放待办、打卡、倒计时或强制诊断。桌面和手机使用同一套页面，手机优先阅读，关联概念以可触控列表呈现。详见[设计基线](docs/cazzexam-next/product-architecture-ui.md)与[验收和路线图](docs/cazzexam-next/release-acceptance.md)。

## 本地启动

需要 Python 3.12、Node.js 22.12 或以上和 npm。切换到 `dev/cazzexam-next` 后，用两个终端分别启动。

**终端 1：API（端口 8010）**

```bash
cd next/api
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8010
```

Windows PowerShell 把激活命令换成 `.\.venv\Scripts\Activate.ps1`；如果不激活，也可以用 `.\.venv\Scripts\python.exe` 运行后两条命令。

**终端 2：Web（端口 5174）**

```bash
cd next/web
npm ci
npm run dev
```

打开 `http://127.0.0.1:5174`。开发服务器会把 API 请求转给 8010。若页面提示读取失败，先检查第一个终端是否仍在运行，再点重试。

## 架构与数据

```text
next/web/           Vue + TypeScript + Vite；探索、阅读、资格筛选与关系浏览
next/api/           FastAPI；知识查询、资格和原始内容导入
docs/cazzexam-next/ 产品、架构、跨端 UI 基线与验收
frontend/           旧版前端，未迁移
backend/            旧版后端，未迁移
data/               旧版来源与导入流程，Next 不读取
```

新版用版本化的原创内容种子启动独立的**内存 SQLite**，每次启动重建，提供只读查询；这一阶段没有账号、写入、跨设备同步或旧库迁移。概念与关联使用独立实体，同一概念可映射到不同资格。后续把用户数据、题源审核、内容许可和考纲版本分开建模，不让导航界面或搜索结果暗示尚未核实的考频。

## 验证

在 API 已激活的虚拟环境中执行 `cd next/api` 后，运行 `python -m unittest -v`。在 `next/web` 中运行：

```bash
npm ci
npm run test:unit
npm run build
```

此前已通过 5 项 API 测试、9 项 Vue 组件测试、TypeScript 类型检查和 Vite 构建，并验证过实际 HTTP 接口。2026-11-23，[GitHub Actions 的 Chromium 测试](https://github.com/YangCazz/CazzExam/actions/runs/45100349303)在提交 `46d3c8c` 上**实际执行并通过全部 10 项**，覆盖 1440、390、320 px 下的首页、中文搜索、概念阅读和返回恢复筛选，并包含 390 px 模拟触控用例。真机中文输入法和视觉还原仍未验收，未部署。

本地复现：保持 API 运行、关闭手动启动的 Web 服务，然后在 `next/web` 执行 `npx playwright install chromium` 和 `npm test`。详见[验证记录](next/VERIFICATION.md)。

## 内容、版本与提交

公开提交仅包含原创样例、可公开的索引、规则和可授权内容。公开可阅读不等于有权再分发；缺项、冲突或权利不明的题不计分。项目代码许可证见 [LICENSE](LICENSE)，不扩展到任何第三方资料。可发布内容逐批提交并验证远端 SHA，避免云电脑是唯一副本。
