import os
import logging
import openai
import asyncio
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OpenAILLM:
    def __init__(self):
        # OpenAI APIキーを環境変数から取得
        openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key")
        logger.info("OpenAI LLM service initialized")
    
    async def generate_response(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        会話履歴に基づいて応答を生成する
        
        Args:
            conversation_history: 会話履歴のリスト
        
        Returns:
            生成された応答テキスト
        """
        try:
            # システムメッセージを追加
            messages = [
                {"role": "system", "content": "あなたは親切で丁寧な日本語アシスタントです。簡潔かつ役立つ回答を提供してください。"}
            ]
            
            # 会話履歴を追加
            messages.extend(conversation_history)
            
            # OpenAI APIを非同期で呼び出す
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            
            # 応答テキストを取得
            response_text = response.choices[0].message.content.strip()
            logger.info(f"Generated response: {response_text}")
            return response_text
        
        except Exception as e:
            logger.error(f"Error in LLM response generation: {str(e)}")
            return "申し訳ありません、応答の生成中にエラーが発生しました。" 