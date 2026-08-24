import json
import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__("OpenAI")
        self.api_key = settings.OPENAI_API_KEY

    def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        self.request_count += 1
        if not self.api_key or self.api_key.startswith("sk-placeholder"):
            logger.warning("OpenAI API key not configured. Triggering fallback.")
            self.fallback_count += 1
            return None

        try:
            import urllib.request
            req_data = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                content = result['choices'][0]['message']['content']
                return json.loads(content)

        except Exception as e:
            logger.error(f"OpenAI Provider execution error: {e}")
            self.fallback_count += 1
            return None
