from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.models.db_models import WorkflowState, ActionState, DiagnosisType, ActionType

class TransactionBase(BaseModel):
    amount: float
    currency: str = "INR"
    failure_reason: str
    payment_method: str
    retry_count: int = 0
    hours_since_failure: float = 1.0
    days_since_last_success: float = 10.0

class TransactionCreate(TransactionBase):
    transaction_id: str
    customer_id: str

class CustomerSchema(BaseModel):
    customer_id: str
    name: str
    email: str
    customer_tenure_days: int
    customer_lifetime_value: float
    payment_success_rate: float
    previous_successes: int
    previous_failures: int

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    recovery_probability: float
    risk_category: str
    recovery_eligible: bool
    threshold: float
    contributing_features: Optional[List[Dict[str, Any]]] = None

class DiagnosisResponse(BaseModel):
    diagnosis: str
    confidence: float
    recommended_direction: str
    reason: str

class StrategyResponse(BaseModel):
    action: str
    reason: str
    confidence: float
    requires_human_review: bool

class PolicyDecisionResponse(BaseModel):
    decision: str  # APPROVED or BLOCKED
    reason: str
    fallback_action: Optional[str] = None
    action_state: str  # PENDING, APPROVED, BLOCKED, EXECUTING, SUCCESS, FAILED, ESCALATED, STOPPED

class ActionRequest(BaseModel):
    idempotency_key: Optional[str] = None

class GatewayResultResponse(BaseModel):
    success: bool
    status: str
    gateway: str
    payment_id: Optional[str] = None
    error_message: Optional[str] = None

class AgentStepDetail(BaseModel):
    step_name: str
    agent_name: str
    decision: str
    status: str
    latency_ms: float
    provider_used: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class AgentTimelineResponse(BaseModel):
    transaction_id: str
    workflow_state: str
    steps: List[AgentStepDetail]

class AuditLogResponse(BaseModel):
    id: str
    transaction_id: str
    agent: str
    actor: str
    event_type: str
    reason: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class TransactionResponse(TransactionBase):
    transaction_id: str
    customer_id: str
    status: str
    recovered: bool
    demo_scenario: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Optional prediction & action summary
    recovery_probability: Optional[float] = None
    threshold: Optional[float] = None
    risk_category: Optional[str] = None
    recommended_action: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionDetailResponse(TransactionResponse):
    customer: Optional[CustomerSchema] = None
    diagnosis: Optional[DiagnosisResponse] = None
    prediction: Optional[PredictionResponse] = None
    latest_action: Optional[Dict[str, Any]] = None
    policy_decision: Optional[PolicyDecisionResponse] = None
    gateway_result: Optional[GatewayResultResponse] = None
    outcome: Optional[Dict[str, Any]] = None
    audit_trail: List[AuditLogResponse] = []
    agent_timeline: Optional[AgentTimelineResponse] = None

class DashboardSummaryResponse(BaseModel):
    at_risk_revenue: float
    recovered_revenue: float
    recovery_rate: float
    net_recovery_value: float
    active_recoveries: int
    escalated_cases: int
    stopped_recoveries: int
    total_transactions: int

class DashboardRevenueResponse(BaseModel):
    timeline: List[Dict[str, Any]]
    by_failure_reason: List[Dict[str, Any]]
    by_payment_method: List[Dict[str, Any]]

class ProviderStatus(BaseModel):
    name: str
    healthy: bool
    status: str  # Healthy, Unavailable, Fallback
    request_count: int
    fallback_count: int

class ProviderHealthResponse(BaseModel):
    providers: List[ProviderStatus]
    simulation_state: Dict[str, bool]

class SimulationToggleRequest(BaseModel):
    simulate_openai_failure: Optional[bool] = None
    simulate_all_llm_failure: Optional[bool] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    idempotency_key: Optional[str] = None
