
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import ChatHeader from '@/components/chat/ChatHeader';
import ChatMessageList from '@/components/chat/ChatMessageList';
import ChatInput from '@/components/chat/ChatInput';
import { useTranslation } from '@/hooks/useTranslation';

interface ChatProps {
  onNavigate: (page: string) => void;
  ragId?: string;
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  sources?: string[];
}

const Chat: React.FC<ChatProps> = ({ onNavigate, ragId }) => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: t('chat.welcomeMessage'),
      sender: 'ai',
      timestamp: new Date(),
      sources: []
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Mock RAG data
  const ragData = {
    name: ragId === 'new' ? 'New RAG' : 'Company Handbook',
    description: 'HR policies and procedures',
    documentCount: ragId === 'new' ? 0 : 5
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: t('chat.simulatedResponse'),
        sender: 'ai',
        timestamp: new Date(),
        sources: ['Document 1.pdf', 'Company Policy.pdf']
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <ChatHeader ragData={ragData} onNavigate={onNavigate} />

      <div className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 flex flex-col">
        <Card className="flex-1 border-border flex flex-col">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg text-foreground">{t('chat.title')}</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0">
            <ChatMessageList
              messages={messages}
              isLoading={isLoading}
              onCopyMessage={copyMessage}
            />
            <ChatInput
              value={inputValue}
              onChange={setInputValue}
              onSubmit={handleSendMessage}
              isLoading={isLoading}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Chat;
