import uuid
import logging
from typing import Dict, Any
from backend.app.services.gateway.base import PaymentGateway

logger = logging.getLogger(__name__)

class MockPaymentGateway(PaymentGateway):
    def __init__(self):
        self.name = "RazorpayMockGateway"

    def retry_payment(self, transaction_id: str, amount: float, payment_method: str, idempotency_key: str = None) -> Dict[str, Any]:
        logger.info(f"MockGateway processing retry for tx: {transaction_id}, amount: {amount}, idempotency: {idempotency_key}")
        
        pay_id = f"pay_mock_{uuid.uuid4().hex[:10]}"
        
        # Deterministic outcome rules based on transaction ID or scenario flags
        if "SCENARIO_1" in transaction_id or "TEMPORARY" in transaction_id or "RETRY_OK" in transaction_id or amount < 5000:
            return {
                "success": True,
                "status": "SUCCESS",
                "gateway": self.name,
                "payment_id": pay_id,
                "error_message": None
            }
        elif "SCENARIO_2" in transaction_id or "PERMANENT" in transaction_id or "DECLINE" in transaction_id:
            return {
                "success": False,
                "status": "FAILED",
                "gateway": self.name,
                "payment_id": pay_id,
                "error_message": "Hard decline from issuing bank."
            }
        else:
            # Default success for general mock runs
            return {
                "success": True,
                "status": "SUCCESS",
                "gateway": self.name,
                "payment_id": pay_id,
                "error_message": None
            }

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        return {
            "payment_id": payment_id,
            "status": "captured",
            "gateway": self.name
        }
