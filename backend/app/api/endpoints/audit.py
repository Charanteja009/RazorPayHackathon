from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.db_models import AuditLog
from backend.app.schemas.pydantic_schemas import AuditLogResponse

router = APIRouter()

@router.get("", response_model=List[AuditLogResponse])
@router.get("/{transaction_id}", response_model=List[AuditLogResponse])
def get_audit_trail(transaction_id: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    """
    Exposes append-only audit trail logs.
    If transaction_id is provided, returns logs for that transaction; otherwise returns latest system audit events.
    """
    query = db.query(AuditLog)
    if transaction_id:
        query = query.filter(AuditLog.transaction_id == transaction_id)
        
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs
