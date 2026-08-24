import pytest
from backend.app.services.policy_engine import policy_engine

def test_max_retry_limit_blocked():
    txn = {'amount': 1000.0, 'retry_count': 3, 'failure_reason': 'TEMPORARY_FAILURE'}
    pred = {'recovery_probability': 0.9, 'recovery_eligible': True, 'threshold': 0.07}
    action = {'action': 'RETRY_PAYMENT'}
    diag = {'diagnosis': 'TEMPORARY_FAILURE'}
    
    res = policy_engine.evaluate(txn, pred, action, diag)
    assert res["decision"] == "BLOCKED"
    assert "retry limit" in res["reason"].lower()

def test_permanent_decline_blocked():
    txn = {'amount': 1000.0, 'retry_count': 0, 'failure_reason': 'PERMANENT_DECLINE'}
    pred = {'recovery_probability': 0.5, 'recovery_eligible': True, 'threshold': 0.07}
    action = {'action': 'RETRY_PAYMENT'}
    diag = {'diagnosis': 'PERMANENT_DECLINE'}
    
    res = policy_engine.evaluate(txn, pred, action, diag)
    assert res["decision"] == "BLOCKED"
    assert "permanent" in res["reason"].lower()

def test_low_probability_blocks_retry():
    txn = {'amount': 1000.0, 'retry_count': 0, 'failure_reason': 'TEMPORARY_FAILURE'}
    pred = {'recovery_probability': 0.02, 'recovery_eligible': False, 'threshold': 0.07}
    action = {'action': 'RETRY_PAYMENT'}
    diag = {'diagnosis': 'TEMPORARY_FAILURE'}
    
    res = policy_engine.evaluate(txn, pred, action, diag)
    assert res["decision"] == "BLOCKED"
    assert res["fallback_action"] == "SEND_PAYMENT_REMINDER"

def test_high_value_transaction_escalates():
    txn = {'amount': 60000.0, 'retry_count': 0, 'failure_reason': 'TEMPORARY_FAILURE'}
    pred = {'recovery_probability': 0.9, 'recovery_eligible': True, 'threshold': 0.07}
    action = {'action': 'RETRY_PAYMENT'}
    diag = {'diagnosis': 'TEMPORARY_FAILURE'}
    
    res = policy_engine.evaluate(txn, pred, action, diag)
    assert res["decision"] == "BLOCKED"
    assert res["fallback_action"] == "ESCALATE_TO_HUMAN"
