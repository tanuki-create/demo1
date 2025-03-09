import axios from 'axios';

// 音声データをバックエンドに送信して処理する
export const processAudio = async (audioBlob: Blob): Promise<void> => {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    await axios.post('http://localhost:8000/api/process-audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  } catch (error) {
    console.error('Error processing audio:', error);
    throw new Error('Failed to process audio');
  }
};

// 音声をバイナリデータに変換する
export const convertAudioToBlob = (audioChunks: Blob[]): Blob => {
  return new Blob(audioChunks, { type: 'audio/wav' });
};

// 音声をBase64に変換する
export const convertBlobToBase64 = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      resolve(base64String.split(',')[1]); // Remove the data URL prefix
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}; 