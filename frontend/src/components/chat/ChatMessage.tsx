
import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, User, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTranslation } from '@/hooks/useTranslation';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  sources?: string[];
}

interface ChatMessageProps {
  message: Message;
  onCopyMessage: (content: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onCopyMessage }) => {
  const { t } = useTranslation();

  return (
    <div
      className={`flex gap-3 ${
        message.sender === 'user' ? 'justify-end' : 'justify-start'
      }`}
    >
      {message.sender === 'ai' && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
          <Bot className="h-4 w-4 text-background" />
        </div>
      )}
      
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          message.sender === 'user'
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-border/20">
            <p className="text-xs text-muted-foreground mb-2">{t('chat.sources')}</p>
            <div className="flex flex-wrap gap-1">
              {message.sources.map((source, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="text-xs"
                >
                  {source}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {message.sender === 'ai' && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/20">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCopyMessage(message.content)}
              className="h-6 px-2"
            >
              <Copy className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2">
              <ThumbsUp className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-6 px-2">
              <ThumbsDown className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>
      
      {message.sender === 'user' && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
          <User className="h-4 w-4 text-secondary-foreground" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
