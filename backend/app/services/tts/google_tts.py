import os
import logging
import base64
from google.cloud import texttospeech
import tempfile
import uuid

logger = logging.getLogger(__name__)

class GoogleTTS:
    def __init__(self):
        # 環境変数からGoogle Cloud認証情報を取得
        self.client = texttospeech.TextToSpeechClient()
        # 一時ファイルを保存するディレクトリ
        self.audio_dir = os.path.join(os.getcwd(), "audio_files")
        os.makedirs(self.audio_dir, exist_ok=True)
        logger.info("Google TTS service initialized")
    
    async def synthesize(self, text: str) -> str:
        """
        テキストを音声に変換する
        
        Args:
            text: 音声に変換するテキスト
        
        Returns:
            生成された音声ファイルのURL
        """
        try:
            # 音声合成リクエストの設定
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # 音声の設定
            voice = texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                name="ja-JP-Neural2-B",  # 自然な日本語音声
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # 音声ファイルの設定
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # 通常の速度
                pitch=0.0  # 通常のピッチ
            )
            
            # 音声合成の実行
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # 一時ファイルに保存
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            with open(filepath, "wb") as out:
                out.write(response.audio_content)
            
            # 実際の環境では、適切なURLを返す必要があります
            # ここでは簡易的に実装
            audio_url = f"/audio/{filename}"
            logger.info(f"Synthesized audio saved to {filepath}")
            
            return audio_url
        
        except Exception as e:
            logger.error(f"Error in TTS synthesis: {str(e)}")
            return "" 