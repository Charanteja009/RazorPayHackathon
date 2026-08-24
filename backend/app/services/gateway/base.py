from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentGateway(ABC):
    @abstractmethod
    def retry_payment(self, transaction_id: str, amount: float, payment_method: str, idempotency_key: str = None) -> Dict[str, Any]:
        """
        Retries a payment. Returns:
        {
            "success": bool,
            "status": "SUCCESS" | "FAILED" | "PENDING",
            "gateway": str,
            "payment_id": str | None,
            "error_message": str | None
        }
        """
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        pass
