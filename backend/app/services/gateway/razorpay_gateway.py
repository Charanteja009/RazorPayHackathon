import uuid
import logging
import json
import urllib.request
import base64
from typing import Dict, Any
from backend.app.core.config import settings
from backend.app.services.gateway.base import PaymentGateway
from backend.app.services.gateway.mock_gateway import MockPaymentGateway

logger = logging.getLogger(__name__)

class RazorpayTestGateway(PaymentGateway):
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.mock_fallback = MockPaymentGateway()

    def retry_payment(self, transaction_id: str, amount: float, payment_method: str, idempotency_key: str = None) -> Dict[str, Any]:
        if settings.USE_MOCK_GATEWAY or not self.key_id or not self.key_secret or self.key_id.startswith("rzp_test_placeholder"):
            logger.info("Razorpay credentials not set or USE_MOCK_GATEWAY=true. Using MockPaymentGateway.")
            return self.mock_fallback.retry_payment(transaction_id, amount, payment_method, idempotency_key)

        try:
            # Call Razorpay Test API to create order / retry payment
            auth_str = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode('utf-8')).decode('utf-8')
            
            req_data = json.dumps({
                "amount": int(amount * 100),  # Amount in paise
                "currency": "INR",
                "receipt": f"rcpt_{transaction_id[:10]}",
                "notes": {
                    "transaction_id": transaction_id,
                    "idempotency_key": idempotency_key or ""
                }
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api.razorpay.com/v1/orders",
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_str}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                res_json = json.loads(resp.read().decode('utf-8'))
                order_id = res_json.get("id")
                return {
                    "success": True,
                    "status": "SUCCESS",
                    "gateway": "RazorpayTestAPI",
                    "payment_id": f"pay_{order_id}",
                    "error_message": None
                }

        except Exception as e:
            logger.error(f"Razorpay API call error: {e}. Falling back to mock response.")
            return self.mock_fallback.retry_payment(transaction_id, amount, payment_method, idempotency_key)

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        return self.mock_fallback.get_payment_status(payment_id)
