import os
import logging
from google.cloud import speech
import io

logger = logging.getLogger(__name__)

class GoogleASR:
    def __init__(self):
        # 環境変数からGoogle Cloud認証情報を取得
        # 実際の環境では、適切な認証情報を設定する必要があります
        self.client = speech.SpeechClient()
        logger.info("Google ASR service initialized")
    
    async def transcribe(self, audio_data: bytes) -> str:
        """
        音声データをテキストに変換する
        
        Args:
            audio_data: 音声データのバイト列
        
        Returns:
            認識されたテキスト
        """
        try:
            # 音声認識リクエストの設定
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="ja-JP",
                enable_automatic_punctuation=True,
            )
            
            # 音声認識の実行
            response = self.client.recognize(config=config, audio=audio)
            
            # 結果の処理
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript
            
            logger.info(f"Transcribed text: {transcript}")
            return transcript
        
        except Exception as e:
            logger.error(f"Error in ASR transcription: {str(e)}")
            return ""

    async def transcribe_streaming(self, audio_stream):
        """
        ストリーミング音声をテキストに変換する
        
        Args:
            audio_stream: 音声データのストリーム
        
        Returns:
            認識されたテキスト
        """
        try:
            # ストリーミング認識の設定
            requests = (
                speech.StreamingRecognizeRequest(
                    audio_content=chunk
                )
                for chunk in audio_stream
            )
            
            streaming_config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="ja-JP",
                    enable_automatic_punctuation=True,
                ),
                interim_results=True,
            )
            
            # ストリーミング認識の実行
            responses = self.client.streaming_recognize(
                config=streaming_config,
                requests=requests,
            )
            
            # 結果の処理
            for response in responses:
                for result in response.results:
                    if result.is_final:
                        return result.alternatives[0].transcript
            
            return ""
        
        except Exception as e:
            logger.error(f"Error in ASR streaming transcription: {str(e)}")
            return "" 