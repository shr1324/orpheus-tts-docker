# Orpheus TTS Docker デプロイメント

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Image](https://img.shields.io/badge/docker-neosun%2Forpheus--tts-blue)](https://hub.docker.com/r/neosun/orpheus-tts)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange)](https://github.com/neosun100/orpheus-tts-docker/releases)

GPU管理、マルチアクセスモード、最適化されたパフォーマンスを備えた、本番環境対応のOrpheus TTS Dockerデプロイメント。

## ✨ 機能

- 🐳 **Dockerコンテナ化**：CUDA 12.1サポートでワンコマンドデプロイ
- 🎯 **インテリジェントGPU管理**：遅延ロード + 自動アンロード（1時間タイムアウト）
- 🌐 **3つのアクセスモード**：Web UI、REST API、MCP（Model Context Protocol）
- 🚀 **最適化されたパフォーマンス**：モデルロード後の推論は約2.5秒
- 🔒 **本番環境対応**：SSL対応のNginxリバースプロキシ
- 🎨 **モダンなWeb UI**：ダークテーマと中英切り替え
- 📊 **APIドキュメント**：組み込みSwagger UI
- 🎤 **8つの音声オプション**：tara, leah, jess, leo, dan, mia, zac, zoe

## 🚀 クイックスタート

### 前提条件

- Docker 20.10+ と nvidia-docker2
- 40GB以上のVRAMを持つNVIDIA GPU（例：L40S、A100）
- CUDA 12.1+互換ドライバ
- [orpheus-3b-0.1-ft](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)へのアクセス権を持つHuggingFaceアカウント

### 方法1：Docker Run（最速）

```bash
# HuggingFaceトークンを設定
export HF_TOKEN=your_huggingface_token

# プルして実行
docker pull neosun/orpheus-tts:v1.0.0-allinone

docker run -d \
  --name orpheus-tts \
  --gpus '"device=0"' \
  -p 8899:8899 \
  -e HF_TOKEN=$HF_TOKEN \
  -v $(pwd)/outputs:/app/outputs \
  --restart unless-stopped \
  neosun/orpheus-tts:v1.0.0-allinone

# サービスの起動を待つ（約30秒）
sleep 30

# ヘルスチェック
curl http://localhost:8899/health
```

### 方法2：Docker Compose（推奨）

1. リポジトリをクローン：
```bash
git clone https://github.com/neosun100/orpheus-tts-docker.git
cd orpheus-tts-docker
```

2. `.env`ファイルを作成：
```bash
cp .env.example .env
# .envを編集してHF_TOKENを設定
```

3. サービスを起動：
```bash
docker compose up -d
```

## 📖 使用方法

### Web UI

ブラウザで以下にアクセス：
```
http://localhost:8899
```

### REST API

#### 音声生成

```bash
curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "こんにちは、これはテストです。",
    "voice": "tara",
    "model_size": "medium"
  }' \
  --output output.wav
```

#### APIドキュメント

インタラクティブなSwagger UI：
```
http://localhost:8899/docs
```

## ⚙️ 設定

### 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `PORT` | 8899 | サービスポート |
| `GPU_IDLE_TIMEOUT` | 3600 | モデルアンロードタイムアウト（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPUデバイスID |
| `HF_TOKEN` | - | HuggingFaceトークン（必須） |

## 🛠️ 技術スタック

- **ベース**：Python 3.10、CUDA 12.1
- **MLフレームワーク**：PyTorch 2.5.1、vLLM 0.7.3
- **Webフレームワーク**：Flask 3.0.0
- **モデル**：Orpheus TTS（canopylabs/orpheus-3b-0.1-ft）
- **コンテナ**：Docker、Docker Compose

## 📊 パフォーマンスベンチマーク

| メトリック | 値 |
|-----------|-----|
| 初回リクエスト | 約48秒 |
| 以降のリクエスト | 約2.5秒 |
| ストリーミングレイテンシ | 約200ms |
| VRAM使用量 | 約39GB |

## 🤝 コントリビューション

コントリビューションを歓迎します！お気軽にPull Requestを送信してください。

## 📝 変更履歴

### v1.0.0（2025-12-13）
- ✅ 初期Dockerデプロイメント
- ✅ GPU管理と遅延ロード
- ✅ 3つのアクセスモード（Web UI、REST API、MCP）
- ✅ Nginxリバースプロキシサポート
- ✅ パフォーマンス最適化
- ✅ Docker Hubイメージ：neosun/orpheus-tts:v1.0.0-allinone

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。

## 🙏 謝辞

- [Canopy Labs](https://canopylabs.ai/) - 素晴らしいOrpheus TTSモデル
- [vLLM](https://github.com/vllm-project/vllm) - 効率的な推論
- オリジナルOrpheus TTS：https://github.com/canopyai/Orpheus-TTS

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/orpheus-tts-docker&type=Date)](https://star-history.com/#neosun100/orpheus-tts-docker)

## 📱 フォローする

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**❤️で作られました**
