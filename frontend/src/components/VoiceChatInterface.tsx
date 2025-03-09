import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, IconButton, Typography, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import { useChatHistory } from '../contexts/ChatHistoryContext';
import ChatHistory from './ChatHistory';
import { processAudio } from '../services/audioService';

const VoiceChatInterface: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const { addMessage } = useChatHistory();

  // WebSocketの接続を管理
  const socketRef = useRef<WebSocket | null>(null);

  // 状態の追加
  const [asrResult, setAsrResult] = useState<string | null>(null);
  const [isAiResponding, setIsAiResponding] = useState(false);

  useEffect(() => {
    // WebSocketの初期化
    const socket = new WebSocket('ws://localhost:8000/ws/audio');
    
    socket.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    socket.onmessage = (event) => {
      const response = JSON.parse(event.data);
      
      if (response.type === 'asr_result') {
        setAsrResult(response.text);
        addMessage({
          text: response.text,
          isUser: true,
        });
      } else if (response.type === 'llm_response') {
        setIsAiResponding(true);
        addMessage({
          text: response.text,
          isUser: false,
        });
      } else if (response.type === 'tts_audio') {
        const audio = new Audio(response.audio_url);
        audio.onended = () => {
          setIsAiResponding(false);
        };
        audio.play();
      } else if (response.type === 'error') {
        setError(response.message);
        setIsAiResponding(false);
      }
    };
    
    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };
    
    socketRef.current = socket;
    
    return () => {
      socket.close();
    };
  }, [addMessage]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // AudioContextを作成して適切なサンプルレートを設定
      const audioContext = new AudioContext({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          
          // WebSocketが接続されている場合、音声データを送信
          if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(event.data);
          }
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setIsProcessing(true);
        
        try {
          // 録音終了時の処理
          await processAudio(audioBlob);
        } catch (err) {
          setError('音声処理中にエラーが発生しました');
          console.error(err);
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start(100); // 100msごとにデータを送信
      setIsRecording(true);
    } catch (err) {
      setError('マイクへのアクセスが拒否されました');
      console.error(err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // 録音停止を通知
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'recording_stopped' }));
      }
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          mb: 2, 
          p: 2, 
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <ChatHistory />
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 2 }}>
        {error && (
          <Typography color="error" variant="body2" sx={{ mb: 1 }}>
            {error}
          </Typography>
        )}
        
        <IconButton 
          color="primary" 
          size="large" 
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          sx={{ 
            width: 80, 
            height: 80, 
            border: '2px solid', 
            borderColor: isRecording ? 'error.main' : 'primary.main',
            color: isRecording ? 'error.main' : 'primary.main',
          }}
        >
          {isProcessing ? (
            <CircularProgress size={40} />
          ) : isRecording ? (
            <StopIcon fontSize="large" />
          ) : (
            <MicIcon fontSize="large" />
          )}
        </IconButton>
      </Box>
      
      {asrResult && (
        <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
          認識結果: {asrResult}
        </Typography>
      )}
      
      {isAiResponding && (
        <Typography variant="body2" color="primary" sx={{ mt: 1, textAlign: 'center' }}>
          AIが応答中...
        </Typography>
      )}
    </Box>
  );
};

export default VoiceChatInterface; 