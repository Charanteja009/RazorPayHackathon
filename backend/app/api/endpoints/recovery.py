from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.idempotency import check_idempotency, record_idempotency
from backend.app.models.db_models import Transaction, RecoveryPrediction, RecoveryAction, RecoveryOutcome, AuditLog, WorkflowState
from backend.app.schemas.pydantic_schemas import (
    PredictionResponse, TransactionResponse, TransactionDetailResponse,
    DiagnosisResponse, PolicyDecisionResponse, GatewayResultResponse, AgentTimelineResponse
)
from backend.app.services.ml_service import ml_predictor
from backend.app.services.agents.orchestrator import recovery_orchestrator
from backend.app.services.policy_engine import policy_engine

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict_recovery(transaction: dict):
    """
    ML Prediction Endpoint: Invokes trained PyTorch MLP model directly.
    """
    try:
        return ml_predictor.predict(transaction)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Prediction error: {str(e)}")

@router.post("/{transaction_id}/start")
def start_recovery_workflow(
    transaction_id: str,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """
    Executes 7-agent recovery workflow with MANDATORY Idempotency protection.
    """
    # Priority 5 Fix: Mandatory Idempotency-Key header check
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Header 'Idempotency-Key' is mandatory for starting financial recovery workflows."
        )

    existing = check_idempotency(db, idempotency_key, f"/api/recovery/{transaction_id}/start")
    if existing:
        return existing.response_json

    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    try:
        result = recovery_orchestrator.run_recovery_workflow(db, transaction_id, idempotency_key)
        record_idempotency(db, idempotency_key, f"/api/recovery/{transaction_id}/start", None, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("", response_model=List[TransactionResponse])
def list_recovery_queue(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lists failed payment recovery queue with scores & statuses.
    """
    query = db.query(Transaction)
    if status_filter:
        query = query.filter(Transaction.status == status_filter.upper())
        
    transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    res = []
    for tx in transactions:
        pred = db.query(RecoveryPrediction).filter(RecoveryPrediction.transaction_id == tx.transaction_id).order_by(RecoveryPrediction.created_at.desc()).first()
        act = db.query(RecoveryAction).filter(RecoveryAction.transaction_id == tx.transaction_id).order_by(RecoveryAction.created_at.desc()).first()
        
        tx_resp = TransactionResponse.from_orm(tx)
        if pred:
            tx_resp.recovery_probability = pred.recovery_probability
            tx_resp.threshold = pred.threshold
            tx_resp.risk_category = pred.risk_category
        if act:
            tx_resp.recommended_action = act.action_type
            
        res.append(tx_resp)
        
    return res

@router.get("/{transaction_id}")
def get_transaction_detail(transaction_id: str, db: Session = Depends(get_db)):
    """
    Fetches full transaction breakdown, ML non-causal explanation ('Why?'), policy state, and audit logs.
    """
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    pred = db.query(RecoveryPrediction).filter(RecoveryPrediction.transaction_id == transaction_id).order_by(RecoveryPrediction.created_at.desc()).first()
    act = db.query(RecoveryAction).filter(RecoveryAction.transaction_id == transaction_id).order_by(RecoveryAction.created_at.desc()).first()
    out = db.query(RecoveryOutcome).filter(RecoveryOutcome.transaction_id == transaction_id).first()
    audits = db.query(AuditLog).filter(AuditLog.transaction_id == transaction_id).order_by(AuditLog.timestamp.asc()).all()

    ml_dict = ml_predictor.predict({
        "transaction_id": tx.transaction_id,
        "amount": tx.amount,
        "failure_reason": tx.failure_reason,
        "payment_method": tx.payment_method,
        "retry_count": tx.retry_count,
        "hours_since_failure": tx.hours_since_failure,
        "payment_success_rate": tx.customer.payment_success_rate if tx.customer else 0.8,
        "previous_successes": tx.customer.previous_successes if tx.customer else 5,
        "previous_failures": tx.customer.previous_failures if tx.customer else 1
    })

    return {
        "transaction": TransactionResponse.from_orm(tx),
        "customer": tx.customer,
        "prediction": pred or ml_dict,
        "latest_action": act,
        "outcome": out,
        "audit_trail": audits
    }

@router.post("/{transaction_id}/retry")
def retry_recovery_action(
    transaction_id: str,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """
    Re-triggers recovery workflow subject to server-side Policy Engine check and MANDATORY Idempotency key.
    """
    # Priority 5 Fix: Mandatory Idempotency-Key header check
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Header 'Idempotency-Key' is mandatory for retry financial actions."
        )

    existing = check_idempotency(db, idempotency_key, f"/api/recovery/{transaction_id}/retry")
    if existing:
        return existing.response_json

    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    res = recovery_orchestrator.run_recovery_workflow(db, transaction_id, idempotency_key)
    record_idempotency(db, idempotency_key, f"/api/recovery/{transaction_id}/retry", None, res)
    return res

@router.post("/{transaction_id}/stop")
def stop_recovery(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    tx.status = WorkflowState.STOPPED.value
    db.commit()
    return {"transaction_id": transaction_id, "status": tx.status, "message": "Recovery workflow manually stopped."}

@router.post("/{transaction_id}/escalate")
def escalate_recovery(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    tx.status = WorkflowState.ESCALATED.value
    db.commit()
    return {"transaction_id": transaction_id, "status": tx.status, "message": "Transaction escalated to human team."}
