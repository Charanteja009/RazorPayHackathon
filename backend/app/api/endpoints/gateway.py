from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from backend.app.services.gateway import get_payment_gateway

router = APIRouter()

class OrderRequest(BaseModel):
    transaction_id: str
    amount: float
    payment_method: str = "CARD"
    idempotency_key: Optional[str] = None

@router.post("/create-order")
def create_razorpay_order(request: OrderRequest):
    """
    Directly invokes Razorpay Gateway Service to create a payment retry order.
    Uses Razorpay Test API when credentials are set & USE_MOCK_GATEWAY=false,
    otherwise uses MockPaymentGateway.
    """
    gateway = get_payment_gateway()
    try:
        res = gateway.retry_payment(
            transaction_id=request.transaction_id,
            amount=request.amount,
            payment_method=request.payment_method,
            idempotency_key=request.idempotency_key
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
