# 音声対話システム

## 概要

このプロジェクトは、リアルタイム音声対話システムのMVP（Minimum Viable Product）実装です。ユーザーの音声入力をテキストに変換し、AIによる応答を生成して音声で返すシステムを提供します。

## 主な機能

- プッシュ・トゥ・トーク方式のUI
- リアルタイム音声認識（ASR）
- 自然な対話応答生成（LLM）
- 音声合成（TTS）
- 会話履歴の保存と表示

## 技術スタック

### フロントエンド
- React
- TypeScript
- Material-UI
- Web Audio API
- WebSocket

### バックエンド
- Python
- FastAPI
- WebSocket
- asyncio

### 外部サービス
- Google Cloud Speech-to-Text (ASR)
- OpenAI GPT (対話生成)
- Google Cloud Text-to-Speech (TTS)

### データベース
- PostgreSQL

## セットアップ方法

### 前提条件
- Docker と Docker Compose がインストールされていること
- Google Cloud Platform のアカウントと認証情報
- OpenAI API キー

### 環境変数の設定
`.env` ファイルをプロジェクトのルートディレクトリに作成し、以下の環境変数を設定します：

OPENAI_API_KEY=your-openai-api-key 