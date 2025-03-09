from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import List, Dict, Any
import uuid
import json  # WebSocketメッセージのJSONパース用
from fastapi.staticfiles import StaticFiles

from app.services.asr.google_asr import GoogleASR
from app.services.llm.openai_llm import OpenAILLM
from app.services.tts.google_tts import GoogleTTS
from app.services.log.conversation_logger import ConversationLogger
from app.core.database import Base, engine, get_db

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Chat API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# サービスのインスタンス化
asr_service = GoogleASR()
llm_service = OpenAILLM()
tts_service = GoogleTTS()
logger_service = ConversationLogger()

# アクティブな接続を追跡
active_connections: Dict[str, WebSocket] = {}

# 会話履歴を保持
conversation_history: Dict[str, List[Dict[str, Any]]] = {}

# 音声ファイル用のディレクトリをマウント
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

@app.get("/")
async def root():
    return {"message": "Voice Chat API is running"}

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket接続を受け入れる
    await websocket.accept()
    
    # 一意のセッションIDを生成
    session_id = str(uuid.uuid4())
    active_connections[session_id] = websocket
    
    # 会話履歴の初期化
    conversation_history[session_id] = []
    
    try:
        while True:
            try:
                # テキストメッセージを受信
                message = await websocket.receive_text()
                message_json = json.loads(message)
                
                if message_json.get("type") == "recording_stopped":
                    logger.info(f"Recording stopped for session {session_id}")
                    continue
            except Exception:
                # バイナリデータを受信
                try:
                    audio_data = await websocket.receive_bytes()
                    
                    try:
                        # 1. ASRで音声をテキストに変換
                        text = await asr_service.transcribe(audio_data)
                        
                        if text:
                            # ASR結果をクライアントに送信
                            await websocket.send_json({
                                "type": "asr_result",
                                "text": text
                            })
                            
                            # 会話履歴に追加
                            conversation_history[session_id].append({
                                "role": "user",
                                "content": text
                            })
                            
                            # ログに保存
                            await logger_service.log_message(session_id, "user", text)
                            
                            # 2. LLMで応答を生成
                            response = await llm_service.generate_response(conversation_history[session_id])
                            
                            # LLM応答をクライアントに送信
                            await websocket.send_json({
                                "type": "llm_response",
                                "text": response
                            })
                            
                            # 会話履歴に追加
                            conversation_history[session_id].append({
                                "role": "assistant",
                                "content": response
                            })
                            
                            # ログに保存
                            await logger_service.log_message(session_id, "assistant", response)
                            
                            # 3. TTSで音声を生成
                            audio_url = await tts_service.synthesize(response)
                            
                            # TTS音声URLをクライアントに送信
                            await websocket.send_json({
                                "type": "tts_audio",
                                "audio_url": audio_url
                            })
                    
                    except Exception as e:
                        logger.error(f"Error processing audio: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"処理中にエラーが発生しました: {str(e)}"
                        })
                except Exception as e:
                    logger.error(f"Error receiving data: {str(e)}")
    
    except WebSocketDisconnect:
        # WebSocket接続が切断された場合
        logger.info(f"Client disconnected: {session_id}")
        
        # クリーンアップ
        if session_id in active_connections:
            del active_connections[session_id]
        
        if session_id in conversation_history:
            # 会話履歴を完全に保存
            await logger_service.save_conversation(session_id, conversation_history[session_id])
            del conversation_history[session_id]
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        
        # クリーンアップ
        if session_id in active_connections:
            del active_connections[session_id]
        
        if session_id in conversation_history:
            del conversation_history[session_id]

@app.post("/api/process-audio")
async def process_audio(audio: UploadFile = File(...)):
    try:
        # 音声ファイルを読み込む
        audio_data = await audio.read()
        
        # 1. ASRで音声をテキストに変換
        text = await asr_service.transcribe(audio_data)
        
        if not text:
            raise HTTPException(status_code=400, detail="音声からテキストを抽出できませんでした")
        
        # 一時的なセッションID（REST API用）
        session_id = f"rest-{uuid.uuid4()}"
        
        # 2. LLMで応答を生成
        history = [{"role": "user", "content": text}]
        response = await llm_service.generate_response(history)
        
        # 3. TTSで音声を生成
        audio_url = await tts_service.synthesize(response)
        
        # ログに保存
        await logger_service.log_message(session_id, "user", text)
        await logger_service.log_message(session_id, "assistant", response)
        
        return {
            "asr_result": text,
            "llm_response": response,
            "tts_audio_url": audio_url
        }
    
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"音声処理中にエラーが発生しました: {str(e)}")

# アプリケーション起動時にデータベースを初期化
@app.on_event("startup")
async def startup():
    # データベーステーブルの作成
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 