import React, { useEffect, useState } from 'react';
import { GitMerge, Clock, Cpu } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { getAgentTimeline, getRecoveryQueue } from '../services/api';

export const AgentTimeline = ({ transactionId: initialTxId }) => {
  const [selectedTxId, setSelectedTxId] = useState(initialTxId || '');
  const [queue, setQueue] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getRecoveryQueue().then(data => {
      setQueue(data);
      if (!selectedTxId && data.length > 0) {
        setSelectedTxId(data[0].transaction_id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedTxId) {
      setLoading(true);
      getAgentTimeline(selectedTxId)
        .then(data => setTimeline(data))
        .catch(err => console.error("Timeline error:", err))
        .finally(() => setLoading(false));
    }
  }, [selectedTxId]);

  return (
    <div className="space-y-6">
      {/* Header Selector */}
      <div className="minimal-card p-4 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <GitMerge className="w-5 h-5 text-slate-800" />
          <h3 className="text-base font-semibold text-slate-900">Multi-Agent Workflow Execution Visualizer</h3>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label className="text-xs text-slate-500 whitespace-nowrap">Select Transaction:</label>
          <select
            value={selectedTxId}
            onChange={(e) => setSelectedTxId(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900 w-full sm:w-64"
          >
            {queue.map(tx => (
              <option key={tx.transaction_id} value={tx.transaction_id}>
                {tx.transaction_id} (₹{tx.amount}) - {tx.status}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading agent sequence logs...</div>
      ) : !timeline || timeline.steps.length === 0 ? (
        <div className="minimal-card p-12 text-center text-slate-500 rounded-2xl">
          <p>No agent runs recorded yet for transaction <span className="font-mono text-slate-900">{selectedTxId}</span>.</p>
          <p className="text-xs text-slate-400 mt-2">Click 'Run Workflow' in Command Center or Recovery Queue to execute the 7-agent pipeline.</p>
        </div>
      ) : (
        <div className="minimal-card p-6 rounded-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <span className="text-xs text-slate-500">Transaction State Machine:</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="font-bold text-slate-900 font-mono">{selectedTxId}</span>
                <StatusBadge status={timeline.workflow_state} />
              </div>
            </div>
            <span className="text-xs text-slate-500">{timeline.steps.length} Steps Executed</span>
          </div>

          {/* Timeline Visualizer Steps */}
          <div className="space-y-4 relative before:absolute before:left-6 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
            {timeline.steps.map((step, idx) => (
              <div key={idx} className="relative pl-12">
                {/* Step indicator dot */}
                <div className="absolute left-4 top-2 -translate-x-1/2 w-4 h-4 rounded-full bg-white border-2 border-slate-900 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-900"></div>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 hover:border-slate-300 transition">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">{step.agent_name}</span>
                      <span className="text-xs text-slate-500 font-mono">({step.step_name})</span>
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-slate-500">
                      <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-slate-400" /> {step.provider_used}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3 text-slate-400" /> {step.latency_ms} ms</span>
                      <StatusBadge status={step.status} />
                    </div>
                  </div>

                  <div>
                    <span className="text-xs font-semibold text-slate-700">Decision / Action:</span>
                    <p className="text-xs text-slate-900 font-mono mt-0.5 bg-white p-2 rounded-lg border border-slate-200">
                      {step.decision}
                    </p>
                  </div>

                  {step.metadata && (
                    <details className="text-[11px] text-slate-500">
                      <summary className="cursor-pointer hover:text-slate-900 transition">View Step Metadata JSON</summary>
                      <pre className="mt-2 p-2 bg-white rounded text-[10px] text-slate-800 font-mono overflow-x-auto border border-slate-200">
                        {JSON.stringify(step.metadata, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentTimeline;
