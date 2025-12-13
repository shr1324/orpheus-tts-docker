# Orpheus TTS Docker Deployment

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Image](https://img.shields.io/badge/docker-neosun%2Forpheus--tts-blue)](https://hub.docker.com/r/neosun/orpheus-tts)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.5.0-orange)](https://github.com/neosun100/orpheus-tts-docker/releases)

Production-ready Docker deployment for Orpheus TTS with GPU management, multi-access modes, and optimized performance.

## ✨ Features

- 🐳 **Docker Containerization**: One-command deployment with CUDA 12.1 support
- 🎯 **Intelligent GPU Management**: Lazy loading + automatic unloading (1-hour timeout)
- 🌐 **Three Access Modes**: Web UI, REST API, and MCP (Model Context Protocol)
- 🚀 **Optimized Performance**: ~2.5s inference after model loading
- 🔒 **Production Ready**: Nginx reverse proxy with SSL support
- 🔐 **Privacy Protection**: All audio files saved to host `/tmp/orpheus-tts`, no data retained in container
- 🎨 **Modern Web UI**: Dark theme with Chinese/English toggle
- 📊 **API Documentation**: Built-in Swagger UI
- 🎤 **8 Voice Options**: tara, leah, jess, leo, dan, mia, zac, zoe

## 🎯 Model Information

- **Model**: canopylabs/orpheus-3b-0.1-ft
- **Precision**: bfloat16 (full precision)
- **Parameters**: 3B (3 billion)
- **VRAM Usage**: ~39GB (gpu_memory_utilization=0.7)
- **Performance**: 
  - First request: ~48s (model loading)
  - Subsequent requests: ~2.5s
  - Streaming latency: ~200ms

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ with nvidia-docker2
- NVIDIA GPU with 40GB+ VRAM (e.g., L40S, A100)
- CUDA 12.1+ compatible driver
- HuggingFace account with access to [orpheus-3b-0.1-ft](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)

### Method 1: Docker Run (Fastest)

```bash
# Set your HuggingFace token
export HF_TOKEN=your_huggingface_token

# Pull and run
docker pull neosun/orpheus-tts:v1.5.0-allinone

docker run -d \
  --name orpheus-tts \
  --gpus '"device=0"' \
  -p 8899:8899 \
  -e HF_TOKEN=$HF_TOKEN \
  -v /tmp/orpheus-tts:/app/outputs \
  --restart unless-stopped \
  neosun/orpheus-tts:v1.5.0-allinone

# Wait for service to start (~30 seconds)
sleep 30

# Check health
curl http://localhost:8899/health
```

### Method 2: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/neosun100/orpheus-tts-docker.git
cd orpheus-tts-docker
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and set your HF_TOKEN
```

3. Start the service:
```bash
docker compose up -d
```

4. Verify:
```bash
# Check container status
docker compose ps

# Check health
curl http://localhost:8899/health
```

## 📖 Usage

### Web UI

Open your browser and navigate to:
```
http://localhost:8899
```

Features:
- Text input with voice selection
- Real-time audio generation
- Download generated audio
- Dark theme with language toggle

### REST API

#### Generate Speech

```bash
curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is a test.",
    "voice": "tara",
    "model_size": "medium"
  }' \
  --output output.wav
```

#### API Documentation

Interactive Swagger UI available at:
```
http://localhost:8899/docs
```

#### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/generate` | POST | Generate speech |
| `/api/voices` | GET | List available voices |
| `/api/models` | GET | List available models |
| `/gpu/status` | GET | GPU status |
| `/gpu/offload` | POST | Offload model from GPU |

### MCP (Model Context Protocol)

For AI assistants and automation tools:

```json
{
  "mcpServers": {
    "orpheus-tts": {
      "command": "docker",
      "args": ["exec", "-i", "orpheus-tts", "python", "/app/mcp_server.py"]
    }
  }
}
```

Available MCP tools:
- `generate_speech`: Generate speech from text
- `get_gpu_status`: Check GPU memory usage
- `offload_gpu`: Free GPU memory
- `list_models`: List available models

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8899 | Service port |
| `GPU_IDLE_TIMEOUT` | 3600 | Model unload timeout (seconds) |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID |
| `HF_TOKEN` | - | HuggingFace token (required) |

### docker-compose.yml

