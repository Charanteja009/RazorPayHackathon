import React from 'react';
import { 
  LayoutDashboard, 
  ListOrdered, 
  GitMerge, 
  TrendingUp, 
  ShieldCheck, 
  Activity,
  RefreshCw
} from 'lucide-react';
import { reseedDemoData } from '../services/api';

export const Layout = ({ activeTab, setActiveTab, children }) => {
  const navItems = [
    { id: 'command-center', label: 'Command Center', icon: LayoutDashboard },
    { id: 'recovery-queue', label: 'Recovery Queue', icon: ListOrdered },
    { id: 'agent-timeline', label: 'Agent Timeline', icon: GitMerge },
    { id: 'revenue-analytics', label: 'Revenue Analytics', icon: TrendingUp },
    { id: 'audit-trail', label: 'Audit Trail', icon: ShieldCheck },
    { id: 'provider-health', label: 'AI Provider Health', icon: Activity },
  ];

  const handleReseed = async () => {
    try {
      await reseedDemoData();
      window.location.reload();
    } catch (e) {
      alert("Error resetting demo data: " + e.message);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      {/* White Minimalist Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 p-6 flex flex-col justify-between hidden md:flex">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center font-bold text-sm text-white shadow-sm">
              RZ
            </div>
            <div>
              <h1 className="font-bold text-sm text-slate-900 leading-tight">Razorpay</h1>
              <p className="text-[11px] text-blue-600 font-semibold">Track 03 • AI Recovery</p>
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive 
                      ? 'bg-slate-900 text-white font-semibold shadow-sm' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="pt-4 border-t border-slate-200">
          <button
            onClick={handleReseed}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset Demo Scenarios
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2 md:hidden">
            <div className="w-7 h-7 rounded-lg bg-slate-900 flex items-center justify-center font-bold text-white text-xs">
              RZ
            </div>
            <span className="font-bold text-xs text-slate-900">AI Revenue Recovery</span>
          </div>

          <div className="hidden md:block">
            <h2 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
              {navItems.find(n => n.id === activeTab)?.label || 'Dashboard'}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-medium bg-emerald-50 border border-emerald-200 text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              Razorpay Test Mode Active
            </span>
          </div>
        </header>

        {/* Mobile Nav Tabs */}
        <div className="flex md:hidden overflow-x-auto border-b border-slate-200 bg-white p-2 gap-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap font-medium ${
                activeTab === item.id ? 'bg-slate-900 text-white' : 'text-slate-600'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        <main className="flex-1 p-6 overflow-y-auto max-w-7xl w-full mx-auto space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
