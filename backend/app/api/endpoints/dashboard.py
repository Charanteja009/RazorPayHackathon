from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.db_models import Transaction, RecoveryOutcome, WorkflowState
from backend.app.schemas.pydantic_schemas import DashboardSummaryResponse, DashboardRevenueResponse

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes Command Center metrics:
    - At-Risk Revenue: Sum of all failed transaction amounts in system
    - Recovered Revenue: Sum of amounts successfully recovered
    - Net Recovery Value: Recovered Revenue - Total Action Attempt Costs
    - Recovery Rate: (Recovered Count / Total Transactions) * 100
    """
    all_txs = db.query(Transaction).all()
    total_count = len(all_txs)
    
    if total_count == 0:
        return DashboardSummaryResponse(
            at_risk_revenue=0.0,
            recovered_revenue=0.0,
            recovery_rate=0.0,
            net_recovery_value=0.0,
            active_recoveries=0,
            escalated_cases=0,
            stopped_recoveries=0,
            total_transactions=0
        )

    # 1. At-Risk Revenue: Sum of transaction amounts
    at_risk_revenue = sum(t.amount for t in all_txs)

    # 2. Recovered Revenue & Net Recovery Value from RecoveryOutcome table
    outcomes = db.query(RecoveryOutcome).all()
    recovered_revenue = sum(o.recovery_amount for o in outcomes if o.final_status == WorkflowState.SUCCESS.value)
    total_costs = sum(o.recovery_cost for o in outcomes)
    net_recovery_value = recovered_revenue - total_costs

    recovered_count = db.query(Transaction).filter(Transaction.recovered == True).count()
    active_count = db.query(Transaction).filter(Transaction.status.in_([
        WorkflowState.PENDING.value, WorkflowState.DIAGNOSED.value, WorkflowState.SCORED.value,
        WorkflowState.STRATEGIZED.value, WorkflowState.POLICY_VERIFIED.value, WorkflowState.EXECUTING.value
    ])).count()
    
    escalated_count = db.query(Transaction).filter(Transaction.status == WorkflowState.ESCALATED.value).count()
    stopped_count = db.query(Transaction).filter(Transaction.status == WorkflowState.STOPPED.value).count()

    recovery_rate = round((recovered_count / total_count) * 100.0, 2) if total_count > 0 else 0.0

    return DashboardSummaryResponse(
        at_risk_revenue=round(at_risk_revenue, 2),
        recovered_revenue=round(recovered_revenue, 2),
        recovery_rate=recovery_rate,
        net_recovery_value=round(net_recovery_value, 2),
        active_recoveries=active_count,
        escalated_cases=escalated_count,
        stopped_recoveries=stopped_count,
        total_transactions=total_count
    )

@router.get("/revenue", response_model=DashboardRevenueResponse)
def get_revenue_analytics(db: Session = Depends(get_db)):
    """
    Returns breakdown analytics:
    - Recovery by failure reason
    - Recovery by payment method
    - Timeline of recovered vs at-risk revenue
    """
    # Breakdown by Failure Reason
    reason_query = db.query(
        Transaction.failure_reason,
        func.count(Transaction.transaction_id).label("total_count"),
        func.sum(Transaction.amount).label("total_at_risk")
    ).group_by(Transaction.failure_reason).all()

    by_reason = []
    for r in reason_query:
        rec_count = db.query(Transaction).filter(
            Transaction.failure_reason == r.failure_reason,
            Transaction.recovered == True
        ).count()
        by_reason.append({
            "category": r.failure_reason,
            "total_count": r.total_count,
            "at_risk_revenue": float(r.total_at_risk or 0.0),
            "recovered_count": rec_count,
            "recovery_rate": round((rec_count / r.total_count) * 100, 1) if r.total_count > 0 else 0.0
        })

    # Breakdown by Payment Method
    method_query = db.query(
        Transaction.payment_method,
        func.count(Transaction.transaction_id).label("total_count"),
        func.sum(Transaction.amount).label("total_at_risk")
    ).group_by(Transaction.payment_method).all()

    by_method = []
    for m in method_query:
        rec_count = db.query(Transaction).filter(
            Transaction.payment_method == m.payment_method,
            Transaction.recovered == True
        ).count()
        by_method.append({
            "category": m.payment_method,
            "total_count": m.total_count,
            "at_risk_revenue": float(m.total_at_risk or 0.0),
            "recovered_count": rec_count,
            "recovery_rate": round((rec_count / m.total_count) * 100, 1) if m.total_count > 0 else 0.0
        })

    # Time series simulation timeline
    timeline = [
        {"period": "Day 1", "at_risk": 45000.0, "recovered": 28000.0, "net_value": 26500.0},
        {"period": "Day 2", "at_risk": 52000.0, "recovered": 36000.0, "net_value": 34200.0},
        {"period": "Day 3", "at_risk": 61000.0, "recovered": 48000.0, "net_value": 45800.0},
        {"period": "Day 4", "at_risk": 58000.0, "recovered": 44000.0, "net_value": 41900.0},
        {"period": "Day 5", "at_risk": 74000.0, "recovered": 59000.0, "net_value": 56400.0},
    ]

    return DashboardRevenueResponse(
        timeline=timeline,
        by_failure_reason=by_reason,
        by_payment_method=by_method
    )
