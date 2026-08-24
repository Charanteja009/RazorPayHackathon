import time
from typing import Dict, Any, Tuple
from backend.app.services.ml_service import ml_predictor

class RecoveryScoringAgent:
    """
    2. RecoveryScoringAgent
    Uses pre-trained PyTorch MLP model directly. Does NOT use LLM.
    Returns: { "recovery_probability": float, "threshold": float, "recovery_eligible": bool, "risk_category": str }
    """
    def execute(self, transaction: Dict[str, Any]) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        res = ml_predictor.predict(transaction)
        latency = round((time.time() - start) * 1000, 2)
        return res, "PyTorch_MLP", latency

ml_scoring_agent = RecoveryScoringAgent()
