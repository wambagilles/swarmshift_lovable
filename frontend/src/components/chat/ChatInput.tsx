
import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send } from 'lucide-react';
import { useTranslation } from '@/hooks/useTranslation';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  value, 
  onChange, 
  onSubmit, 
  isLoading 
}) => {
  const { t } = useTranslation();

  return (
    <div className="border-t border-border p-6">
      <form onSubmit={onSubmit} className="flex gap-2">
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={t('chat.askQuestion')}
          disabled={isLoading}
          className="flex-1"
        />
        <Button 
          type="submit" 
          disabled={!value.trim() || isLoading}
          variant="default"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
      <p className="text-xs text-muted-foreground mt-2">
        {t('chat.askQuestionHelp')}
      </p>
    </div>
  );
};

export default ChatInput;
