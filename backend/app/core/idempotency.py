import hashlib
import json
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.db_models import IdempotencyRecord

def check_idempotency(db: Session, key: Optional[str], path: str, body_dict: Optional[Dict[str, Any]] = None) -> Optional[IdempotencyRecord]:
    if not key:
        return None

    body_str = json.dumps(body_dict or {}, sort_keys=True)
    req_hash = hashlib.sha256(f"{path}:{body_str}".encode('utf-8')).hexdigest()

    existing = db.query(IdempotencyRecord).filter(IdempotencyRecord.idempotency_key == key).first()
    if existing:
        if existing.request_hash != req_hash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Idempotency-Key '{key}' was previously used with different request parameters."
            )
        return existing

    return None

def record_idempotency(db: Session, key: str, path: str, body_dict: Optional[Dict[str, Any]], response_dict: Dict[str, Any], status_code: int = 200):
    if not key:
        return
    
    body_str = json.dumps(body_dict or {}, sort_keys=True)
    req_hash = hashlib.sha256(f"{path}:{body_str}".encode('utf-8')).hexdigest()

    record = IdempotencyRecord(
        idempotency_key=key,
        path=path,
        request_hash=req_hash,
        response_json=response_dict,
        status_code=status_code
    )
    db.add(record)
    db.commit()
