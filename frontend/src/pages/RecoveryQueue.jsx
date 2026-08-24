import React, { useEffect, useState } from 'react';
import { Search, Filter, Play, ExternalLink, RefreshCw } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { getRecoveryQueue, startRecoveryWorkflow } from '../services/api';

export const RecoveryQueue = ({ onSelectTransaction }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [runningId, setRunningId] = useState(null);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const data = await getRecoveryQueue(filterStatus || null);
      setTransactions(data);
    } catch (e) {
      console.error("Queue fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [filterStatus]);

  const handleRun = async (txId) => {
    setRunningId(txId);
    try {
      await startRecoveryWorkflow(txId);
      await fetchQueue();
    } catch (e) {
      alert("Execution error: " + (e.response?.data?.detail || e.message));
    } finally {
      setRunningId(null);
    }
  };

  const filtered = transactions.filter(t => 
    t.transaction_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.failure_reason.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.payment_method.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header controls */}
      <div className="minimal-card p-4 rounded-2xl flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search transaction, reason, method..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">PENDING</option>
            <option value="SCORED">SCORED</option>
            <option value="POLICY_VERIFIED">POLICY_VERIFIED</option>
            <option value="EXECUTING">EXECUTING</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="FAILED">FAILED</option>
            <option value="ESCALATED">ESCALATED</option>
            <option value="STOPPED">STOPPED</option>
          </select>

          <button
            onClick={fetchQueue}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Queue Table */}
      <div className="minimal-card rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Fetching recovery queue...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3.5">Transaction ID</th>
                  <th className="px-4 py-3.5">Amount</th>
                  <th className="px-4 py-3.5">Failure Reason</th>
                  <th className="px-4 py-3.5">ML Prob %</th>
                  <th className="px-4 py-3.5">Risk Category</th>
                  <th className="px-4 py-3.5">Recommended Action</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-slate-400">No recovery queue items match your filter.</td>
                  </tr>
                ) : (
                  filtered.map((tx) => {
                    const prob = tx.recovery_probability != null ? (tx.recovery_probability * 100).toFixed(1) : 'N/A';
                    const probColor = tx.recovery_probability >= (tx.threshold || 0.0707) ? 'text-emerald-700 font-bold' : 'text-slate-600 font-bold';

                    return (
                      <tr key={tx.transaction_id} className="hover:bg-slate-50/80 transition">
                        <td className="px-4 py-3.5 font-semibold">
                          <button
                            onClick={() => onSelectTransaction(tx.transaction_id)}
                            className="hover:underline text-blue-600 font-mono flex items-center gap-1"
                          >
                            {tx.transaction_id}
                            <ExternalLink className="w-3 h-3 opacity-60" />
                          </button>
                        </td>
                        <td className="px-4 py-3.5 font-medium text-slate-900">₹{tx.amount.toLocaleString('en-IN')}</td>
                        <td className="px-4 py-3.5 text-slate-600 font-mono text-[11px]">{tx.failure_reason}</td>
                        <td className={`px-4 py-3.5 ${probColor}`}>{prob}%</td>
                        <td className="px-4 py-3.5 text-slate-700">{tx.risk_category || 'Scoring Pending'}</td>
                        <td className="px-4 py-3.5 font-mono text-[11px] text-slate-800 font-medium">{tx.recommended_action || 'Pending'}</td>
                        <td className="px-4 py-3.5"><StatusBadge status={tx.status} /></td>
                        <td className="px-4 py-3.5 text-right">
                          <button
                            onClick={() => handleRun(tx.transaction_id)}
                            disabled={runningId === tx.transaction_id}
                            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold minimal-btn-primary disabled:opacity-50 inline-flex items-center gap-1.5 transition"
                          >
                            <Play className="w-3 h-3" />
                            {runningId === tx.transaction_id ? 'Running...' : 'Run'}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecoveryQueue;
