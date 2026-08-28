from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routers import knowledge, questions, exams, wrong, plans, stats, essay, import_api, ai, learning


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(knowledge.router)
app.include_router(questions.router)
app.include_router(exams.router)
app.include_router(wrong.router)
app.include_router(plans.router)
app.include_router(stats.router)
app.include_router(essay.router)
app.include_router(import_api.router)
app.include_router(ai.router)
app.include_router(learning.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
