# Orpheus TTS 快速开始 🚀

## 一分钟启动

```bash
# 1. 启动服务
./start.sh

# 2. 访问 UI
# 浏览器打开: http://0.0.0.0:8899
```

## 三种使用方式

### 🎨 方式 1: Web UI（最简单）

```
http://0.0.0.0:8899
```

1. 输入文本
2. 选择模型和声音
3. 点击生成
4. 播放音频

### 🔌 方式 2: REST API

```bash
curl -X POST http://0.0.0.0:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "tara"}' \
  --output output.wav
```

**API 文档**: http://0.0.0.0:8899/apidocs

### 🤖 方式 3: MCP（AI Agent）

```python
result = await mcp.call_tool(
    "generate_speech",
    {"text": "Hello", "output_path": "out.wav"}
)
```

**详细文档**: [MCP_GUIDE.md](MCP_GUIDE.md)

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 测试部署
./test_deployment.sh

# 查看 GPU
nvidia-smi
```

## 参数速查

| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| model | medium-3b, small-1b*, tiny-400m*, nano-150m* | medium-3b | 模型大小 |
| voice | tara, leah, jess, leo, dan, mia, zac, zoe | tara | 声音选择 |
| temperature | 0.1-1.5 | 0.6 | 随机性 |
| top_p | 0.1-1.0 | 0.8 | 采样范围 |
| repetition_penalty | 1.0-2.0 | 1.3 | 重复惩罚 |

*即将推出

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | 修改 `.env` 中的 `PORT` |
| 显存不足 | 访问 `/api/offload` 释放显存 |
| 模型下载慢 | 设置 `HF_ENDPOINT=https://hf-mirror.com` |
| GPU 不可用 | 检查 `nvidia-smi` 和 `nvidia-docker` |

## 更多帮助

- 📖 完整文档: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- 🤖 MCP 指南: [MCP_GUIDE.md](MCP_GUIDE.md)
- 🐛 问题反馈: [GitHub Issues](https://github.com/canopyai/Orpheus-TTS/issues)
