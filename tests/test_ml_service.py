import pytest
from backend.app.services.ml_service import ml_predictor

def test_ml_prediction_output_structure():
    sample = {
        'amount': 2500.0,
        'failure_reason': 'INSUFFICIENT_FUNDS',
        'payment_method': 'UPI',
        'retry_count': 0,
        'hours_since_failure': 1.0,
        'days_since_last_success': 5.0,
        'previous_successes': 10,
        'previous_failures': 1,
        'payment_success_rate': 0.9,
        'customer_tenure_days': 200,
        'customer_lifetime_value': 20000.0
    }
    
    res = ml_predictor.predict(sample)
    
    assert "recovery_probability" in res
    assert isinstance(res["recovery_probability"], float)
    assert 0.0 <= res["recovery_probability"] <= 1.0
    assert "risk_category" in res
    assert "recovery_eligible" in res
    assert "threshold" in res
    assert "contributing_features" in res
    assert len(res["contributing_features"]) > 0

def test_ml_non_causal_explanations():
    sample = {
        'amount': 3000.0,
        'failure_reason': 'PERMANENT_DECLINE',
        'payment_method': 'CARD',
        'retry_count': 2,
        'hours_since_failure': 48.0,
        'payment_success_rate': 0.4
    }
    
    res = ml_predictor.predict(sample)
    
    for feat in res["contributing_features"]:
        explanation = feat["explanation"].lower()
        # Verify no causal claims are made
        assert "caused" not in explanation
        assert "because of" not in explanation
        assert ("correlated" in explanation or "associated" in explanation or "indicates" in explanation)
