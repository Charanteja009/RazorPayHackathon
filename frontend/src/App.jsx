import React, { useState } from 'react';
import Layout from './components/Layout';
import CommandCenter from './pages/CommandCenter';
import RecoveryQueue from './pages/RecoveryQueue';
import TransactionDetail from './pages/TransactionDetail';
import AgentTimeline from './pages/AgentTimeline';
import RevenueAnalytics from './pages/RevenueAnalytics';
import AuditTrail from './pages/AuditTrail';
import ProviderHealth from './pages/ProviderHealth';

export const App = () => {
  const [activeTab, setActiveTab] = useState('command-center');
  const [selectedTxId, setSelectedTxId] = useState(null);

  const handleSelectTransaction = (txId) => {
    setSelectedTxId(txId);
    setActiveTab('transaction-detail');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'command-center':
        return <CommandCenter onSelectTransaction={handleSelectTransaction} />;
      case 'recovery-queue':
        return <RecoveryQueue onSelectTransaction={handleSelectTransaction} />;
      case 'transaction-detail':
        return <TransactionDetail transactionId={selectedTxId} onBack={() => setActiveTab('recovery-queue')} />;
      case 'agent-timeline':
        return <AgentTimeline transactionId={selectedTxId} />;
      case 'revenue-analytics':
        return <RevenueAnalytics />;
      case 'audit-trail':
        return <AuditTrail transactionId={selectedTxId} />;
      case 'provider-health':
        return <ProviderHealth />;
      default:
        return <CommandCenter onSelectTransaction={handleSelectTransaction} />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
};

export default App;
