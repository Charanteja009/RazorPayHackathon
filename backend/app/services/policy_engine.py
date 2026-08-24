from typing import Dict, Any
from backend.app.core.config import settings
from backend.app.models.db_models import ActionState, DiagnosisType, ActionType

class PolicyEngine:
    """
    Deterministic server-side Policy Engine.
    Mandatory safety gatekeeper for ALL financial recovery operations.
    Enforces loop protection & strict bounds (MAX_RETRY_COUNT = 3).
    """

    @staticmethod
    def evaluate(
        transaction: Dict[str, Any],
        prediction: Dict[str, Any],
        proposed_action: Dict[str, Any],
        diagnosis: Dict[str, Any]
    ) -> Dict[str, Any]:
        action = str(proposed_action.get("action", "")).upper()
        amount = float(transaction.get("amount", 0.0))
        retry_count = int(transaction.get("retry_count", 0))
        failure_reason = str(transaction.get("failure_reason", "")).upper()
        diag_code = str(diagnosis.get("diagnosis", "")).upper()
        
        prob = float(prediction.get("recovery_probability", 0.0))
        eligible = bool(prediction.get("recovery_eligible", False))
        threshold = float(prediction.get("threshold", settings.AVERAGE_RECOVERY_RATE))

        # Rule 1: Valid action type check
        allowed_actions = [a.value for a in ActionType]
        if action not in allowed_actions:
            return {
                "decision": "BLOCKED",
                "reason": f"Invalid or unapproved action type '{action}'. System permits only standard recovery actions.",
                "fallback_action": ActionType.ESCALATE_TO_HUMAN.value,
                "action_state": ActionState.BLOCKED.value
            }

        # Rule 2: Priority 10 Fix - Loop Prevention & Max Retry Bound Enforcement
        if retry_count >= settings.MAX_RETRY_COUNT:
            return {
                "decision": "BLOCKED",
                "reason": f"Maximum payment retry limit ({settings.MAX_RETRY_COUNT}) reached. System forcefully halted retries to prevent workflow cycles.",
                "fallback_action": ActionType.ESCALATE_TO_HUMAN.value,
                "action_state": ActionState.ESCALATED.value
            }

        # Rule 3: Permanent decline auto-retry prohibition
        permanent_diagnoses = [
            DiagnosisType.PERMANENT_DECLINE.value,
            DiagnosisType.EXPIRED_CARD.value
        ]
        if (diag_code in permanent_diagnoses or "PERMANENT" in failure_reason or "EXPIRED" in failure_reason) and action in [ActionType.RETRY_PAYMENT.value, ActionType.WAIT_AND_RETRY.value]:
            return {
                "decision": "BLOCKED",
                "reason": f"Permanent decline diagnosis ('{diag_code}') cannot be auto-retried.",
                "fallback_action": ActionType.SEND_PAYMENT_REMINDER.value if diag_code == DiagnosisType.EXPIRED_CARD.value else ActionType.STOP.value,
                "action_state": ActionState.BLOCKED.value
            }

        # Rule 4: Low ML recovery probability blocks monetary retries
        if not eligible and action in [ActionType.RETRY_PAYMENT.value, ActionType.WAIT_AND_RETRY.value]:
            return {
                "decision": "BLOCKED",
                "reason": f"Recovery probability ({round(prob, 4)}) is below business threshold ({round(threshold, 4)}). Automated retry blocked to prevent wasted attempt cost.",
                "fallback_action": ActionType.SEND_PAYMENT_REMINDER.value,
                "action_state": ActionState.BLOCKED.value
            }

        # Rule 5: High transaction value requiring human oversight
        if amount >= settings.HIGH_VALUE_THRESHOLD:
            if proposed_action.get("requires_human_review") or action == ActionType.RETRY_PAYMENT.value:
                return {
                    "decision": "BLOCKED",
                    "reason": f"Transaction amount (₹{amount:,.2f}) exceeds high-value threshold (₹{settings.HIGH_VALUE_THRESHOLD:,.2f}). Escalating for human authorization.",
                    "fallback_action": ActionType.ESCALATE_TO_HUMAN.value,
                    "action_state": ActionState.ESCALATED.value
                }

        # Rule 6: Non-monetary actions (SEND_PAYMENT_REMINDER, ESCALATE_TO_HUMAN, STOP) are approved safely
        if action in [ActionType.SEND_PAYMENT_REMINDER.value, ActionType.ESCALATE_TO_HUMAN.value, ActionType.STOP.value]:
            final_state = ActionState.APPROVED.value
            if action == ActionType.ESCALATE_TO_HUMAN.value:
                final_state = ActionState.ESCALATED.value
            elif action == ActionType.STOP.value:
                final_state = ActionState.STOPPED.value
                
            return {
                "decision": "APPROVED",
                "reason": f"Non-monetary action '{action}' approved under policy guardrails.",
                "fallback_action": None,
                "action_state": final_state
            }

        # Rule 7: Monetary action approved
        return {
            "decision": "APPROVED",
            "reason": f"Monetary retry action '{action}' approved. ML probability ({round(prob, 4)}) exceeds threshold ({round(threshold, 4)}), retries ({retry_count}/{settings.MAX_RETRY_COUNT}) within bounds.",
            "fallback_action": None,
            "action_state": ActionState.APPROVED.value
        }

policy_engine = PolicyEngine()
