# Orpheus TTS Docker 部署

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Image](https://img.shields.io/badge/docker-neosun%2Forpheus--tts-blue)](https://hub.docker.com/r/neosun/orpheus-tts)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0.0-orange)](https://github.com/neosun100/orpheus-tts-docker/releases)

生产级 Orpheus TTS Docker 部署方案，支持 GPU 管理、多种访问模式和性能优化。

## ✨ 功能特性

- 🐳 **Docker 容器化**：一键部署，支持 CUDA 12.1
- 🎯 **智能 GPU 管理**：懒加载 + 自动卸载（1小时超时）
- 🌐 **三种访问模式**：Web UI、REST API 和 MCP（模型上下文协议）
- 🚀 **性能优化**：模型加载后推理仅需 ~2.5秒
- 🔒 **生产就绪**：支持 Nginx 反向代理和 SSL
- 🎨 **现代化 Web UI**：暗色主题，支持中英文切换
- 📊 **API 文档**：内置 Swagger UI
- 🎤 **8种语音选项**：tara, leah, jess, leo, dan, mia, zac, zoe

## 🎯 模型信息

- **模型**：canopylabs/orpheus-3b-0.1-ft
- **精度**：bfloat16（全精度）
- **参数量**：3B（30亿参数）
- **显存占用**：~39GB（gpu_memory_utilization=0.7）
- **性能指标**：
  - 首次请求：~48秒（模型加载）
  - 后续请求：~2.5秒
  - 流式延迟：~200ms

## 🚀 快速开始

### 前置要求

- Docker 20.10+ 和 nvidia-docker2
- NVIDIA GPU，显存 40GB+（如 L40S、A100）
- CUDA 12.1+ 兼容驱动
- HuggingFace 账号，并获得 [orpheus-3b-0.1-ft](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft) 访问权限

### 方式一：Docker Run（最快）

```bash
# 设置 HuggingFace token
export HF_TOKEN=your_huggingface_token

# 拉取并运行
docker pull neosun/orpheus-tts:v1.0.0-allinone

docker run -d \
  --name orpheus-tts \
  --gpus '"device=0"' \
  -p 8899:8899 \
  -e HF_TOKEN=$HF_TOKEN \
  -v $(pwd)/outputs:/app/outputs \
  --restart unless-stopped \
  neosun/orpheus-tts:v1.0.0-allinone

# 等待服务启动（约30秒）
sleep 30

# 检查健康状态
curl http://localhost:8899/health
```

### 方式二：Docker Compose（推荐）

1. 克隆仓库：
```bash
git clone https://github.com/neosun100/orpheus-tts-docker.git
cd orpheus-tts-docker
```

2. 创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 并设置你的 HF_TOKEN
```

3. 启动服务：
```bash
docker compose up -d
```

4. 验证：
```bash
# 检查容器状态
docker compose ps

# 检查健康状态
curl http://localhost:8899/health
```

## 📖 使用方法

### Web UI

在浏览器中打开：
```
http://localhost:8899
```

功能：
- 文本输入和语音选择
- 实时音频生成
- 下载生成的音频
- 暗色主题和语言切换

### REST API

#### 生成语音

```bash
curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好世界，这是一个测试。",
    "voice": "tara",
    "model_size": "medium"
  }' \
  --output output.wav
```

#### API 文档

交互式 Swagger UI：
```
http://localhost:8899/docs
```

#### 可用端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/generate` | POST | 生成语音 |
| `/api/voices` | GET | 列出可用语音 |
| `/api/models` | GET | 列出可用模型 |
| `/gpu/status` | GET | GPU 状态 |
| `/gpu/offload` | POST | 卸载 GPU 模型 |

### MCP（模型上下文协议）

用于 AI 助手和自动化工具：

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

可用的 MCP 工具：
- `generate_speech`：从文本生成语音
- `get_gpu_status`：检查 GPU 内存使用
- `offload_gpu`：释放 GPU 内存
- `list_models`：列出可用模型

## ⚙️ 配置

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `PORT` | 8899 | 服务端口 |
| `GPU_IDLE_TIMEOUT` | 3600 | 模型卸载超时（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU 设备 ID |
| `HF_TOKEN` | - | HuggingFace token（必需） |

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

## 📁 项目结构

```
orpheus-tts-docker/
├── Dockerfile              # 容器定义
├── docker-compose.yml      # 编排配置
├── server.py              # Flask Web 服务器
├── mcp_server.py          # MCP 接口
├── gpu_manager.py         # GPU 管理
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量模板
├── outputs/               # 生成的音频文件
└── docs/                  # 文档
    ├── ARCHITECTURE.md
    ├── DOCKER_DEPLOYMENT.md
    ├── MCP_GUIDE.md
    └── QUANTIZED_MODELS.md
```

## 🛠️ 技术栈

- **基础**：Python 3.10、CUDA 12.1
- **ML 框架**：PyTorch 2.5.1、vLLM 0.7.3
- **Web 框架**：Flask 3.0.0
- **模型**：Orpheus TTS（canopylabs/orpheus-3b-0.1-ft）
- **容器**：Docker、Docker Compose
- **GPU**：NVIDIA CUDA with nvidia-docker2

## 🔧 高级用法

### 自定义 GPU 选择

```bash
# 使用 GPU 2
docker run -d \
  --gpus '"device=2"' \
  -e NVIDIA_VISIBLE_DEVICES=2 \
  neosun/orpheus-tts:v1.0.0-allinone
```

### 调整内存使用

编辑 `server.py` 修改 `gpu_memory_utilization`：

```python
def load_model(model_name):
    return OrpheusModel(
        model_name=MODEL_CONFIGS[model_name], 
        max_model_len=2048,
        gpu_memory_utilization=0.6  # 从 0.7 降至 0.6
    )
```

### 生产环境部署（Nginx）

参见 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) 了解 Nginx 反向代理和 SSL 配置。

## 📊 性能基准

| 指标 | 数值 |
|------|------|
| 首次请求 | ~48秒 |
| 后续请求 | ~2.5秒 |
| 流式延迟 | ~200ms |
| 并发请求 | 148.42x（2048 tokens） |
| 显存占用 | ~39GB |
| 模型加载时间 | ~15秒 |

## 🐛 故障排除

### CUDA 内存不足

1. 检查 GPU 可用性：
```bash
nvidia-smi
```

2. 降低内存使用：
- 将 `gpu_memory_utilization` 降至 0.6 或 0.5
- 将 `max_model_len` 降至 1024

### HuggingFace 访问被拒

1. 在此申请访问：https://huggingface.co/canopylabs/orpheus-3b-0.1-ft
2. 验证你的 token：https://huggingface.co/settings/tokens
3. 确保 token 有读取权限

### 容器无法启动

```bash
# 查看日志
docker logs orpheus-tts

# 检查 GPU 访问
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0（2025-12-13）
- ✅ 初始 Docker 部署
- ✅ GPU 管理和懒加载
- ✅ 三种访问模式（Web UI、REST API、MCP）
- ✅ Nginx 反向代理支持
- ✅ 性能优化（gpu_memory_utilization=0.7）
- ✅ Docker Hub 镜像：neosun/orpheus-tts:v1.0.0-allinone

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Canopy Labs](https://canopylabs.ai/) 提供的出色 Orpheus TTS 模型
- [vLLM](https://github.com/vllm-project/vllm) 提供的高效推理
- 原始 Orpheus TTS：https://github.com/canopyai/Orpheus-TTS

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/orpheus-tts-docker&type=Date)](https://star-history.com/#neosun100/orpheus-tts-docker)

## 📱 关注我们

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**用 ❤️ 打造**
