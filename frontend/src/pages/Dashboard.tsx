import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, MessageSquare, FileText, Trash2, Settings, LogOut, Bot, Brain, Zap, Globe } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from '@/hooks/useTranslation';

interface DashboardProps {
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

// Mock data for AI Agents
const mockAgents = [
  {
    id: 1,
    name: "Company Knowledge Assistant",
    description: "HR policies and procedures specialist",
    documentCount: 5,
    lastUsed: "2 hours ago",
    status: "active"
  },
  {
    id: 2,
    name: "Product Documentation Expert",
    description: "Technical specs and API documentation expert",
    documentCount: 12,
    lastUsed: "1 day ago",
    status: "active"
  },
  {
    id: 3,
    name: "Research Assistant",
    description: "AI and machine learning research specialist",
    documentCount: 8,
    lastUsed: "3 days ago",
    status: "training"
  }
];

const Dashboard: React.FC<DashboardProps> = ({ onNavigate, onLogout }) => {
  const { t, language, changeLanguage } = useTranslation();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
                <Bot className="h-6 w-6 text-background" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">{t('app.name')}</h1>
                <p className="text-sm text-muted-foreground">{t('app.description')}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => changeLanguage(language === 'en' ? 'fr' : 'en')}
              >
                <Globe className="h-4 w-4" />
                {language === 'en' ? 'FR' : 'EN'}
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
                {t('dashboard.settings')}
              </Button>
              <Button variant="ghost" size="sm" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
                {t('dashboard.logout')}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-primary/10 via-accent/5 to-success/10 rounded-2xl p-6 border border-border">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">
                  {t('dashboard.welcome')}
                </h2>
                <p className="text-muted-foreground">
                  {t('dashboard.agentCount', { count: mockAgents.length })}
                </p>
              </div>
              <Button 
                variant="hero" 
                size="lg"
                onClick={() => onNavigate('create')}
                className="whitespace-nowrap"
              >
                <Plus className="h-5 w-5" />
                {t('createAgent.createAgent')}
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('dashboard.totalAgents')}
                </CardTitle>
                <Brain className="h-4 w-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{mockAgents.length}</div>
              <p className="text-xs text-muted-foreground">
                +1 from last week
              </p>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('dashboard.documents')}
                </CardTitle>
                <FileText className="h-4 w-4 text-accent" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">
                {mockAgents.reduce((acc, agent) => acc + agent.documentCount, 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                Across all agents
              </p>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('dashboard.activeChats')}
                </CardTitle>
                <MessageSquare className="h-4 w-4 text-success" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">
                {mockAgents.filter(agent => agent.status === 'active').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Ready to use
              </p>
            </CardContent>
          </Card>
        </div>

        {/* AI Agents Grid */}
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-foreground">{t('dashboard.myAgents')}</h3>
            <Button variant="outline" onClick={() => onNavigate('create')}>
              <Plus className="h-4 w-4" />
              {t('dashboard.addNew')}
            </Button>
          </div>

          {mockAgents.length === 0 ? (
            <Card className="border-dashed border-2 border-muted">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Bot className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {t('dashboard.noAgents')}
                </h3>
                <p className="text-muted-foreground text-center mb-4 max-w-sm">
                  {t('dashboard.noAgentsDesc')}
                </p>
                <Button variant="hero" onClick={() => onNavigate('create')}>
                  <Plus className="h-4 w-4" />
                  {t('dashboard.createFirst')}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockAgents.map((agent) => (
                <Card key={agent.id} className="border-border hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 group">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg text-foreground group-hover:text-primary transition-colors">
                        {agent.name}
                      </CardTitle>
                      <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                        {agent.status === 'active' ? (
                          <>
                            <Zap className="h-3 w-3 mr-1" />
                            {t('common.active')}
                          </>
                        ) : (
                          <>
                            <Brain className="h-3 w-3 mr-1" />
                            {t('common.training')}
                          </>
                        )}
                      </Badge>
                    </div>
                    <CardDescription className="text-muted-foreground">
                      {agent.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{t('dashboard.documentsCount')}</span>
                      <span className="font-medium text-foreground">{agent.documentCount}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{t('dashboard.lastUsed')}</span>
                      <span className="font-medium text-foreground">{agent.lastUsed}</span>
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button 
                        variant="default" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => onNavigate(`chat/${agent.id}`)}
                        disabled={agent.status !== 'active'}
                      >
                        <MessageSquare className="h-4 w-4" />
                        {t('dashboard.chat')}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => onNavigate(`config/${agent.id}`)}
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        className="text-destructive hover:text-destructive-foreground hover:bg-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;