import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  BrainCircuit, 
  ShieldAlert, 
  CreditCard, 
  Play, 
  RotateCcw, 
  Octagon, 
  UserCheck 
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { 
  getTransactionDetail, 
  startRecoveryWorkflow, 
  retryRecoveryAction, 
  stopRecoveryAction, 
  escalateRecoveryAction 
} from '../services/api';

export const TransactionDetail = ({ transactionId, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDetail = async () => {
    try {
      setLoading(true);
      const res = await getTransactionDetail(transactionId);
      setData(res);
    } catch (e) {
      console.error("Detail error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (transactionId) fetchDetail();
  }, [transactionId]);

  const handleAction = async (actionFn) => {
    setActionLoading(true);
    try {
      await actionFn(transactionId);
      await fetchDetail();
    } catch (e) {
      alert("Action failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading transaction details for {transactionId}...</div>;
  }

  if (!data || !data.transaction) {
    return <div className="p-8 text-center text-slate-500">Transaction not found.</div>;
  }

  const tx = data.transaction;
  const pred = data.prediction;
  const act = data.latest_action;
  const out = data.outcome;

  return (
    <div className="space-y-6">
      {/* Top Bar with Back button & Status */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900">{tx.transaction_id}</h2>
              <StatusBadge status={tx.status} />
            </div>
            <p className="text-xs text-slate-500">Customer ID: {tx.customer_id} • Created: {new Date(tx.created_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleAction(startRecoveryWorkflow)}
            disabled={actionLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold minimal-btn-primary disabled:opacity-50 inline-flex items-center gap-1.5 transition"
          >
            <Play className="w-3.5 h-3.5" />
            Run Agent Workflow
          </button>
          <button
            onClick={() => handleAction(retryRecoveryAction)}
            disabled={actionLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold minimal-btn-secondary disabled:opacity-50 inline-flex items-center gap-1.5 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Policy Retry
          </button>
          <button
            onClick={() => handleAction(escalateRecoveryAction)}
            disabled={actionLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 disabled:opacity-50 inline-flex items-center gap-1.5 transition"
          >
            <UserCheck className="w-3.5 h-3.5" />
            Escalate
          </button>
          <button
            onClick={() => handleAction(stopRecoveryAction)}
            disabled={actionLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 disabled:opacity-50 inline-flex items-center gap-1.5 transition"
          >
            <Octagon className="w-3.5 h-3.5" />
            Stop
          </button>
        </div>
      </div>

      {/* Grid overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="minimal-card p-4 rounded-xl">
          <p className="text-xs text-slate-500">Transaction Amount</p>
          <p className="text-xl font-bold text-slate-900 mt-0.5">₹{tx.amount.toLocaleString('en-IN')}</p>
        </div>
        <div className="minimal-card p-4 rounded-xl">
          <p className="text-xs text-slate-500">Failure Reason</p>
          <p className="text-sm font-semibold text-rose-600 mt-0.5 font-mono">{tx.failure_reason}</p>
        </div>
        <div className="minimal-card p-4 rounded-xl">
          <p className="text-xs text-slate-500">Payment Method</p>
          <p className="text-sm font-semibold text-slate-900 mt-0.5">{tx.payment_method}</p>
        </div>
        <div className="minimal-card p-4 rounded-xl">
          <p className="text-xs text-slate-500">Current Retries</p>
          <p className="text-sm font-semibold text-slate-900 mt-0.5">{tx.retry_count} / 3 Max</p>
        </div>
      </div>

      {/* ML Prediction & Feature Contributions ("Why?") Panel */}
      <div className="minimal-card p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-semibold text-slate-900">PyTorch MLP Recovery Scoring</h3>
          </div>
          <span className="text-xs font-mono text-slate-500">Optimal Threshold: {pred?.threshold || 0.0707}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500 uppercase">Recovery Probability</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">
              {pred?.recovery_probability != null ? `${(pred.recovery_probability * 100).toFixed(1)}%` : 'N/A'}
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500 uppercase">Risk Category</p>
            <p className="text-base font-semibold text-slate-900 mt-2">{pred?.risk_category || 'Scored'}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500 uppercase">Action Eligibility</p>
            <p className={`text-base font-semibold mt-2 ${pred?.recovery_eligible ? 'text-emerald-700' : 'text-slate-700'}`}>
              {pred?.recovery_eligible ? 'Eligible for Retry' : 'Ineligible (Below Threshold)'}
            </p>
          </div>
        </div>

        {/* Contributing Features ("Why?") */}
        <div className="pt-2">
          <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Model Explanation (Associated Feature Correlations)
          </h4>
          <p className="text-[11px] text-slate-500 mb-3 italic">
            The model estimates recovery probability from transaction features. The explanation highlights features associated with the prediction; it is not a causal explanation.
          </p>
          <div className="space-y-2">
            {(pred?.contributing_features || []).map((feat, idx) => (
              <div 
                key={idx} 
                className={`p-3 rounded-xl border text-xs flex items-center gap-3 ${
                  feat.direction === 'positive' 
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
                    : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${feat.direction === 'positive' ? 'bg-emerald-500' : 'bg-slate-400'}`}></div>
                <span>{feat.explanation}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Policy Engine & Gateway Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Policy Engine Decision */}
        <div className="minimal-card p-6 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
            <ShieldAlert className="w-5 h-5 text-amber-600" />
            <h3 className="text-base font-semibold text-slate-900">Policy Engine Verification</h3>
          </div>
          {act ? (
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Policy Decision:</span>
                <StatusBadge status={act.policy_decision || act.state} />
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Approved Action:</span>
                <span className="font-mono font-semibold text-slate-800">{act.action_type}</span>
              </div>
              <div className="py-1">
                <span className="text-slate-500 block mb-1">Policy Rationale:</span>
                <p className="text-slate-800 bg-slate-50 p-2.5 rounded-lg border border-slate-200">{act.policy_reason || act.reason}</p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-4">Policy verification pending.</p>
          )}
        </div>

        {/* Gateway Result */}
        <div className="minimal-card p-6 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
            <CreditCard className="w-5 h-5 text-emerald-600" />
            <h3 className="text-base font-semibold text-slate-900">Razorpay Gateway Result</h3>
          </div>
          {out ? (
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Final Status:</span>
                <StatusBadge status={out.final_status} />
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Recovered Amount:</span>
                <span className="font-semibold text-emerald-700">₹{out.recovery_amount.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Action Fee / Cost:</span>
                <span className="text-slate-800">₹{out.recovery_cost}</span>
              </div>
              <div className="flex justify-between py-1 pt-1 font-bold">
                <span className="text-slate-700">Net Recovery Value:</span>
                <span className={out.net_recovery_value >= 0 ? "text-emerald-700" : "text-rose-600"}>
                  ₹{out.net_recovery_value.toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-4">Gateway execution pending.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionDetail;
