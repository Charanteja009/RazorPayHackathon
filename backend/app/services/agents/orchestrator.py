import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.db_models import (
    Transaction, RecoveryPrediction, RecoveryAction, AgentRun,
    PaymentAttempt, RecoveryOutcome, WorkflowState, ActionState
)
from backend.app.services.agents.diagnosis_agent import diagnosis_agent
from backend.app.services.agents.ml_scoring_agent import ml_scoring_agent
from backend.app.services.agents.strategy_agent import strategy_agent
from backend.app.services.agents.policy_agent import policy_agent
from backend.app.services.agents.executor_agent import executor_agent
from backend.app.services.agents.monitor_agent import outcome_monitor_agent
from backend.app.services.agents.audit_agent import audit_agent

logger = logging.getLogger(__name__)

class RecoveryOrchestrator:
    """
    Master Orchestrator executing the 7-agent revenue recovery workflow sequentially.
    """
    def run_recovery_workflow(
        self,
        db: Session,
        transaction_id: str,
        idempotency_key: str = None
    ) -> Dict[str, Any]:
        tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if not tx:
            raise ValueError(f"Transaction '{transaction_id}' not found.")

        # Convert transaction to dictionary for agent processing
        tx_dict = {
            "transaction_id": tx.transaction_id,
            "customer_id": tx.customer_id,
            "amount": tx.amount,
            "currency": tx.currency,
            "failure_reason": tx.failure_reason,
            "payment_method": tx.payment_method,
            "retry_count": tx.retry_count,
            "hours_since_failure": tx.hours_since_failure,
            "days_since_last_success": tx.days_since_last_success,
            "payment_success_rate": tx.customer.payment_success_rate if tx.customer else 0.8,
            "previous_successes": tx.customer.previous_successes if tx.customer else 5,
            "previous_failures": tx.customer.previous_failures if tx.customer else 1,
            "customer_lifetime_value": tx.customer.customer_lifetime_value if tx.customer else 15000.0,
            "customer_tenure_days": tx.customer.customer_tenure_days if tx.customer else 365,
            "demo_scenario": tx.demo_scenario
        }

        audit_agent.record_event(
            db, tx.transaction_id, "Orchestrator", "System", "WORKFLOW_STARTED",
            reason=f"Recovery workflow initiated for transaction ₹{tx.amount:,.2f}",
            metadata={"idempotency_key": idempotency_key}
        )

        # Step 1: Diagnosis Agent
        tx.status = WorkflowState.PENDING.value
        db.commit()
        
        diag_res, diag_prov, diag_lat = diagnosis_agent.execute(tx_dict)
        tx.status = WorkflowState.DIAGNOSED.value
        db.commit()
        
        self._record_agent_run(db, tx.transaction_id, "DiagnosisAgent", "DIAGNOSE", str(diag_res.get("diagnosis")), "DONE", diag_lat, diag_prov, diag_res)
        audit_agent.record_event(db, tx.transaction_id, "DiagnosisAgent", diag_prov, "DIAGNOSIS_COMPLETED", reason=diag_res.get("reason"), metadata=diag_res)

        # Step 2: Recovery Scoring Agent (ML Model)
        pred_res, pred_prov, pred_lat = ml_scoring_agent.execute(tx_dict)
        tx.status = WorkflowState.SCORED.value
        db.commit()

        # Save prediction record
        pred_record = RecoveryPrediction(
            transaction_id=tx.transaction_id,
            recovery_probability=pred_res["recovery_probability"],
            risk_category=pred_res["risk_category"],
            recovery_eligible=pred_res["recovery_eligible"],
            threshold=pred_res["threshold"],
            contributing_features=pred_res.get("contributing_features")
        )
        db.add(pred_record)
        db.commit()

        self._record_agent_run(db, tx.transaction_id, "RecoveryScoringAgent", "SCORE", f"Prob: {pred_res['recovery_probability']} ({pred_res['risk_category']})", "DONE", pred_lat, pred_prov, pred_res)
        audit_agent.record_event(db, tx.transaction_id, "RecoveryScoringAgent", "PyTorch_MLP", "ML_SCORING_COMPLETED", reason=f"Recovery probability calculated: {pred_res['recovery_probability']}", metadata=pred_res)

        # Step 3: Strategy Agent (LLM Reasoning)
        strat_res, strat_prov, strat_lat = strategy_agent.execute(tx_dict, diag_res, pred_res)
        tx.status = WorkflowState.STRATEGIZED.value
        db.commit()

        proposed_action = strat_res.get("action")
        self._record_agent_run(db, tx.transaction_id, "StrategyAgent", "STRATEGY", f"Action: {proposed_action}", "DONE", strat_lat, strat_prov, strat_res)
        audit_agent.record_event(db, tx.transaction_id, "StrategyAgent", strat_prov, "STRATEGY_PROPOSED", reason=strat_res.get("reason"), metadata=strat_res)

        # Step 4: Policy Agent (Deterministic Server-Side Policy Engine)
        policy_res, policy_prov, policy_lat = policy_agent.execute(tx_dict, pred_res, strat_res, diag_res)
        tx.status = WorkflowState.POLICY_VERIFIED.value
        db.commit()

        decision = policy_res.get("decision")
        approved_action = proposed_action if decision == "APPROVED" else policy_res.get("fallback_action", "ESCALATE_TO_HUMAN")
        
        # Save Action record
        act_record = RecoveryAction(
            transaction_id=tx.transaction_id,
            action_type=approved_action,
            reason=policy_res.get("reason", strat_res.get("reason")),
            confidence=strat_res.get("confidence", 1.0),
            requires_human_review=(approved_action == "ESCALATE_TO_HUMAN"),
            state=policy_res.get("action_state", ActionState.PENDING.value),
            policy_decision=decision,
            policy_reason=policy_res.get("reason"),
            fallback_action=policy_res.get("fallback_action"),
            idempotency_key=idempotency_key
        )
        db.add(act_record)
        db.commit()

        self._record_agent_run(db, tx.transaction_id, "PolicyAgent", "POLICY_VERIFY", f"Decision: {decision} ({approved_action})", "DONE", policy_lat, policy_prov, policy_res)
        audit_agent.record_event(
            db, tx.transaction_id, "PolicyAgent", "PolicyEngine", 
            "ACTION_APPROVED" if decision == "APPROVED" else "ACTION_BLOCKED",
            reason=policy_res.get("reason"), metadata=policy_res
        )

        # Handle Blocked or Non-retry Actions
        if decision == "BLOCKED" and approved_action in ["STOP", "ESCALATE_TO_HUMAN"]:
            tx.status = WorkflowState.STOPPED.value if approved_action == "STOP" else WorkflowState.ESCALATED.value
            db.commit()
            
            outcome_res, _, _ = outcome_monitor_agent.execute(tx_dict, {"success": False, "status": tx.status}, approved_action)
            self._save_outcome(db, tx.transaction_id, act_record.id, outcome_res)
            
            audit_agent.record_event(db, tx.transaction_id, "OutcomeMonitorAgent", "System", tx.status, reason=f"Workflow concluded with state: {tx.status}", metadata=outcome_res)
            return self._build_result_dict(tx, diag_res, pred_res, strat_res, policy_res, {"success": False, "status": tx.status}, outcome_res)

        # Step 5: Recovery Executor Agent (Payment Gateway)
        tx.status = WorkflowState.EXECUTING.value
        act_record.state = ActionState.EXECUTING.value
        db.commit()

        exec_res, exec_prov, exec_lat = executor_agent.execute(tx_dict, approved_action, idempotency_key)
        self._record_agent_run(db, tx.transaction_id, "RecoveryExecutorAgent", "EXECUTE_GATEWAY", f"Gateway status: {exec_res.get('status')}", "DONE", exec_lat, exec_prov, exec_res)
        audit_agent.record_event(db, tx.transaction_id, "RecoveryExecutorAgent", exec_prov, "GATEWAY_EXECUTED", reason=f"Gateway execution: {exec_res.get('status')}", metadata=exec_res)

        # Log attempt if payment attempt occurred
        if approved_action in ["RETRY_PAYMENT", "WAIT_AND_RETRY"]:
            tx.retry_count += 1
            db.add(PaymentAttempt(
                transaction_id=tx.transaction_id,
                attempt_number=tx.retry_count,
                gateway=exec_res.get("gateway", "MockGateway"),
                gateway_payment_id=exec_res.get("payment_id"),
                status=exec_res.get("status", "FAILED"),
                error_message=exec_res.get("error_message")
            ))
            db.commit()

        # Step 6: Outcome Monitor Agent
        outcome_res, mon_prov, mon_lat = outcome_monitor_agent.execute(tx_dict, exec_res, approved_action)
        
        tx.status = outcome_res["final_status"]
        tx.recovered = outcome_res["is_recovered"]
        act_record.state = outcome_res["action_state"]
        db.commit()

        self._save_outcome(db, tx.transaction_id, act_record.id, outcome_res)
        self._record_agent_run(db, tx.transaction_id, "OutcomeMonitorAgent", "MONITOR_OUTCOME", f"Final State: {tx.status}", "DONE", mon_lat, mon_prov, outcome_res)
        audit_agent.record_event(db, tx.transaction_id, "OutcomeMonitorAgent", "System", "RECOVERY_OUTCOME", reason=f"Final outcome state: {tx.status}", metadata=outcome_res)

        return self._build_result_dict(tx, diag_res, pred_res, strat_res, policy_res, exec_res, outcome_res)

    def _record_agent_run(self, db: Session, tx_id: str, agent: str, step: str, decision: str, status: str, latency: float, provider: str, meta: Dict[str, Any]):
        run = AgentRun(
            transaction_id=tx_id,
            agent_name=agent,
            step_name=step,
            decision=decision,
            status=status,
            latency_ms=latency,
            provider_used=provider,
            metadata_json=meta
        )
        db.add(run)
        db.commit()

    def _save_outcome(self, db: Session, tx_id: str, action_id: str, outcome: Dict[str, Any]):
        out = db.query(RecoveryOutcome).filter(RecoveryOutcome.transaction_id == tx_id).first()
        if not out:
            out = RecoveryOutcome(transaction_id=tx_id)
            db.add(out)
        
        out.action_id = action_id
        out.final_status = outcome["final_status"]
        out.recovery_amount = outcome["recovery_amount"]
        out.recovery_cost = outcome["recovery_cost"]
        out.net_recovery_value = outcome["net_recovery_value"]
        db.commit()

    def _build_result_dict(self, tx: Transaction, diag: Dict, pred: Dict, strat: Dict, policy: Dict, exec_res: Dict, outcome: Dict) -> Dict[str, Any]:
        return {
            "transaction_id": tx.transaction_id,
            "status": tx.status,
            "recovered": tx.recovered,
            "retry_count": tx.retry_count,
            "diagnosis": diag,
            "prediction": pred,
            "strategy": strat,
            "policy_decision": policy,
            "gateway_result": exec_res,
            "outcome": outcome
        }

recovery_orchestrator = RecoveryOrchestrator()
