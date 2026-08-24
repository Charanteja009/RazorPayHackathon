import time
from typing import Dict, Any, Tuple
from backend.app.services.llm.gateway import llm_gateway

class DiagnosisAgent:
    """
    1. DiagnosisAgent
    Input: transaction, failure_reason, payment_method, retry_count
    Output: { "diagnosis": "...", "confidence": 0.0, "recommended_direction": "...", "reason": "..." }
    """
    def execute(self, transaction: Dict[str, Any]) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        reason = str(transaction.get("failure_reason", "")).upper()
        
        system_prompt = (
            "You are a specialized Payment Failure Diagnosis AI Agent. "
            "Analyze the failure reason and details to return structured JSON with fields: "
            "diagnosis (one of: TEMPORARY_FAILURE, INSUFFICIENT_FUNDS, BANK_DECLINE, NETWORK_ERROR, EXPIRED_CARD, PERMANENT_DECLINE, UNKNOWN), "
            "confidence (float 0 to 1), recommended_direction (RETRY, REMINDER, ESCALATE, or STOP), and reason (string explanation)."
        )

        user_prompt = (
            f"Transaction ID: {transaction.get('transaction_id')}\n"
            f"Failure Reason: {transaction.get('failure_reason')}\n"
            f"Payment Method: {transaction.get('payment_method')}\n"
            f"Retry Count: {transaction.get('retry_count')}\n"
            f"Hours Since Failure: {transaction.get('hours_since_failure')}\n"
            "Provide diagnosis JSON."
        )

        res, provider, latency = llm_gateway.generate(user_prompt, system_prompt)
        
        # Ensure valid keys exist
        if not isinstance(res, dict) or "diagnosis" not in res:
            res = {
                "diagnosis": "TEMPORARY_FAILURE" if "INSUFFICIENT" in reason or "NETWORK" in reason else "UNKNOWN",
                "confidence": 0.8,
                "recommended_direction": "RETRY",
                "reason": f"Fallback rule diagnosis for failure reason '{reason}'."
            }

        return res, provider, latency

diagnosis_agent = DiagnosisAgent()
