import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDashboardSummary = async () => {
  const res = await api.get('/dashboard/summary');
  return res.data;
};

export const getRevenueAnalytics = async () => {
  const res = await api.get('/dashboard/revenue');
  return res.data;
};

export const getRecoveryQueue = async (statusFilter = null) => {
  const params = statusFilter ? { status_filter: statusFilter } : {};
  const res = await api.get('/recovery', { params });
  return res.data;
};

export const getTransactionDetail = async (transactionId) => {
  const res = await api.get(`/recovery/${transactionId}`);
  return res.data;
};

export const startRecoveryWorkflow = async (transactionId) => {
  const idempotencyKey = `ik_${transactionId}_${Date.now()}`;
  const res = await api.post(`/recovery/${transactionId}/start`, {}, {
    headers: { 'Idempotency-Key': idempotencyKey }
  });
  return res.data;
};

export const retryRecoveryAction = async (transactionId) => {
  const idempotencyKey = `ik_retry_${transactionId}_${Date.now()}`;
  const res = await api.post(`/recovery/${transactionId}/retry`, {}, {
    headers: { 'Idempotency-Key': idempotencyKey }
  });
  return res.data;
};

export const stopRecoveryAction = async (transactionId) => {
  const res = await api.post(`/recovery/${transactionId}/stop`);
  return res.data;
};

export const escalateRecoveryAction = async (transactionId) => {
  const res = await api.post(`/recovery/${transactionId}/escalate`);
  return res.data;
};

export const getAuditTrail = async (transactionId = null) => {
  const url = transactionId ? `/audit/${transactionId}` : '/audit';
  const res = await api.get(url);
  return res.data;
};

export const getAgentTimeline = async (transactionId) => {
  const res = await api.get(`/agents/${transactionId}`);
  return res.data;
};

export const getProviderHealth = async () => {
  const res = await api.get('/llm/providers');
  return res.data;
};

export const toggleLLMSimulation = async (openaiFail = null, allLlmFail = null) => {
  const res = await api.post('/llm/simulation', {
    simulate_openai_failure: openaiFail,
    simulate_all_llm_failure: allLlmFail
  });
  return res.data;
};

export const reseedDemoData = async () => {
  const res = await api.post('/seed/demo-scenarios');
  return res.data;
};

export default api;
