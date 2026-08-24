import logging
from typing import Dict, Any, Optional
from backend.app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class DeterministicFallbackProvider(LLMProvider):
    def __init__(self):
        super().__init__("Deterministic Policy Rules")

    def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        self.request_count += 1
        logger.info("Executing conservative deterministic fallback (Fail-Closed safety behavior).")

        prompt_lower = prompt.lower()
        
        # Diagnosis context
        if "diagnosis" in prompt_lower or "diagnose" in prompt_lower:
            if "permanent" in prompt_lower or "expired" in prompt_lower:
                diag = "PERMANENT_DECLINE"
                rec_dir = "STOP"
            elif "insufficient" in prompt_lower or "temporary" in prompt_lower:
                diag = "TEMPORARY_FAILURE"
                rec_dir = "ESCALATE"  # Fail-closed preference over auto-retry
            else:
                diag = "UNKNOWN"
                rec_dir = "STOP"
                
            return {
                "diagnosis": diag,
                "confidence": 0.90,
                "recommended_direction": rec_dir,
                "reason": "Deterministic fallback applied following LLM unavailability (fail-closed)."
            }

        # Strategy context (Priority 1: Always fail closed to STOP or ESCALATE_TO_HUMAN when all LLMs fail)
        if "permanent" in prompt_lower or "expired" in prompt_lower:
            action = "STOP"
            reason = "Deterministic safety rule stopped action for permanent failure after LLM fallback."
        else:
            action = "ESCALATE_TO_HUMAN"
            reason = "Conservative deterministic fallback escalated action for human review after LLM provider failure."

        return {
            "action": action,
            "reason": reason,
            "confidence": 1.0,
            "requires_human_review": True
        }
