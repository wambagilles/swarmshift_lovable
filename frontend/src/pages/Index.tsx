import React, { useState } from 'react';
import Auth from './Auth';
import Dashboard from './Dashboard';
import CreateRag from './CreateRag';
import Chat from './Chat';
import AgentConfig from './AgentConfig';

const Index = () => {
  const [currentPage, setCurrentPage] = useState<string>('auth');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentPage('auth');
  };

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
  };

  // Route rendering logic
  const renderCurrentPage = () => {
    if (!isAuthenticated) {
      return <Auth onLogin={handleLogin} />;
    }

    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={handleNavigate} onLogout={handleLogout} />;
      case 'create':
        return <CreateRag onNavigate={handleNavigate} />;
      case 'chat/new':
      case 'chat/1':
      case 'chat/2':
      case 'chat/3':
        const ragId = currentPage.split('/')[1];
        return <Chat onNavigate={handleNavigate} ragId={ragId} />;
      case 'config/1':
      case 'config/2':
      case 'config/3':
        const configAgentId = currentPage.split('/')[1];
        return <AgentConfig onNavigate={handleNavigate} agentId={configAgentId} />;
      default:
        return <Dashboard onNavigate={handleNavigate} onLogout={handleLogout} />;
    }
  };

  return renderCurrentPage();
};

export default Index;
