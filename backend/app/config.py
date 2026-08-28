from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    app_name = "软考架构师备考系统"
    db_path = DATA_DIR / "study.db"
    ai_base_url = ""   # OpenAI 兼容 API 地址（如 DeepSeek/通义），留空则 AI 能力降级关闭
    ai_api_key = ""
    ai_model = ""
    cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]


settings = Settings()
