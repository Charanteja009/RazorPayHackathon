import time
import uuid
from typing import Dict, Any, Tuple
from backend.app.services.gateway import get_payment_gateway
from backend.app.models.db_models import ActionState, ActionType

class RecoveryExecutorAgent:
    """
    5. RecoveryExecutorAgent
    Executes bounded recovery actions through PaymentGateway with Idempotency Key.
    """
    def __init__(self):
        self.gateway = get_payment_gateway()

    def execute(
        self,
        transaction: Dict[str, Any],
        approved_action: str,
        idempotency_key: str = None
    ) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        tx_id = transaction.get("transaction_id")
        amount = float(transaction.get("amount", 0.0))
        method = transaction.get("payment_method", "CARD")
        ikey = idempotency_key or f"ik_{tx_id}_{uuid.uuid4().hex[:8]}"

        if approved_action in [ActionType.RETRY_PAYMENT.value, ActionType.WAIT_AND_RETRY.value]:
            res = self.gateway.retry_payment(tx_id, amount, method, ikey)
        elif approved_action == ActionType.SEND_PAYMENT_REMINDER.value:
            res = {
                "success": True,
                "status": "SUCCESS",
                "gateway": "NotificationEngine",
                "payment_id": f"rem_{uuid.uuid4().hex[:8]}",
                "error_message": None,
                "details": f"Payment reminder email & SMS sent to customer."
            }
        elif approved_action in [ActionType.ESCALATE_TO_HUMAN.value, ActionType.STOP.value]:
            res = {
                "success": True,
                "status": "SUCCESS" if approved_action == ActionType.STOP.value else "ESCALATED",
                "gateway": "WorkflowController",
                "payment_id": None,
                "error_message": None,
                "details": f"Action '{approved_action}' executed successfully."
            }
        else:
            res = {
                "success": False,
                "status": "FAILED",
                "gateway": "System",
                "payment_id": None,
                "error_message": f"Unhandled action type '{approved_action}'."
            }

        latency = round((time.time() - start) * 1000, 2)
        return res, res.get("gateway", "Gateway"), latency

executor_agent = RecoveryExecutorAgent()
