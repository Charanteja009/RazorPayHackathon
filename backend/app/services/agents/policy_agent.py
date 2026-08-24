import time
from typing import Dict, Any, Tuple
from backend.app.services.policy_engine import policy_engine

class PolicyAgent:
    """
    4. PolicyAgent / PolicyEngine
    Deterministic server-side Policy verification.
    """
    def execute(
        self,
        transaction: Dict[str, Any],
        prediction: Dict[str, Any],
        strategy: Dict[str, Any],
        diagnosis: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        res = policy_engine.evaluate(transaction, prediction, strategy, diagnosis)
        latency = round((time.time() - start) * 1000, 2)
        return res, "DeterministicPolicyEngine", latency

policy_agent = PolicyAgent()
