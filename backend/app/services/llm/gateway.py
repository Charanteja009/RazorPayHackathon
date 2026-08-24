import time
import logging
from typing import Dict, Any, Tuple
from backend.app.services.llm.openai_provider import OpenAIProvider
from backend.app.services.llm.groq_provider import GroqProvider
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.services.llm.deterministic_provider import DeterministicFallbackProvider

logger = logging.getLogger(__name__)

class LLMGateway:
    _instance = None

    def __init__(self):
        self.openai = OpenAIProvider()
        self.groq = GroqProvider()
        self.ollama = OllamaProvider()
        self.deterministic = DeterministicFallbackProvider()
        
        # Simulation toggles for Demo Scenario 4 & 5
        self.simulate_openai_failure = False
        self.simulate_all_llm_failure = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_simulation(self, openai_fail: bool = None, all_llm_fail: bool = None):
        if openai_fail is not None:
            self.simulate_openai_failure = openai_fail
        if all_llm_fail is not None:
            self.simulate_all_llm_failure = all_llm_fail

    def get_status(self) -> Dict[str, Any]:
        return {
            "providers": [
                {
                    "name": self.openai.name,
                    "healthy": not self.simulate_openai_failure and not self.simulate_all_llm_failure and bool(self.openai.api_key),
                    "status": "Unavailable (Simulated)" if (self.simulate_openai_failure or self.simulate_all_llm_failure) else ("Healthy" if self.openai.api_key else "Unavailable (No Key)"),
                    "request_count": self.openai.request_count,
                    "fallback_count": self.openai.fallback_count
                },
                {
                    "name": self.groq.name,
                    "healthy": not self.simulate_all_llm_failure and bool(self.groq.api_key),
                    "status": "Unavailable (Simulated)" if self.simulate_all_llm_failure else ("Healthy" if self.groq.api_key else "Unavailable (No Key)"),
                    "request_count": self.groq.request_count,
                    "fallback_count": self.groq.fallback_count
                },
                {
                    "name": self.ollama.name,
                    "healthy": not self.simulate_all_llm_failure,
                    "status": "Unavailable (Simulated)" if self.simulate_all_llm_failure else "Fallback / Local",
                    "request_count": self.ollama.request_count,
                    "fallback_count": self.ollama.fallback_count
                },
                {
                    "name": self.deterministic.name,
                    "healthy": True,
                    "status": "Active (Deterministic Guardrail)",
                    "request_count": self.deterministic.request_count,
                    "fallback_count": 0
                }
            ],
            "simulation_state": {
                "simulate_openai_failure": self.simulate_openai_failure,
                "simulate_all_llm_failure": self.simulate_all_llm_failure
            }
        }

    def generate(self, prompt: str, system_prompt: str) -> Tuple[Dict[str, Any], str, float]:
        """
        Executes fallback chain: OpenAI -> Groq -> Ollama -> Deterministic Fallback.
        Returns (result_dict, provider_used, latency_ms).
        """
        start_time = time.time()

        # Step 1: Check OpenAI if simulation permits and provider is available
        if not self.simulate_openai_failure and not self.simulate_all_llm_failure:
            result = self.openai.generate_json(prompt, system_prompt)
            if result:
                latency = round((time.time() - start_time) * 1000, 2)
                return result, self.openai.name, latency

        # Step 2: Check Groq if simulation permits
        if not self.simulate_all_llm_failure:
            result = self.groq.generate_json(prompt, system_prompt)
            if result:
                latency = round((time.time() - start_time) * 1000, 2)
                return result, self.groq.name, latency

        # Step 3: Check Ollama if simulation permits
        if not self.simulate_all_llm_failure:
            result = self.ollama.generate_json(prompt, system_prompt)
            if result:
                latency = round((time.time() - start_time) * 1000, 2)
                return result, self.ollama.name, latency

        # Step 4: Deterministic Policy Fallback
        result = self.deterministic.generate_json(prompt, system_prompt)
        latency = round((time.time() - start_time) * 1000, 2)
        return result, self.deterministic.name, latency

llm_gateway = LLMGateway.get_instance()
