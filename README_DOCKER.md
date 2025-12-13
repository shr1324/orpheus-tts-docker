# 🐳 Orpheus TTS Docker 部署

> 一键部署 Orpheus TTS，支持 UI + API + MCP 三种访问方式

## 🚀 快速开始（30 秒）

```bash
# 1. 启动服务
./start.sh

# 2. 访问 UI
# 浏览器打开: http://0.0.0.0:8899
```

就这么简单！🎉

## 📚 文档导航

### 新手入门

1. **[快速开始](QUICK_START.md)** ⭐ - 1 分钟上手
2. **[部署检查清单](DEPLOYMENT_CHECKLIST.md)** - 确保部署成功

### 详细文档

3. **[完整部署指南](DOCKER_DEPLOYMENT.md)** - 所有细节
4. **[MCP 使用指南](MCP_GUIDE.md)** - AI Agent 接口
5. **[架构说明](ARCHITECTURE.md)** - 深入理解

### 项目信息

6. **[项目总结](PROJECT_SUMMARY.md)** - 功能概览
7. **[最终报告](FINAL_REPORT.md)** - 完整报告

## 🎯 三种使用方式

### 1️⃣ Web UI（最简单）

```
http://0.0.0.0:8899
```

- 中英文界面
- 实时 GPU 监控
- 参数可视化调节
- 音频在线播放

### 2️⃣ REST API

```bash
curl -X POST http://0.0.0.0:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "tara"}' \
  --output output.wav
```

**API 文档**: http://0.0.0.0:8899/apidocs

### 3️⃣ MCP（AI Agent）

```python
result = await mcp.call_tool(
    "generate_speech",
    {"text": "Hello", "output_path": "out.wav"}
)
```

**详细说明**: [MCP_GUIDE.md](MCP_GUIDE.md)

## 🎨 支持的模型和声音

### 模型

- ✅ **medium-3b** (3B 参数) - 当前可用
- 🔜 **small-1b** (1B 参数) - 即将推出
- 🔜 **tiny-400m** (400M 参数) - 即将推出
- 🔜 **nano-150m** (150M 参数) - 即将推出

### 声音

tara, leah, jess, leo, dan, mia, zac, zoe

## 🔧 常用命令

```bash
# 启动服务
./start.sh

# 测试部署
./test_deployment.sh

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看 GPU
nvidia-smi
```

## ⚙️ 配置

编辑 `.env` 文件：

```bash
PORT=8899                    # 服务端口
GPU_IDLE_TIMEOUT=60          # GPU 空闲超时（秒）
NVIDIA_VISIBLE_DEVICES=0     # GPU 设备 ID
```

## 🐛 常见问题

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | 修改 `.env` 中的 `PORT` |
| 显存不足 | 访问 `/api/offload` 释放显存 |
| 模型下载慢 | 设置 `HF_ENDPOINT=https://hf-mirror.com` |
| GPU 不可用 | 检查 `nvidia-smi` 和 `nvidia-docker` |

**更多问题**: 查看 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

## 📊 系统要求

- Docker & Docker Compose
- NVIDIA GPU + nvidia-docker
- CUDA 12.1+
- 至少 8GB GPU 显存

## 🎓 推荐阅读顺序

1. [QUICK_START.md](QUICK_START.md) - 快速上手
2. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 部署检查
3. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 详细了解
4. [MCP_GUIDE.md](MCP_GUIDE.md) - MCP 使用（可选）
5. [ARCHITECTURE.md](ARCHITECTURE.md) - 深入理解（可选）

## 🌟 特性亮点

- ✅ 一键启动（自动选择最空闲 GPU）
- ✅ 三种访问方式（UI + API + MCP）
- ✅ 智能 GPU 管理（自动加载/卸载）
- ✅ 四模型架构（支持切换）
- ✅ 中英文界面
- ✅ 完整文档

## 📞 获取帮助

- 📖 查看文档: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- 🐛 提交 Issue: [GitHub Issues](https://github.com/canopyai/Orpheus-TTS/issues)
- 💬 讨论区: [GitHub Discussions](https://github.com/canopyai/Orpheus-TTS/discussions)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**开始使用**: `./start.sh` 🚀
