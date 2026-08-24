import React, { useEffect, useState } from 'react';
import { TrendingUp } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { getRevenueAnalytics } from '../services/api';

export const RevenueAnalytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRevenueAnalytics()
      .then(res => setData(res))
      .catch(err => console.error("Analytics error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading Revenue Analytics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Chart: Revenue Recovered over Time */}
      <div className="minimal-card p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-600" />
            <h3 className="text-base font-semibold text-slate-900">Revenue Recovery & Net Value Performance</h3>
          </div>
          <span className="text-xs text-slate-500">Daily Revenue Metrics</span>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data?.timeline || []}>
              <defs>
                <linearGradient id="colorAtRisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorRecovered" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="period" stroke="#64748B" fontSize={10} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', color: '#0F172A', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, '']}
              />
              <Area type="monotone" dataKey="at_risk" stroke="#3B82F6" fillOpacity={1} fill="url(#colorAtRisk)" name="At-Risk Revenue" />
              <Area type="monotone" dataKey="recovered" stroke="#10B981" fillOpacity={1} fill="url(#colorRecovered)" name="Recovered Revenue" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Breakdown Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Failure Reason */}
        <div className="minimal-card p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-semibold text-slate-900">Breakdown by Failure Reason</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-3 py-2">Failure Reason</th>
                  <th className="px-3 py-2">Count</th>
                  <th className="px-3 py-2">At-Risk (₹)</th>
                  <th className="px-3 py-2">Recovery %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(data?.by_failure_reason || []).map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80">
                    <td className="px-3 py-2.5 font-mono text-[11px] font-semibold text-slate-900">{row.category}</td>
                    <td className="px-3 py-2.5">{row.total_count}</td>
                    <td className="px-3 py-2.5 font-medium">₹{row.at_risk_revenue.toLocaleString('en-IN')}</td>
                    <td className="px-3 py-2.5 font-bold text-emerald-600">{row.recovery_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* By Payment Method */}
        <div className="minimal-card p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-semibold text-slate-900">Breakdown by Payment Method</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-3 py-2">Payment Method</th>
                  <th className="px-3 py-2">Count</th>
                  <th className="px-3 py-2">At-Risk (₹)</th>
                  <th className="px-3 py-2">Recovery %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(data?.by_payment_method || []).map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80">
                    <td className="px-3 py-2.5 font-semibold text-slate-900">{row.category}</td>
                    <td className="px-3 py-2.5">{row.total_count}</td>
                    <td className="px-3 py-2.5 font-medium">₹{row.at_risk_revenue.toLocaleString('en-IN')}</td>
                    <td className="px-3 py-2.5 font-bold text-emerald-600">{row.recovery_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RevenueAnalytics;
