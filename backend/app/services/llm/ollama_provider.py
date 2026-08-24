import json
import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    def __init__(self):
        super().__init__("Ollama")
        self.base_url = settings.OLLAMA_BASE_URL

    def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        self.request_count += 1
        try:
            import urllib.request
            req_data = json.dumps({
                "model": "llama3",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "format": "json",
                "stream": False
            }).encode('utf-8')

            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=3) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                content = result['message']['content']
                return json.loads(content)

        except Exception as e:
            logger.info(f"Ollama local instance unavailable: {e}. Triggering fallback.")
            self.fallback_count += 1
            return None
