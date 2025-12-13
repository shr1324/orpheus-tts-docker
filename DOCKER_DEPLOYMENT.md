# Orpheus TTS Docker 部署指南

## 🎯 功能特性

- ✅ **四模型支持**: Medium (3B), Small (1B), Tiny (400M), Nano (150M)
- ✅ **三种访问模式**: UI 界面 + REST API + MCP 接口
- ✅ **智能 GPU 管理**: 自动选择最空闲 GPU，自动释放显存
- ✅ **多语言支持**: 中文/英文界面切换
- ✅ **实时监控**: GPU 状态实时显示
- ✅ **零配置启动**: 一键启动脚本

## 📋 系统要求

- Docker & Docker Compose
- NVIDIA GPU + nvidia-docker
- CUDA 12.1+
- 至少 8GB GPU 显存（推荐 16GB+）

## 🚀 快速开始

### 1. 一键启动

```bash
./start.sh
```

脚本会自动：
- 检测 NVIDIA 驱动
- 选择最空闲的 GPU
- 检查端口冲突
- 构建并启动容器

### 2. 访问服务

启动成功后，访问：

- **UI 界面**: http://0.0.0.0:8899
- **API 文档**: http://0.0.0.0:8899/apidocs
- **健康检查**: http://0.0.0.0:8899/health

## 🎨 使用方式

### 方式一：Web UI

1. 打开浏览器访问 http://0.0.0.0:8899
2. 输入要转换的文本
3. 选择模型和声音
4. 调整参数（可选）
5. 点击"生成语音"
6. 播放或下载生成的音频

**UI 特性：**
- 现代化深色主题
- 响应式设计（支持移动端）
- 中英文切换
- 实时 GPU 状态监控
- 参数滑块调节
- 音频在线播放

### 方式二：REST API

#### 生成语音

```bash
curl -X POST http://0.0.0.0:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is Orpheus TTS.",
    "model": "medium-3b",
    "voice": "tara",
    "temperature": 0.6,
    "top_p": 0.8,
    "repetition_penalty": 1.3
  }' \
  --output output.wav
```

#### 健康检查

```bash
curl http://0.0.0.0:8899/health
```

#### 释放 GPU

```bash
# 释放所有模型
curl -X POST http://0.0.0.0:8899/api/offload

# 释放特定模型
curl -X POST "http://0.0.0.0:8899/api/offload?model=medium-3b"
```

#### Swagger 文档

访问 http://0.0.0.0:8899/apidocs 查看完整 API 文档和在线测试。

### 方式三：MCP 接口

详见 [MCP_GUIDE.md](MCP_GUIDE.md)

**快速示例：**

```python
from fastmcp import FastMCP

mcp = FastMCP("orpheus-tts")

# 生成语音
result = await mcp.call_tool(
    "generate_speech",
    {
        "text": "Hello world",
        "output_path": "/app/outputs/hello.wav",
        "voice": "tara"
    }
)
```

## 🎛️ 参数说明

### 模型选择

| 模型 | 参数量 | 显存需求 | 状态 |
|------|--------|----------|------|
| medium-3b | 3B | ~8GB | ✅ 可用 |
| small-1b | 1B | ~4GB | 🔜 即将推出 |
| tiny-400m | 400M | ~2GB | 🔜 即将推出 |
| nano-150m | 150M | ~1GB | 🔜 即将推出 |

### 声音选择

| 声音 | 特点 | 适用场景 |
|------|------|----------|
| tara | 自然、友好 | 通用 |
| leah | 专业、清晰 | 商务 |
| jess | 活泼、年轻 | 娱乐 |
| leo | 男声、沉稳 | 叙述 |
| dan | 男声、友好 | 对话 |
| mia | 温柔、柔和 | 故事 |
| zac | 男声、活力 | 广告 |
| zoe | 清新、明亮 | 教育 |

### 生成参数

- **temperature** (0.1-1.5): 控制随机性，越高越多样化
- **top_p** (0.1-1.0): 核采样，控制词汇多样性
- **repetition_penalty** (1.0-2.0): 重复惩罚，>=1.1 推荐

## 🔧 配置

### 环境变量

编辑 `.env` 文件：

```bash
# 服务端口
PORT=8899

# GPU 空闲超时（秒）
GPU_IDLE_TIMEOUT=60

# GPU 设备 ID
NVIDIA_VISIBLE_DEVICES=0
```

### GPU 管理策略

系统会自动管理 GPU 显存：

1. **按需加载**: 首次使用时加载模型
2. **智能缓存**: 常用模型保持在内存中
3. **自动释放**: 超过 `GPU_IDLE_TIMEOUT` 秒未使用则释放
4. **手动控制**: 可通过 API/UI 手动释放

## 📊 监控与管理

### 查看日志

```bash
# 实时日志
docker-compose logs -f

# 最近 100 行
docker-compose logs --tail=100
```

### GPU 监控

```bash
# 宿主机监控
nvidia-smi -l 1

# 容器内监控
docker exec orpheus-tts nvidia-smi
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

## 🐛 故障排除

### 问题 1: 端口被占用

**错误信息**: `Bind for 0.0.0.0:8899 failed: port is already allocated`

**解决方案**:
```bash
# 修改 .env 中的 PORT
PORT=8900

# 或停止占用端口的服务
lsof -ti:8899 | xargs kill -9
```

### 问题 2: GPU 不可用

**错误信息**: `CUDA error` 或 `No GPU available`

**解决方案**:
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 nvidia-docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 重启 Docker
sudo systemctl restart docker
```

### 问题 3: 显存不足

**错误信息**: `CUDA out of memory`

**解决方案**:
1. 释放其他 GPU 进程
2. 使用更小的模型（当可用时）
3. 降低 `max_model_len` 参数
4. 手动释放显存：访问 `/api/offload`

### 问题 4: 模型下载慢

**解决方案**:
```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或预先下载模型
huggingface-cli download canopylabs/orpheus-tts-0.1-finetune-prod
```

### 问题 5: vLLM 版本问题

**错误信息**: `KV cache error` 或 `max_model_len property does not exist`

**解决方案**:
```bash
# 回退到稳定版本
pip install vllm==0.7.3
```

## 📈 性能优化

### 1. 预加载模型

在 `server.py` 启动时预加载：

```python
# 在 if __name__ == '__main__' 之前
for model_name in MODEL_CONFIGS.keys():
    try:
        gpu_manager.get_model(model_name, lambda: load_model(model_name))
    except:
        pass
```

### 2. 调整超时时间

对于频繁使用的场景，增加 `GPU_IDLE_TIMEOUT`：

```bash
GPU_IDLE_TIMEOUT=600  # 10 分钟
```

### 3. 使用 fp8 推理

参考 [Baseten 优化方案](additional_inference_options/baseten_inference_example/README.md)

## 🔐 安全建议

1. **生产环境**: 添加认证中间件
2. **防火墙**: 限制访问 IP
3. **HTTPS**: 使用反向代理（Nginx/Caddy）
4. **速率限制**: 防止滥用

## 📚 更多资源

- [原始 README](README.md) - 项目介绍和训练指南
- [MCP 使用指南](MCP_GUIDE.md) - MCP 接口详细文档
- [官方博客](https://canopylabs.ai/model-releases) - 模型发布说明
- [GitHub Issues](https://github.com/canopyai/Orpheus-TTS/issues) - 问题反馈

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
