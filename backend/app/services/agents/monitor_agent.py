import time
from typing import Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.models.db_models import WorkflowState, ActionState

class OutcomeMonitorAgent:
    """
    6. OutcomeMonitorAgent
    Monitors execution result, calculates net recovery value, updates state machine.
    Consistent Math: Recovered Revenue = Full Transaction Amount on SUCCESS.
    """
    def execute(
        self,
        transaction: Dict[str, Any],
        executor_result: Dict[str, Any],
        approved_action: str
    ) -> Tuple[Dict[str, Any], str, float]:
        start = time.time()
        success = executor_result.get("success", False)
        status_raw = str(executor_result.get("status", "")).upper()
        amount = float(transaction.get("amount", 0.0))
        cost = settings.COST_PER_RECOVERY_ATTEMPT if approved_action in ["RETRY_PAYMENT", "WAIT_AND_RETRY"] else 10.0

        if success and status_raw == "SUCCESS":
            final_workflow_state = WorkflowState.SUCCESS.value
            final_action_state = ActionState.SUCCESS.value
            # Priority 4 Fix: Full Transaction Amount recovered
            recovery_amount = amount
            net_value = recovery_amount - cost
        elif status_raw == "ESCALATED" or approved_action == "ESCALATE_TO_HUMAN":
            final_workflow_state = WorkflowState.ESCALATED.value
            final_action_state = ActionState.ESCALATED.value
            recovery_amount = 0.0
            net_value = 0.0
        elif approved_action == "STOP":
            final_workflow_state = WorkflowState.STOPPED.value
            final_action_state = ActionState.STOPPED.value
            recovery_amount = 0.0
            net_value = 0.0
        else:
            final_workflow_state = WorkflowState.FAILED.value
            final_action_state = ActionState.FAILED.value
            recovery_amount = 0.0
            net_value = -cost

        res = {
            "final_status": final_workflow_state,
            "action_state": final_action_state,
            "recovery_amount": round(recovery_amount, 2),
            "recovery_cost": round(cost, 2),
            "net_recovery_value": round(net_value, 2),
            "is_recovered": (final_workflow_state == WorkflowState.SUCCESS.value)
        }

        latency = round((time.time() - start) * 1000, 2)
        return res, "OutcomeMonitor", latency

outcome_monitor_agent = OutcomeMonitorAgent()
