import logging
import json
import os
import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ConversationLogger:
    def __init__(self):
        # ログを保存するディレクトリ
        self.log_dir = os.path.join(os.getcwd(), "conversation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        logger.info("Conversation logger initialized")
    
    async def log_message(self, session_id: str, role: str, content: str) -> None:
        """
        メッセージをログに記録する
        
        Args:
            session_id: セッションID
            role: メッセージの送信者（"user" または "assistant"）
            content: メッセージの内容
        """
        try:
            # ログファイルのパス
            log_file = os.path.join(self.log_dir, f"{session_id}.jsonl")
            
            # メッセージデータの作成
            message_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "role": role,
                "content": content
            }
            
            # ログファイルに追記
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(message_data, ensure_ascii=False) + "\n")
            
            logger.info(f"Logged message for session {session_id}")
        
        except Exception as e:
            logger.error(f"Error logging message: {str(e)}")
    
    async def save_conversation(self, session_id: str, conversation: List[Dict[str, Any]]) -> None:
        """
        会話全体を保存する
        
        Args:
            session_id: セッションID
            conversation: 会話履歴
        """
        try:
            # 会話ファイルのパス
            conversation_file = os.path.join(self.log_dir, f"{session_id}_full.json")
            
            # 会話データの作成
            conversation_data = {
                "session_id": session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "conversation": conversation
            }
            
            # 会話ファイルに保存
            with open(conversation_file, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved full conversation for session {session_id}")
        
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}") 