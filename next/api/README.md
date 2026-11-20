# CazzExam Next API

从仓库根目录进入 `next/api`。使用 Python 3.12：

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8010
```

Windows PowerShell 的虚拟环境激活命令是 `.venv\Scripts\Activate.ps1`。前端开发服务应把 `/api` 请求转发给该端口，不需要开放 CORS。

```sh
python -m pip install -r requirements-test.txt
python -m unittest -v
```

- `GET /api/v1/concepts`：探索、`q` 搜索以及 `qualification` 可选筛选。词法匹配标题、别名、摘要，对包含已知术语的提问也可返回结果；不是生成式问答或语义搜索。
- `GET /api/v1/concepts/{slug}`：阅读正文、关联方向及理由、编辑视角。
- `GET /api/v1/qualifications`：列出五个可见视角及目前是否有内容。

启动时将版本化原创种子载入进程内 SQLite，随后设为只读。不读写旧版或磁盘数据库，不使用第三方题文。所有映射均是本站编辑视角，不代表经过核对的考纲条目。首批有架构师主题及一个系统分析师对照条目，未覆盖其他视角；未知视角返回 422，已知但暂无内容则返回空列表。
