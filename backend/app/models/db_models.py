import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class WorkflowState(str, Enum):
    PENDING = "PENDING"
    DIAGNOSED = "DIAGNOSED"
    SCORED = "SCORED"
    STRATEGIZED = "STRATEGIZED"
    POLICY_VERIFIED = "POLICY_VERIFIED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    STOPPED = "STOPPED"

class ActionState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    STOPPED = "STOPPED"

class DiagnosisType(str, Enum):
    TEMPORARY_FAILURE = "TEMPORARY_FAILURE"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    BANK_DECLINE = "BANK_DECLINE"
    NETWORK_ERROR = "NETWORK_ERROR"
    EXPIRED_CARD = "EXPIRED_CARD"
    PERMANENT_DECLINE = "PERMANENT_DECLINE"
    UNKNOWN = "UNKNOWN"

class ActionType(str, Enum):
    RETRY_PAYMENT = "RETRY_PAYMENT"
    WAIT_AND_RETRY = "WAIT_AND_RETRY"
    SEND_PAYMENT_REMINDER = "SEND_PAYMENT_REMINDER"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    STOP = "STOP"

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    customer_tenure_days = Column(Integer, default=30)
    customer_lifetime_value = Column(Float, default=1000.0)
    payment_success_rate = Column(Float, default=0.8)
    previous_successes = Column(Integer, default=5)
    previous_failures = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="customer")

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    failure_reason = Column(String(128), nullable=False)
    payment_method = Column(String(64), nullable=False)
    retry_count = Column(Integer, default=0)
    status = Column(String(32), default=WorkflowState.PENDING)
    hours_since_failure = Column(Float, default=1.0)
    days_since_last_success = Column(Float, default=10.0)
    recovered = Column(Boolean, default=False)
    demo_scenario = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")
    attempts = relationship("PaymentAttempt", back_populates="transaction")
    predictions = relationship("RecoveryPrediction", back_populates="transaction")
    actions = relationship("RecoveryAction", back_populates="transaction")
    agent_runs = relationship("AgentRun", back_populates="transaction")
    audit_logs = relationship("AuditLog", back_populates="transaction")
    outcome = relationship("RecoveryOutcome", back_populates="transaction", uselist=False)

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    gateway = Column(String(64), nullable=False)
    gateway_payment_id = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="attempts")

class RecoveryPrediction(Base):
    __tablename__ = "recovery_predictions"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    recovery_probability = Column(Float, nullable=False)
    risk_category = Column(String(64), nullable=False)
    recovery_eligible = Column(Boolean, nullable=False)
    threshold = Column(Float, nullable=False)
    contributing_features = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="predictions")

class RecoveryAction(Base):
    __tablename__ = "recovery_actions"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    action_type = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    requires_human_review = Column(Boolean, default=False)
    state = Column(String(32), default=ActionState.PENDING)
    policy_decision = Column(String(32), nullable=True) # APPROVED / BLOCKED
    policy_reason = Column(Text, nullable=True)
    fallback_action = Column(String(64), nullable=True)
    idempotency_key = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

    transaction = relationship("Transaction", back_populates="actions")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    agent_name = Column(String(64), nullable=False)
    step_name = Column(String(64), nullable=False)
    decision = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    latency_ms = Column(Float, default=0.0)
    provider_used = Column(String(64), default="System")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="agent_runs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    agent = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False) # ACTION_REQUESTED, POLICY_CHECKED, etc.
    reason = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="audit_logs")

class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    action_id = Column(String(64), nullable=True)
    final_status = Column(String(32), nullable=False) # SUCCESS, FAILED, ESCALATED, STOPPED
    recovery_amount = Column(Float, default=0.0)
    recovery_cost = Column(Float, default=0.0)
    net_recovery_value = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="outcome")

class LLMRequest(Base):
    __tablename__ = "llm_requests"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(64), nullable=True)
    provider = Column(String(64), nullable=False)
    prompt_summary = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    fallback_triggered = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)
    path = Column(String(256), nullable=False)
    request_hash = Column(String(128), nullable=False)
    response_json = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
