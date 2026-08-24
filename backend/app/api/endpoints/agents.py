from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.db_models import Transaction, AgentRun
from backend.app.schemas.pydantic_schemas import AgentTimelineResponse, AgentStepDetail

router = APIRouter()

@router.get("/{transaction_id}", response_model=AgentTimelineResponse)
def get_agent_timeline(transaction_id: str, db: Session = Depends(get_db)):
    """
    Returns step-by-step Agent Timeline execution logs for a transaction.
    """
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")

    runs = db.query(AgentRun).filter(AgentRun.transaction_id == transaction_id).order_by(AgentRun.created_at.asc()).all()
    
    steps = [
        AgentStepDetail(
            step_name=r.step_name,
            agent_name=r.agent_name,
            decision=r.decision,
            status=r.status,
            latency_ms=r.latency_ms,
            provider_used=r.provider_used,
            timestamp=r.created_at,
            metadata=r.metadata_json
        ) for r in runs
    ]

    return AgentTimelineResponse(
        transaction_id=tx.transaction_id,
        workflow_state=tx.status,
        steps=steps
    )
