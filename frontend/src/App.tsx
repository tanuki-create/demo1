import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import VoiceChatInterface from './components/VoiceChatInterface';
import ChatHistoryProvider from './contexts/ChatHistoryContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ChatHistoryProvider>
        <Container maxWidth="md">
          <Box sx={{ my: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              音声対話システム
            </Typography>
            <VoiceChatInterface />
          </Box>
        </Container>
      </ChatHistoryProvider>
    </ThemeProvider>
  );
}

export default App;
