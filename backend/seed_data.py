import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.db_models import (
    Customer, Transaction, WorkflowState, ActionState, RecoveryPrediction,
    RecoveryAction, AuditLog, RecoveryOutcome, AgentRun, PaymentAttempt
)

def seed_database():
    print("Initializing PostgreSQL database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check if dataset already seeded
        if db.query(Transaction).count() > 0:
            print("Database already contains transaction data. Skipping initial dataset seed.")
            return

        print("Seeding synthetic transactions from dataset...")

        csv_path = os.path.join(os.path.dirname(__file__), "..", "transactions.csv")
        if not os.path.exists(csv_path):
            print(f"Warning: CSV dataset not found at {csv_path}. Creating fallback dataset.")
            df = pd.DataFrame()
        else:
            df = pd.read_csv(csv_path)

        # Create base customers
        customer_cache = {}
        
        # 1. Seed demo customers & default synthetic transactions (limit to 100 for fast startup)
        sample_df = df.head(100) if not df.empty else pd.DataFrame()

        for idx, row in sample_df.iterrows():
            cid = str(row.get("customer_id", f"C{idx:05d}"))
            if cid not in customer_cache:
                c = Customer(
                    customer_id=cid,
                    name=f"Customer {cid}",
                    email=f"customer_{cid.lower()}@example.com",
                    customer_tenure_days=int(row.get("customer_tenure_days", 180)),
                    customer_lifetime_value=float(row.get("customer_lifetime_value", 12000.0)),
                    payment_success_rate=float(row.get("payment_success_rate", 0.82)),
                    previous_successes=int(row.get("previous_successes", 8)),
                    previous_failures=int(row.get("previous_failures", 2))
                )
                db.add(c)
                customer_cache[cid] = c

            tx_id = str(row.get("transaction_id", f"TX{idx:06d}"))
            tx = Transaction(
                transaction_id=tx_id,
                customer_id=cid,
                amount=float(row.get("amount", 2500.0)),
                currency="INR",
                failure_reason=str(row.get("failure_reason", "INSUFFICIENT_FUNDS")),
                payment_method=str(row.get("payment_method", "CARD")),
                retry_count=int(row.get("retry_count", 0)),
                status=WorkflowState.PENDING.value,
                hours_since_failure=float(row.get("hours_since_failure", 2.0)),
                days_since_last_success=float(row.get("days_since_last_success", 12.0)),
                recovered=bool(row.get("recovered", False))
            )
            db.add(tx)

        db.commit()

        # 2. Seed 5 Deterministic Demo Scenarios
        print("Seeding 5 Deterministic Demo Scenarios...")
        
        demo_cust = Customer(
            customer_id="C_DEMO_99",
            name="Demo Priority Enterprise Customer",
            email="enterprise_demo@razorpay-track03.com",
            customer_tenure_days=450,
            customer_lifetime_value=85000.0,
            payment_success_rate=0.92,
            previous_successes=25,
            previous_failures=2
        )
        db.merge(demo_cust)
        db.commit()

        scenarios = [
            {
                "transaction_id": "SCENARIO_1_TEMPORARY_SUCCESS",
                "customer_id": "C_DEMO_99",
                "amount": 4200.0,
                "failure_reason": "INSUFFICIENT_FUNDS",
                "payment_method": "UPI",
                "retry_count": 0,
                "hours_since_failure": 1.5,
                "demo_scenario": "Scenario 1: Temporary Failure -> ML Score High -> Auto Retry -> Success"
            },
            {
                "transaction_id": "SCENARIO_2_PERMANENT_DECLINE_BLOCKED",
                "customer_id": "C_DEMO_99",
                "amount": 8900.0,
                "failure_reason": "PERMANENT_DECLINE",
                "payment_method": "CARD",
                "retry_count": 0,
                "hours_since_failure": 24.0,
                "demo_scenario": "Scenario 2: Permanent Decline -> Policy Engine Blocks Auto-Retry -> Safe Stop"
            },
            {
                "transaction_id": "SCENARIO_3_MAX_RETRIES_ESCALATED",
                "customer_id": "C_DEMO_99",
                "amount": 15000.0,
                "failure_reason": "NETWORK_ERROR",
                "payment_method": "NET_BANKING",
                "retry_count": 3,
                "hours_since_failure": 48.0,
                "demo_scenario": "Scenario 3: Max Retries (3/3) Reached -> Policy Engine Prevents Loop -> Escalated"
            },
            {
                "transaction_id": "SCENARIO_4_OPENAI_FALLBACK_GROQ",
                "customer_id": "C_DEMO_99",
                "amount": 3500.0,
                "failure_reason": "TEMPORARY_FAILURE",
                "payment_method": "UPI",
                "retry_count": 1,
                "hours_since_failure": 3.0,
                "demo_scenario": "Scenario 4: OpenAI Simulated Failure -> Seamless Groq Fallback -> Recovered"
            },
            {
                "transaction_id": "SCENARIO_5_ALL_LLM_DETERMINISTIC_FALLBACK",
                "customer_id": "C_DEMO_99",
                "amount": 12500.0,
                "failure_reason": "UNKNOWN",
                "payment_method": "CARD",
                "retry_count": 1,
                "hours_since_failure": 12.0,
                "demo_scenario": "Scenario 5: All LLMs Unavailable -> Conservative Deterministic Policy -> Safe Stop/Escalate"
            }
        ]

        for sc in scenarios:
            tx = Transaction(
                transaction_id=sc["transaction_id"],
                customer_id=sc["customer_id"],
                amount=sc["amount"],
                currency="INR",
                failure_reason=sc["failure_reason"],
                payment_method=sc["payment_method"],
                retry_count=sc["retry_count"],
                status=WorkflowState.PENDING.value,
                hours_since_failure=sc["hours_since_failure"],
                days_since_last_success=5.0,
                recovered=False,
                demo_scenario=sc["demo_scenario"]
            )
            db.merge(tx)

        db.commit()
        print("Database successfully seeded with transactions and demo scenarios!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