```yaml
version: '3.8'

services:
  orpheus-tts:
    image: neosun/orpheus-tts:v1.0.0-bfloat16-3b-allinone
    container_name: orpheus-tts
    environment:
      - PORT=${PORT:-8899}
      - GPU_IDLE_TIMEOUT=${GPU_IDLE_TIMEOUT:-3600}
      - HF_TOKEN=${HF_TOKEN}
    ports:
      - "0.0.0.0:${PORT:-8899}:${PORT:-8899}"
    volumes:
      - ./outputs:/app/outputs
      - huggingface_cache:/root/.cache/huggingface
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['${NVIDIA_VISIBLE_DEVICES:-0}']
              capabilities: [gpu]

volumes:
  huggingface_cache:
```

## 📁 Project Structure

```
orpheus-tts-docker/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration config
├── server.py              # Flask web server
├── mcp_server.py          # MCP interface
├── gpu_manager.py         # GPU management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── outputs/               # Generated audio files
└── docs/                  # Documentation
    ├── ARCHITECTURE.md
    ├── DOCKER_DEPLOYMENT.md
    ├── MCP_GUIDE.md
    └── QUANTIZED_MODELS.md
```

## 🛠️ Tech Stack

- **Base**: Python 3.10, CUDA 12.1
- **ML Framework**: PyTorch 2.5.1, vLLM 0.7.3
- **Web Framework**: Flask 3.0.0
- **Model**: Orpheus TTS (canopylabs/orpheus-3b-0.1-ft)
- **Container**: Docker, Docker Compose
- **GPU**: NVIDIA CUDA with nvidia-docker2

## 🔧 Advanced Usage

### Custom GPU Selection

```bash
# Use GPU 2
docker run -d \
  --gpus '"device=2"' \
  -e NVIDIA_VISIBLE_DEVICES=2 \
  neosun/orpheus-tts:v1.0.0-allinone
```

### Adjust Memory Usage

Edit `server.py` to change `gpu_memory_utilization`:

```python
def load_model(model_name):
    return OrpheusModel(
        model_name=MODEL_CONFIGS[model_name], 
        max_model_len=2048,
        gpu_memory_utilization=0.6  # Reduce from 0.7 to 0.6
    )
```

### Production Deployment with Nginx

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for Nginx reverse proxy setup with SSL.

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| First Request | ~48 seconds |
| Subsequent Requests | ~2.5 seconds |
| Streaming Latency | ~200ms |
| Concurrent Requests | 148.42x (2048 tokens) |
| VRAM Usage | ~39GB |
| Model Loading Time | ~15 seconds |

## 🐛 Troubleshooting

### CUDA Out of Memory

1. Check GPU availability:
```bash
nvidia-smi
```

2. Reduce memory usage:
- Lower `gpu_memory_utilization` to 0.6 or 0.5
- Reduce `max_model_len` to 1024

### HuggingFace Access Denied

1. Request access at: https://huggingface.co/canopylabs/orpheus-3b-0.1-ft
2. Verify your token: https://huggingface.co/settings/tokens
3. Ensure token has read permissions

### Container Won't Start

```bash
# Check logs
docker logs orpheus-tts

# Check GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Changelog

### v1.5.0 (2025-12-14)
- ✅ Model preloading on startup (26x faster first request)
- ✅ Zero-shot voice cloning UI with file upload
- ✅ Generation timing display (model load, generation, total)
- ✅ Privacy protection: host volume mount `/tmp/orpheus-tts`
- ✅ Performance: 3.7s generation (was 48s in v1.0)
- ✅ Memory optimization: 29.8GB VRAM (was 39GB)
- ✅ Docker Hub image: neosun/orpheus-tts:v1.5.0-allinone

### v1.0.0 (2025-12-13)
- ✅ Initial Docker deployment
- ✅ GPU management with lazy loading
- ✅ Three access modes (Web UI, REST API, MCP)
- ✅ Nginx reverse proxy support
- ✅ Performance optimization (gpu_memory_utilization=0.7)
- ✅ Docker Hub image: neosun/orpheus-tts:v1.0.0-allinone

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Canopy Labs](https://canopylabs.ai/) for the amazing Orpheus TTS model
- [vLLM](https://github.com/vllm-project/vllm) for efficient inference
- Original Orpheus TTS: https://github.com/canopyai/Orpheus-TTS

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/orpheus-tts-docker&type=Date)](https://star-history.com/#neosun100/orpheus-tts-docker)

## 📱 Follow Us

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**Made with ❤️ by the community**
