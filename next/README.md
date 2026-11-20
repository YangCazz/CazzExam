# CazzExam Next · 原创知识探索首片

独立于旧版的探索、词法搜索、概念阅读、解释型关系与考试视角。无任务、倒计时、打卡、账号或部署。旧 `frontend`、`backend`、数据库和题库未改动。

## 本地运行

Python 3.12，Node 22.12+（本次 Node 24）。两个终端分别启动：

```sh
cd next/api
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8010
```

Windows 激活使用 `.venv\Scripts\Activate.ps1`。

```sh
cd next/web
npm ci
npm run dev
```

打开 http://127.0.0.1:5174 。Vite 将 `/api` 转发到 8010；只有前端进程不足以阅读内容。URL 使用哈希路由，可直接打开 `/#/concept/service-decomposition`。生产构建不是部署命令；未来静态托管需配置同源 API 转发。

## 内容和存储

7 个原创概念、10 条有理由的定向关系，版本见 API 内容包。每次启动把代码中的原创种子导入进程内 SQLite，随后只读；不读取任何磁盘学习数据库，不存个人记录。搜索可试“拆分”“ACID”“一致性”，搜索匹配原因可见，不是生成式问答。

五类高级资格均可选择。架构师和系统分析师仅含编辑标注的相关主题，其他视角当前如实为空；不代表已核验考纲或完整覆盖。同一概念 ID 跨视角复用。首版地图是可访问的概念列表及关系入口，不是可拖动图谱。收藏、笔记、练习未开放，不展示虚假保存按钮。

## 验证

```sh
cd next/api
python -m pip install -r requirements-test.txt
python -m unittest -v
# 另一个终端
cd next/web
npm run test:unit
npm run build
# API 启动后执行真实浏览器套件；首次安装受支持 Chromium
npx playwright install chromium
npm test
```

浏览器测试默认用 Playwright 的 Chromium；已有受支持浏览器可设置 `CHROMIUM_PATH`。测试会启动自己的 5174 前端，故运行前关闭已占用的前端进程，API 8010 保持开启。

本次结果与限制见 `VERIFICATION.md`。真实浏览器测试未通过前，不宣称已完成桌面、手机或像素还原验收。
