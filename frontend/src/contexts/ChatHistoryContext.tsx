import React, { createContext, useState, useContext, ReactNode } from 'react';

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  audioUrl?: string;
}

interface ChatHistoryContextType {
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearHistory: () => void;
}

const ChatHistoryContext = createContext<ChatHistoryContextType | undefined>(undefined);

export const useChatHistory = () => {
  const context = useContext(ChatHistoryContext);
  if (!context) {
    throw new Error('useChatHistory must be used within a ChatHistoryProvider');
  }
  return context;
};

interface ChatHistoryProviderProps {
  children: ReactNode;
}

const ChatHistoryProvider: React.FC<ChatHistoryProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  };

  const clearHistory = () => {
    setMessages([]);
  };

  return (
    <ChatHistoryContext.Provider value={{ messages, addMessage, clearHistory }}>
      {children}
    </ChatHistoryContext.Provider>
  );
};

export default ChatHistoryProvider; 