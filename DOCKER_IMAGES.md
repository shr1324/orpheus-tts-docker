# Orpheus TTS Docker 镜像说明

## 镜像标签体系

### v1.0.0-bfloat16-3b-allinone
**完整标签**: `orpheus-tts:v1.0.0-bfloat16-3b-allinone`

**模型信息**:
- 模型: `canopylabs/orpheus-3b-0.1-ft`
- 精度: bfloat16 (全精度，16位浮点)
- 参数量: 3B (30亿参数)
- 显存占用: ~39GB (gpu_memory_utilization=0.7)

**镜像特性**:
- ✅ All-in-One: 包含所有依赖和模型加载代码
- ✅ 基础镜像: nvidia/cuda:12.1.0-devel-ubuntu22.04
- ✅ Python 3.10 + PyTorch 2.5.1 + vLLM 0.7.3
- ✅ 三种访问模式: Web UI, REST API, MCP
- ✅ GPU 智能管理: 懒加载 + 1小时自动卸载
- ✅ 镜像大小: 11.1GB

**性能指标**:
- 首次请求: ~48秒 (模型加载)
- 后续请求: ~2.5秒
- 流式延迟: ~200ms
- 支持语音: tara, leah, jess, leo, dan, mia, zac, zoe

**使用方法**:
```bash
# 使用完整标签
docker run --gpus '"device=3"' -p 8899:8899 \
  -e HF_TOKEN=your_token \
  orpheus-tts:v1.0.0-bfloat16-3b-allinone

# 或使用简短标签
docker run --gpus '"device=3"' -p 8899:8899 \
  -e HF_TOKEN=your_token \
  orpheus-tts:v1.0.0-allinone
```

### 标签别名

| 标签 | 说明 |
|------|------|
| `orpheus-tts:v1.0.0-bfloat16-3b-allinone` | 完整描述标签 (推荐) |
| `orpheus-tts:v1.0.0-allinone` | 版本标签 |
| `orpheus-tts:latest` | 最新版本 |

## Git 里程碑

**Tag**: `v1.0.0-bfloat16-3b`
**Commit**: 75f6f23

查看里程碑:
```bash
git tag -l -n20 v1.0.0-bfloat16-3b
```

## 环境要求

- **GPU**: NVIDIA GPU with CUDA 12.1+ support
- **显存**: 至少 40GB (推荐 48GB)
- **Docker**: 20.10+ with nvidia-docker2
- **系统**: Linux with NVIDIA Driver 525+

## 下一步计划

### v1.1.0-awq-4bit-3b (计划中)
- 模型: Hariprasath28/orpheus-3b-4bit-AWQ
- 精度: AWQ 4-bit 量化
- 预计显存: ~10-15GB
- 预计性能: 略快于 bfloat16

## 镜像管理

### 查看所有镜像
```bash
docker images | grep orpheus-tts
```

### 删除旧镜像
```bash
docker rmi orpheus-tts:old-tag
```

### 导出镜像
```bash
docker save orpheus-tts:v1.0.0-allinone | gzip > orpheus-tts-v1.0.0.tar.gz
```

### 导入镜像
```bash
docker load < orpheus-tts-v1.0.0.tar.gz
```

## 部署配置

当前生产环境:
- **服务器**: 44.193.212.118
- **GPU**: NVIDIA L40S GPU 3
- **域名**: https://orpheus-tts.aws.xin
- **端口**: 8899
- **Nginx**: 反向代理 + SSL

## 更新日志

### v1.0.0 (2025-12-13)
- ✅ 初始 Docker 化部署
- ✅ GPU 管理器实现
- ✅ 三种访问模式
- ✅ Nginx 反向代理
- ✅ 性能优化 (gpu_memory_utilization=0.7)
- ✅ 稳定运行在 GPU 3
