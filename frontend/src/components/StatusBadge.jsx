import React from 'react';

export const StatusBadge = ({ status }) => {
  const s = String(status || 'PENDING').toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';

  if (s === 'SUCCESS' || s === 'RECOVERED' || s === 'APPROVED') {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (s === 'BLOCKED' || s === 'FAILED') {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (s === 'ESCALATED') {
    colorClasses = 'bg-amber-50 text-amber-800 border-amber-200';
  } else if (s === 'STOPPED') {
    colorClasses = 'bg-slate-100 text-slate-500 border-slate-200';
  } else if (s.includes('EXECUTING') || s.includes('SCORED') || s.includes('DIAGNOSED')) {
    colorClasses = 'bg-blue-50 text-blue-700 border-blue-200 animate-pulse';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${colorClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5"></span>
      {s}
    </span>
  );
};

export default StatusBadge;
