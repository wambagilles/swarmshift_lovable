
import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Bot } from 'lucide-react';
import { useTranslation } from '@/hooks/useTranslation';
import LanguageToggle from './LanguageToggle';

interface ChatHeaderProps {
  ragData: {
    name: string;
    description: string;
    documentCount: number;
  };
  onNavigate: (page: string) => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ ragData, onNavigate }) => {
  const { t } = useTranslation();

  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => onNavigate('dashboard')}
            >
              <ArrowLeft className="h-4 w-4" />
              {t('chat.backToAgents')}
            </Button>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
                <Bot className="h-5 w-5 text-background" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-foreground">{ragData.name}</h1>
                <p className="text-sm text-muted-foreground">
                  {ragData.documentCount} {t('dashboard.documents').toLowerCase()} • {ragData.description}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant="default" className="bg-success text-success-foreground">
              {t('chat.online')}
            </Badge>
            <LanguageToggle />
          </div>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
