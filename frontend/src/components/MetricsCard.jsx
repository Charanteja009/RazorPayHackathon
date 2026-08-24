import React from 'react';

export const MetricsCard = ({ title, value, subtitle, icon: Icon, color = "dark" }) => {
  const colorStyles = {
    dark: "border-slate-200 text-slate-900 bg-white",
    blue: "border-blue-200 text-blue-900 bg-blue-50/30",
    emerald: "border-emerald-200 text-emerald-900 bg-emerald-50/30",
    amber: "border-amber-200 text-amber-900 bg-amber-50/30"
  };

  const iconStyles = {
    dark: "bg-slate-100 text-slate-700",
    blue: "bg-blue-100 text-blue-700",
    emerald: "bg-emerald-100 text-emerald-700",
    amber: "bg-amber-100 text-amber-700"
  };

  return (
    <div className={`p-5 rounded-2xl minimal-card border ${colorStyles[color] || colorStyles.dark}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-[11px] text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${iconStyles[color] || iconStyles.dark}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricsCard;
