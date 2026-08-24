import React, { useEffect, useState } from 'react';
import { 
  DollarSign, 
  CheckCircle2, 
  Percent, 
  TrendingUp, 
  Play, 
  AlertTriangle 
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import MetricsCard from '../components/MetricsCard';
import StatusBadge from '../components/StatusBadge';
import { getDashboardSummary, getRevenueAnalytics, getRecoveryQueue, startRecoveryWorkflow } from '../services/api';

export const CommandCenter = ({ onSelectTransaction }) => {
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [demoTxs, setDemoTxs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executingId, setExecutingId] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sumData, anaData, queueData] = await Promise.all([
        getDashboardSummary(),
        getRevenueAnalytics(),
        getRecoveryQueue()
      ]);
      setSummary(sumData);
      setAnalytics(anaData);
      setDemoTxs(queueData.filter(t => t.demo_scenario || t.transaction_id.startsWith('SCENARIO')));
    } catch (err) {
      console.error("Error loading command center data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunWorkflow = async (txId) => {
    setExecutingId(txId);
    try {
      await startRecoveryWorkflow(txId);
      await loadData();
    } catch (e) {
      alert("Execution error: " + (e.response?.data?.detail || e.message));
    } finally {
      setExecutingId(null);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Command Center analytics...</div>;
  }

  const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EC4899'];

  return (
    <div className="space-y-6">
      {/* KPI Cards Header */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="At-Risk Revenue"
          value={`₹${(summary?.at_risk_revenue || 0).toLocaleString('en-IN')}`}
          subtitle="Sum of failed payment candidates"
          icon={AlertTriangle}
          color="blue"
        />
        <MetricsCard
          title="Recovered Revenue"
          value={`₹${(summary?.recovered_revenue || 0).toLocaleString('en-IN')}`}
          subtitle="Total revenue saved by system"
          icon={CheckCircle2}
          color="emerald"
        />
        <MetricsCard
          title="Recovery Rate"
          value={`${summary?.recovery_rate || 0}%`}
          subtitle={`${summary?.active_recoveries || 0} active recoveries in flight`}
          icon={Percent}
          color="dark"
        />
        <MetricsCard
          title="Net Recovery Value"
          value={`₹${(summary?.net_recovery_value || 0).toLocaleString('en-IN')}`}
          subtitle="Recovered revenue minus attempt fees"
          icon={TrendingUp}
          color="amber"
        />
      </div>

      {/* Recovery Funnel Diagram */}
      <div className="minimal-card p-6 rounded-2xl">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">AI Recovery Pipeline Funnel</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-center">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-[11px] text-slate-500 font-medium uppercase">1. Failed Payment</p>
            <p className="text-xl font-bold text-slate-900 mt-1">{summary?.total_transactions || 0}</p>
            <p className="text-[10px] text-slate-400 mt-1">Detected by Webhook</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-[11px] text-slate-500 font-medium uppercase">2. Diagnosed</p>
            <p className="text-xl font-bold text-blue-600 mt-1">{summary?.total_transactions || 0}</p>
            <p className="text-[10px] text-slate-400 mt-1">DiagnosisAgent</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-[11px] text-slate-500 font-medium uppercase">3. ML Eligible</p>
            <p className="text-xl font-bold text-indigo-600 mt-1">{summary?.total_transactions || 0}</p>
            <p className="text-[10px] text-slate-400 mt-1">PyTorch MLP (prob &gt; threshold)</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-[11px] text-slate-500 font-medium uppercase">4. Policy Approved</p>
            <p className="text-xl font-bold text-amber-600 mt-1">{(summary?.total_transactions || 0) - (summary?.stopped_recoveries || 0)}</p>
            <p className="text-[10px] text-slate-400 mt-1">Deterministic PolicyEngine</p>
          </div>
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
            <p className="text-[11px] text-emerald-700 font-medium uppercase">5. Recovered</p>
            <p className="text-xl font-bold text-emerald-700 mt-1">₹{(summary?.recovered_revenue || 0).toLocaleString('en-IN')}</p>
            <p className="text-[10px] text-emerald-600 mt-1">Razorpay Gateway Test Mode</p>
          </div>
        </div>
      </div>

      {/* Analytics Breakdown Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="minimal-card p-6 rounded-2xl">
          <h3 className="text-sm font-semibold text-slate-900 mb-4">At-Risk Revenue by Failure Reason</h3>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.by_failure_reason || []}>
                <XAxis dataKey="category" stroke="#64748B" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', color: '#0F172A', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'At-Risk Revenue']}
                />
                <Bar dataKey="at_risk_revenue" radius={[4, 4, 0, 0]}>
                  {(analytics?.by_failure_reason || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="minimal-card p-6 rounded-2xl">
          <h3 className="text-sm font-semibold text-slate-900 mb-4">Recovery Rate by Payment Method (%)</h3>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.by_payment_method || []}>
                <XAxis dataKey="category" stroke="#64748B" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={10} tickLine={false} unit="%" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', color: '#0F172A', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  formatter={(val) => [`${val}%`, 'Recovery Rate']}
                />
                <Bar dataKey="recovery_rate" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Demo Walkthrough Scenarios */}
      <div className="minimal-card p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Preset Deterministic Demo Scenarios</h3>
            <p className="text-xs text-slate-500">Click 'Run Workflow' to test end-to-end multi-agent execution in real time.</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Transaction</th>
                <th className="px-4 py-3">Demo Scenario Description</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {demoTxs.map((tx) => (
                <tr key={tx.transaction_id} className="hover:bg-slate-50/80 transition">
                  <td className="px-4 py-3.5 font-semibold">
                    <button onClick={() => onSelectTransaction(tx.transaction_id)} className="hover:underline text-blue-600 font-mono">
                      {tx.transaction_id}
                    </button>
                  </td>
                  <td className="px-4 py-3.5 text-slate-600 max-w-md">
                    {tx.demo_scenario || 'Standard Demo Scenario'}
                  </td>
                  <td className="px-4 py-3.5 font-medium text-slate-900">₹{tx.amount.toLocaleString('en-IN')}</td>
                  <td className="px-4 py-3.5"><StatusBadge status={tx.status} /></td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      onClick={() => handleRunWorkflow(tx.transaction_id)}
                      disabled={executingId === tx.transaction_id}
                      className="px-3.5 py-1.5 rounded-lg text-xs font-semibold minimal-btn-primary disabled:opacity-50 inline-flex items-center gap-1.5 transition"
                    >
                      <Play className="w-3 h-3" />
                      {executingId === tx.transaction_id ? 'Running...' : 'Run Workflow'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;
