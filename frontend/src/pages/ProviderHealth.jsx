import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, ShieldCheck, Zap, RefreshCw } from 'lucide-react';
import { getProviderHealth, toggleLLMSimulation } from '../services/api';

export const ProviderHealth = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const data = await getProviderHealth();
      setHealthData(data);
    } catch (e) {
      console.error("Provider health error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleToggle = async (openaiFail, allFail) => {
    setUpdating(true);
    try {
      await toggleLLMSimulation(openaiFail, allFail);
      await fetchHealth();
    } catch (e) {
      alert("Simulation error: " + e.message);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading AI Provider Health metrics...</div>;
  }

  const providers = healthData?.providers || [];
  const simState = healthData?.simulation_state || {};

  return (
    <div className="space-y-6">
      {/* Demo Controls Card */}
      <div className="minimal-card p-6 rounded-2xl space-y-4 border-l-4 border-l-slate-900">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-500" />
              Demo Failure Simulation Controls
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Toggle provider failure states to test automatic resilient fallback chains during hackathon judging.
            </p>
          </div>
          <button
            onClick={fetchHealth}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            onClick={() => handleToggle(true, false)}
            disabled={updating}
            className={`px-4 py-2.5 rounded-xl text-xs font-semibold border transition flex items-center gap-2 ${
              simState.simulate_openai_failure && !simState.simulate_all_llm_failure
                ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                : 'bg-white hover:bg-amber-50 text-amber-800 border-amber-200'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            Simulate OpenAI Failure (Groq Fallback)
          </button>

          <button
            onClick={() => handleToggle(true, true)}
            disabled={updating}
            className={`px-4 py-2.5 rounded-xl text-xs font-semibold border transition flex items-center gap-2 ${
              simState.simulate_all_llm_failure
                ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                : 'bg-white hover:bg-rose-50 text-rose-700 border-rose-200'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            Simulate All LLM Failure (Deterministic Rule Fallback)
          </button>

          <button
            onClick={() => handleToggle(false, false)}
            disabled={updating}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition flex items-center gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            Reset All Providers to Healthy
          </button>
        </div>
      </div>

      {/* Provider Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {providers.map((p) => {
          const isOk = p.healthy;
          return (
            <div key={p.name} className={`p-5 rounded-2xl minimal-card border ${isOk ? 'border-emerald-200' : 'border-rose-200'}`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-bold text-slate-900 text-base">{p.name}</h4>
                <span className={`w-2.5 h-2.5 rounded-full ${isOk ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Health Status:</span>
                  <span className={`font-semibold ${isOk ? 'text-emerald-700' : 'text-rose-600'}`}>{p.status}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Total Requests:</span>
                  <span className="font-mono text-slate-900">{p.request_count}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Fallback Triggers:</span>
                  <span className="font-mono text-amber-600">{p.fallback_count}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Resilient Chain Diagram */}
      <div className="minimal-card p-6 rounded-2xl">
        <h3 className="text-base font-semibold text-slate-900 mb-3">Resilient LLM Fallback Sequence</h3>
        <p className="text-xs text-slate-500 mb-6">
          If any provider encounters API error, timeout, rate limit, or invalid JSON output, the system automatically cascades down the chain without breaking the financial recovery workflow.
        </p>

        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center text-xs">
          <div className="flex-1 p-4 rounded-xl bg-slate-50 border border-blue-200 w-full">
            <span className="text-blue-700 font-bold block">1. OpenAI</span>
            <span className="text-slate-500 text-[10px]">gpt-4o-mini</span>
          </div>
          <span className="text-slate-400 font-bold">→</span>
          <div className="flex-1 p-4 rounded-xl bg-slate-50 border border-purple-200 w-full">
            <span className="text-purple-700 font-bold block">2. Groq</span>
            <span className="text-slate-500 text-[10px]">llama-3.3-70b-versatile</span>
          </div>
          <span className="text-slate-400 font-bold">→</span>
          <div className="flex-1 p-4 rounded-xl bg-slate-50 border border-amber-200 w-full">
            <span className="text-amber-700 font-bold block">3. Ollama</span>
            <span className="text-slate-500 text-[10px]">local llama3</span>
          </div>
          <span className="text-slate-400 font-bold">→</span>
          <div className="flex-1 p-4 rounded-xl bg-emerald-50 border border-emerald-200 w-full">
            <span className="text-emerald-700 font-bold block">4. Deterministic Guardrail</span>
            <span className="text-emerald-600 text-[10px]">Server-Side Conservative Policy</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProviderHealth;
