import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useChatHistory } from '../contexts/ChatHistoryContext';

const ChatHistory: React.FC = () => {
  const { messages } = useChatHistory();
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    // 新しいメッセージが追加されたら自動スクロール
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography variant="body1" color="text.secondary">
          マイクボタンを押して会話を開始してください
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {messages.map((message) => (
        <Box
          key={message.id}
          sx={{
            display: 'flex',
            justifyContent: message.isUser ? 'flex-end' : 'flex-start',
          }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 2,
              maxWidth: '80%',
              backgroundColor: message.isUser ? 'primary.light' : 'grey.100',
              color: message.isUser ? 'white' : 'text.primary',
              borderRadius: 2,
            }}
          >
            <Typography variant="body1">{message.text}</Typography>
            <Typography variant="caption" color={message.isUser ? 'white' : 'text.secondary'} sx={{ display: 'block', mt: 1 }}>
              {message.timestamp.toLocaleTimeString()}
            </Typography>
          </Paper>
        </Box>
      ))}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatHistory; 