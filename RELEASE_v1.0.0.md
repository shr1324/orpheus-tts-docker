# Orpheus TTS v1.0.0 Release Summary

## 📦 发布信息

**版本**: v1.0.0  
**发布日期**: 2025-12-13  
**Git Tag**: `v1.0.0-bfloat16-3b`  
**Docker Tag**: `orpheus-tts:v1.0.0-bfloat16-3b-allinone`

## 🎯 核心特性

### 模型配置
- **模型**: canopylabs/orpheus-3b-0.1-ft
- **精度**: bfloat16 (全精度 16位浮点)
- **参数量**: 3B (30亿参数)
- **显存占用**: ~39GB (gpu_memory_utilization=0.7)
- **支持语音**: tara, leah, jess, leo, dan, mia, zac, zoe

### 部署架构
- **容器化**: Docker + CUDA 12.1
- **GPU 管理**: 智能懒加载 + 1小时自动卸载
- **访问模式**: 
  - Web UI (暗色主题 + 中英文切换)
  - REST API (Swagger 文档)
  - MCP (Model Context Protocol)
- **反向代理**: Nginx + SSL
- **域名**: https://orpheus-tts.aws.xin

### 性能指标
- **首次请求**: ~48秒 (模型加载)
- **后续请求**: ~2.5秒 (20倍提速)
- **流式延迟**: ~200ms
- **并发支持**: 148.42x (2048 tokens)

## 🐳 Docker 镜像

### 镜像标签
```bash
orpheus-tts:v1.0.0-bfloat16-3b-allinone  # 完整标签 (推荐)
orpheus-tts:v1.0.0-allinone              # 简短标签
orpheus-tts:latest                        # 最新版本
```

### 镜像信息
- **大小**: 11.1GB
- **基础镜像**: nvidia/cuda:12.1.0-devel-ubuntu22.04
- **Python**: 3.10
- **主要依赖**: PyTorch 2.5.1, vLLM 0.7.3, Flask, FastMCP

### 快速启动
```bash
export HF_TOKEN=your_huggingface_token
./run_v1.0.0.sh
```

或使用 docker-compose:
```bash
docker compose up -d
```

## 📊 生产环境

### 服务器配置
- **IP**: 44.193.212.118
- **GPU**: NVIDIA L40S GPU 3 (48GB)
- **端口**: 8899
- **域名**: https://orpheus-tts.aws.xin

### 环境变量
```bash
PORT=8899
GPU_IDLE_TIMEOUT=3600
NVIDIA_VISIBLE_DEVICES=3
HF_TOKEN=hf_***
```

## 🔧 技术亮点

### GPU 优化
1. ✅ 智能 GPU 选择 (避开已满的 GPU)
2. ✅ 显存优化 (gpu_memory_utilization=0.7)
3. ✅ 懒加载机制 (按需加载模型)
4. ✅ 自动卸载 (1小时无请求后释放显存)
5. ✅ 线程安全 (支持并发请求)

### 代码结构
```
Orpheus-TTS/
├── Dockerfile              # 容器定义
├── docker-compose.yml      # 编排配置
├── server.py              # Flask Web 服务
├── mcp_server.py          # MCP 接口
├── gpu_manager.py         # GPU 管理器
├── requirements.txt       # Python 依赖
└── orpheus_tts_pypi/      # Orpheus TTS 库
```

## 📝 已知问题

### HuggingFace 授权
- 模型需要在 HuggingFace 上申请访问权限
- 需要有效的 HF_TOKEN 环境变量

### 显存需求
- 需要至少 40GB 显存
- 推荐 48GB GPU (如 L40S, A100)

## 🚀 下一步计划

### v1.1.0 - AWQ 4-bit 量化版本
- **模型**: Hariprasath28/orpheus-3b-4bit-AWQ
- **预计显存**: ~10-15GB
- **预计性能**: 略快于 bfloat16
- **状态**: 准备测试

### 未来优化
- [ ] 支持多模型切换
- [ ] 添加模型预热机制
- [ ] 实现请求队列管理
- [ ] 添加监控和日志系统
- [ ] 支持分布式部署

## 📚 文档

- [Docker 部署指南](DOCKER_DEPLOYMENT.md)
- [快速开始](QUICK_START.md)
- [MCP 使用指南](MCP_GUIDE.md)
- [架构说明](ARCHITECTURE.md)
- [量化模型说明](QUANTIZED_MODELS.md)
- [镜像说明](DOCKER_IMAGES.md)

## 🎉 致谢

感谢 Canopy Labs 开源 Orpheus TTS 模型！

---

**准备测试 AWQ 4-bit 版本**: 请确认后继续 v1.1.0 开发
