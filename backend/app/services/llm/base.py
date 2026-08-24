from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.request_count = 0
        self.fallback_count = 0
        self.is_healthy = True

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Executes prompt and returns validated JSON dict, or None on failure.
        """
        pass
