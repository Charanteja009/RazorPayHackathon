from backend.app.services.gateway.razorpay_gateway import RazorpayTestGateway
from backend.app.services.gateway.mock_gateway import MockPaymentGateway

def get_payment_gateway():
    return RazorpayTestGateway()

__all__ = ["RazorpayTestGateway", "MockPaymentGateway", "get_payment_gateway"]
