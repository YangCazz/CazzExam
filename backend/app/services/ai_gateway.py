import json
import httpx
from ..config import settings


class AIGateway:
    """OpenAI 兼容网关：未配置 key 时返回 None（离线降级）"""

    def __init__(self):
        self.base_url = settings.ai_base_url
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model

    def available(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    def chat_json(self, system: str, user: str, timeout: float = 60.0):
        if not self.available():
            return None
        try:
            with httpx.Client(timeout=timeout) as client:
                url = self.base_url.rstrip("/") + "/chat/completions"
                resp = client.post(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            return {"error": str(e)}


ai_gateway = AIGateway()
