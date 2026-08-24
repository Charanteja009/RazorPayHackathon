import time
from typing import Dict, Any, Tuple
from backend.app.services.llm.gateway import llm_gateway
from backend.app.models.db_models import ActionType

class StrategyAgent:
    """
    3. StrategyAgent
    Uses LLM reasoning over diagnosis, ML prediction, transaction amount, retry history, policy constraints.
    Returns: { "action": "...", "reason": "...", "confidence": 0.91, "requires_human_review": bool }
    Allowed actions ONLY: RETRY_PAYMENT, WAIT_AND_RETRY, SEND_PAYMENT_REMINDER, ESCALATE_TO_HUMAN, STOP.
    """
    def execute(
        self,
        transaction: Dict[str, Any],
        diagnosis: Dict[str, Any],
        prediction: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        
        system_prompt = (
            "You are a specialized Recovery Strategy AI Agent. "
            "You recommend recovery interventions for failed payments. "
            "You must ONLY choose from these 5 allowed action strings: "
            "['RETRY_PAYMENT', 'WAIT_AND_RETRY', 'SEND_PAYMENT_REMINDER', 'ESCALATE_TO_HUMAN', 'STOP']. "
            "Return JSON format with fields: action, reason, confidence (float 0 to 1), requires_human_review (bool)."
        )

        user_prompt = (
            f"Transaction Amount: ₹{transaction.get('amount')}\n"
            f"Diagnosis: {diagnosis.get('diagnosis')} - {diagnosis.get('reason')}\n"
            f"ML Recovery Probability: {prediction.get('recovery_probability')} (Threshold: {prediction.get('threshold')}, Eligible: {prediction.get('recovery_eligible')})\n"
            f"Retry Count: {transaction.get('retry_count')}\n"
            "Select best recovery strategy action."
        )

        res, provider, latency = llm_gateway.generate(user_prompt, system_prompt)

        # Validate action string
        allowed = [a.value for a in ActionType]
        action = str(res.get("action", "")).upper() if isinstance(res, dict) else ""

        if action not in allowed:
            # Safe default fallback
            if prediction.get("recovery_eligible") and transaction.get("retry_count", 0) < 3:
                action = ActionType.RETRY_PAYMENT.value
            else:
                action = ActionType.ESCALATE_TO_HUMAN.value

            res = {
                "action": action,
                "reason": "Strategy fallback applied to ensure valid action bounds.",
                "confidence": 0.85,
                "requires_human_review": (action == ActionType.ESCALATE_TO_HUMAN.value)
            }

        return res, provider, latency

strategy_agent = StrategyAgent()
