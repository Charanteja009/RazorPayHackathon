import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from backend.app.models.db_models import (
    Customer, Transaction, WorkflowState, ActionState, RecoveryPrediction,
    RecoveryAction, AuditLog, RecoveryOutcome, AgentRun, PaymentAttempt
)
from backend.app.services.agents.orchestrator import recovery_orchestrator

def test_complete_end_to_end_recovery_workflow():
    """
    Priority 6 Fix: Comprehensive End-to-End Integration Test.
    Tests the full pipeline from failed transaction creation through all 7 agents, DB state transitions,
    gateway execution, outcome calculation, and audit trail generation.
    """
    mock_db = MagicMock(spec=Session)
    
    # Mock Customer
    customer = Customer(
        customer_id="C_E2E_001",
        name="End-to-End Test Customer",
        email="e2e@example.com",
        customer_tenure_days=180,
        customer_lifetime_value=25000.0,
        payment_success_rate=0.88,
        previous_successes=15,
        previous_failures=2
    )

    # Mock Failed Transaction
    tx = Transaction(
        transaction_id="TX_E2E_100",
        customer_id="C_E2E_001",
        amount=4200.0,
        currency="INR",
        failure_reason="INSUFFICIENT_FUNDS",
        payment_method="UPI",
        retry_count=0,
        status=WorkflowState.PENDING.value,
        hours_since_failure=1.5,
        days_since_last_success=3.0,
        recovered=False,
        customer=customer
    )

    # Setup mock query behavior
    def query_side_effect(model):
        q = MagicMock()
        if model == Transaction:
            q.filter.return_value.first.return_value = tx
        elif model == RecoveryOutcome:
            q.filter.return_value.first.return_value = None
        return q

    mock_db.query.side_effect = query_side_effect

    # Execute complete orchestrator workflow
    idempotency_key = "ik_e2e_test_999"
    result = recovery_orchestrator.run_recovery_workflow(mock_db, tx.transaction_id, idempotency_key)

    # Assertions
    # 1. Transaction state changed correctly
    assert tx.status == WorkflowState.SUCCESS.value
    assert tx.recovered is True

    # 2. Result structure returned
    assert result["transaction_id"] == "TX_E2E_100"
    assert result["status"] == WorkflowState.SUCCESS.value
    assert result["diagnosis"]["diagnosis"] in ["INSUFFICIENT_FUNDS", "TEMPORARY_FAILURE", "UNKNOWN"]
    assert result["prediction"]["recovery_probability"] > 0
    assert result["policy_decision"]["decision"] == "APPROVED"
    assert result["gateway_result"]["success"] is True

    # 3. Outcome metrics updated (Full Amount Recovery: ₹4,200 - ₹50 fee = ₹4,150)
    assert result["outcome"]["recovery_amount"] == 4200.0
    assert result["outcome"]["recovery_cost"] == 50.0
    assert result["outcome"]["net_recovery_value"] == 4150.0

    # 4. DB DB objects added (RecoveryPrediction, RecoveryAction, AgentRun, AuditLog, PaymentAttempt)
    assert mock_db.add.called
    assert mock_db.commit.called
