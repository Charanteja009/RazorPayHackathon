# AI Revenue Recovery Platform — Razorpay Track 03

> **Find revenue that’s slipping away and win it back.**

An enterprise-grade, production-style AI Revenue Recovery platform built for failed payment interventions. The platform combines a pre-trained **PyTorch MLP machine learning model**, a **7-Agent orchestration pipeline**, a **deterministic server-side Policy Engine**, a **resilient LLM gateway** with automated fallbacks, **Razorpay test-mode integration**, **PostgreSQL database**, and a **React Command Center UI**.

> [!IMPORTANT]
> **Razorpay Integration Boundary**: Razorpay Test Mode is used as the payment gateway boundary, with a mock gateway for deterministic hackathon scenarios. The system operates in a test/simulation environment and does NOT perform real customer payment charges.
>
> **ML Explanation Disclaimer**: The model estimates recovery probability from transaction features. The explanation highlights features associated with the prediction; it is not a causal explanation.

---

## 🏛️ System Architecture

```
Payment Failure (Webhook / Event)
   │
   ▼
1. DiagnosisAgent ────────► Identifies root failure cause (TEMPORARY_FAILURE, PERMANENT_DECLINE, etc.)
   │
   ▼
2. RecoveryScoringAgent ──► PyTorch MLP inference (Dynamic architecture from model_metadata.json)
   │
   ▼
3. StrategyAgent ─────────► LLM reasoning (selects action: RETRY, REMINDER, ESCALATE, STOP)
   │
   ▼
4. PolicyEngine ──────────► Universal server-side deterministic policy verification (Fail-closed)
   │
   ▼
5. RecoveryExecutorAgent ─► Payment Gateway execution (Mandatory Idempotency, Razorpay Test / Mock)
   │
   ▼
6. OutcomeMonitorAgent ───► Calculates Net Recovery Value (Full Amount - Cost) & updates State Machine
   │
   ▼
7. AuditAgent ────────────► Persists append-only audit trail in PostgreSQL
```

---

## 🚀 Key Features & Safety Guardrails

1. **Pre-trained PyTorch MLP Service**:
   - Directly loads `model_artifacts/final_mlp_model.pth`, `preprocessor.joblib`, `feature_names.json`, and `model_metadata.json`.
   - The model estimates recovery probability from transaction features. The explanation highlights features associated with the prediction; it is not a causal explanation.

2. **Deterministic Server-Side Policy Engine (Fail-Closed)**:
   - Universal gatekeeper for all financial and recovery actions.
   - Enforces max 3 payment retries, blocks retries on permanent declines, escalates high-value transactions (> ₹50,000) for human review, and requires `Idempotency-Key` headers for financial idempotency.
   - Low ML probability blocks monetary retries while permitting safe interventions (reminders, escalation, safe stop).

3. **Resilient LLM Fallback Chain (Fail-Closed Safety)**:
   - Cascades automatically: `OpenAI` → `Groq` → `Ollama` → `Deterministic Guardrails`.
   - Guaranteed conservative fallback if all reasoning providers fail or return invalid JSON. When all LLMs fail, system fails closed (`STOP` / `ESCALATE_TO_HUMAN`).
   - Includes UI demo controls to simulate provider failures live during hackathons.

4. **Consistent Revenue Recovery Metrics**:
   - **At-Risk Revenue**: Total transaction amounts for failed payments entering recovery.
   - **Recovered Revenue**: Full transaction amount recovered on `SUCCESS` actions (e.g. ₹4,200).
   - **Net Recovery Value**: `Recovered Revenue - Action Attempt Costs` (₹50 attempt fee) = ₹4,150.

---

## 🎮 Preserved 5 Deterministic Demo Scenarios

1. **Scenario 1**: Temporary failure → High ML score → Auto Retry → Success → RECOVERED.
2. **Scenario 2**: Permanent decline → Policy Engine blocks auto-retry → STOPPED.
3. **Scenario 3**: Max retries (3/3) reached → Policy Engine prevents loop → ESCALATED.
4. **Scenario 4**: Simulate OpenAI failure → Automatic Groq fallback → RECOVERED.
5. **Scenario 5**: All LLMs unavailable → Conservative Deterministic Policy → Safe STOP/ESCALATE.

---

## 🛠️ Running the Application

### Option 1: Docker Compose (Recommended)

```bash
cd D:\2048\RazorPay
docker compose up --build
```

- **Frontend Command Center**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Documentation**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

### Option 2: Local Manual Setup

#### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing Suite

Run the full automated pytest suite (covers happy paths, policy guardrails, mandatory idempotency, 404/422 error codes, provider fallback, and complete end-to-end workflow):

```bash
python -m pytest -v
```

---

## 📋 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/recovery/predict` | Invokes PyTorch MLP prediction service directly |
| `POST` | `/api/recovery/{id}/start` | Executes 7-agent workflow (`Idempotency-Key` mandatory) |
| `GET`  | `/api/recovery/{id}` | Detailed transaction, ML explanation, policy, and audit |
| `POST` | `/api/recovery/{id}/retry` | Policy retry execution (`Idempotency-Key` mandatory) |
| `POST` | `/api/recovery/{id}/stop` | Manually stops recovery workflow |
| `POST` | `/api/recovery/{id}/escalate` | Escalates transaction to human team |
| `GET`  | `/api/recovery` | Paginated recovery queue table |
| `GET`  | `/api/dashboard/summary` | At-Risk, Recovered, Net Recovery Value, and KPIs |
| `GET`  | `/api/dashboard/revenue` | Revenue analytics and breakdown by reason/method |
| `GET`  | `/api/audit/{id}` | Immutable append-only audit trail logs |
| `GET`  | `/api/agents/{id}` | Step-by-step 7-agent execution timeline |
| `GET`  | `/api/llm/providers` | Provider health status, request count, fallback count |
| `POST` | `/api/llm/simulation` | Toggle simulated OpenAI / All LLM provider failures |
| `POST` | `/api/seed/demo-scenarios` | Reseeds default demo dataset and 5 scenarios |
