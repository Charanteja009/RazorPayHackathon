import React, { useEffect, useState } from 'react';
import { ShieldCheck, Search } from 'lucide-react';
import { getAuditTrail } from '../services/api';

export const AuditTrail = ({ transactionId: initialTxId }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(initialTxId || '');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await getAuditTrail(search || null);
      setLogs(data);
    } catch (e) {
      console.error("Audit fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="minimal-card p-4 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-emerald-600" />
          <div>
            <h3 className="text-base font-semibold text-slate-900">Immutable Financial Audit Trail</h3>
            <p className="text-xs text-slate-500">Append-only compliance ledger for all automated payment actions</p>
          </div>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by Transaction ID or Event..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchLogs()}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900"
          />
        </div>
      </div>

      <div className="minimal-card rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading audit trail records...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3.5">Timestamp</th>
                  <th className="px-4 py-3.5">Transaction ID</th>
                  <th className="px-4 py-3.5">Event Type</th>
                  <th className="px-4 py-3.5">Agent</th>
                  <th className="px-4 py-3.5">Actor</th>
                  <th className="px-4 py-3.5">Reason / Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-4 py-8 text-center text-slate-400">No audit trail records found.</td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50/80 transition">
                      <td className="px-4 py-3 text-slate-500">{new Date(log.timestamp).toLocaleString()}</td>
                      <td className="px-4 py-3 font-semibold text-blue-600">{log.transaction_id}</td>
                      <td className="px-4 py-3 font-bold text-slate-900">{log.event_type}</td>
                      <td className="px-4 py-3 text-indigo-700">{log.agent}</td>
                      <td className="px-4 py-3 text-slate-500">{log.actor}</td>
                      <td className="px-4 py-3 font-sans text-slate-600 max-w-sm">{log.reason || 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditTrail;
