# Orpheus TTS 架构说明

## 📐 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker 容器                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              GPU 资源管理器 (gpu_manager.py)        │    │
│  │  - 模型缓存管理                                      │    │
│  │  - 自动加载/卸载                                     │    │
│  │  - 空闲超时控制                                      │    │
│  └────────────────────────────────────────────────────┘    │
│           ↓              ↓              ↓                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │   Web UI     │ │  REST API    │ │  MCP Server  │       │
│  │  (Flask)     │ │  (Flask)     │ │  (FastMCP)   │       │
│  │              │ │              │ │              │       │
│  │ - 中英文界面  │ │ - Swagger    │ │ - 4 个工具   │       │
│  │ - 实时监控    │ │ - JSON API   │ │ - 类型注解   │       │
│  │ - 参数调节    │ │ - 文件下载   │ │ - 错误处理   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│           ↓              ↓              ↓                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Orpheus TTS 核心 (orpheus_tts_pypi)        │    │
│  │  - OrpheusModel (engine_class.py)                  │    │
│  │  - SNAC Decoder (decoder.py)                       │    │
│  │  - vLLM 推理引擎                                    │    │
│  └────────────────────────────────────────────────────┘    │
│           ↓                                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │                  NVIDIA GPU                         │    │
│  │  - CUDA 12.1                                        │    │
│  │  - 自动选择最空闲 GPU                                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 核心组件

### 1. GPU 管理器 (gpu_manager.py)

**职责**:
- 统一管理所有模型的 GPU 资源
- 实现模型的懒加载和自动卸载
- 防止显存溢出

**关键特性**:
```python
class GPUManager:
    - get_model(name, load_func)  # 获取或加载模型
    - force_offload(name)          # 强制卸载模型
    - get_status()                 # 获取 GPU 状态
    - _cleanup_idle_models()       # 自动清理空闲模型
```

**工作流程**:
1. 首次请求时加载模型到 GPU
2. 记录最后使用时间
3. 后台线程定期检查空闲时间
4. 超时自动卸载，释放显存
5. 下次请求时重新加载

### 2. Web 服务器 (server.py)

**职责**:
- 提供 Web UI 界面
- 提供 REST API 接口
- 集成 Swagger 文档

**端点**:
- `GET /` - Web UI
- `GET /health` - 健康检查
- `POST /api/generate` - 生成语音
- `POST /api/offload` - 释放显存
- `GET /apidocs` - Swagger 文档

**UI 特性**:
- 单页应用（SPA）
- 响应式设计
- 深色主题
- 中英文切换
- 实时 GPU 监控
- 参数滑块

### 3. MCP 服务器 (mcp_server.py)

**职责**:
- 提供程序化访问接口
- 支持 AI Agent 调用
- 与 UI/API 共享 GPU 管理器

**工具**:
1. `generate_speech` - 生成语音
2. `get_gpu_status` - 查询状态
3. `offload_gpu` - 释放显存
4. `list_models` - 列出模型

**优势**:
- 类型安全
- 自动文档
- 错误处理
- 异步支持

### 4. Orpheus TTS 核心

**组件**:
- `OrpheusModel` - 主模型类
- `SNAC` - 音频解码器
- `vLLM` - 推理引擎

**流程**:
```
文本输入 → 格式化提示 → vLLM 生成 token → SNAC 解码 → 音频输出
```

## 🔄 数据流

### UI 生成流程

```
用户输入文本
    ↓
前端 JavaScript 发送 POST 请求
    ↓
Flask 接收请求
    ↓
GPU Manager 获取/加载模型
    ↓
OrpheusModel.generate_speech()
    ↓
流式生成音频块
    ↓
写入 WAV 文件
    ↓
返回音频文件
    ↓
前端播放音频
```

### API 生成流程

```
HTTP POST /api/generate
    ↓
解析 JSON 参数
    ↓
GPU Manager 获取模型
    ↓
生成音频
    ↓
返回 audio/wav
```

### MCP 生成流程

```
MCP Client 调用工具
    ↓
mcp_server.py 接收调用
    ↓
GPU Manager 获取模型
    ↓
生成音频到文件
    ↓
返回结果 JSON
```

## 🎯 模型管理策略

### 四模型架构

```python
MODEL_CONFIGS = {
    "medium-3b": "canopylabs/orpheus-tts-0.1-finetune-prod",  # ✅ 可用
    "small-1b": "...",   # 🔜 即将推出
    "tiny-400m": "...",  # 🔜 即将推出
    "nano-150m": "..."   # 🔜 即将推出
}
```

### 加载策略

**按需加载**:
- 首次请求时才加载模型
- 避免启动时占用大量显存

**智能缓存**:
- 常用模型保持在内存
- 根据使用频率动态调整

**自动卸载**:
- 超时未使用自动释放
- 可配置超时时间

**手动控制**:
- UI 按钮手动释放
- API 端点手动释放
- MCP 工具手动释放

### 显存优化

1. **单模型模式**: 只加载一个模型（默认）
2. **多模型模式**: 预加载所有模型（需修改代码）
3. **混合模式**: 常用模型常驻，其他按需加载

## 🚀 部署架构

### Docker 容器

```dockerfile
nvidia/cuda:12.1.0 基础镜像
    ↓
安装 Python 3.10
    ↓
安装依赖 (vLLM, transformers, etc.)
    ↓
复制项目代码
    ↓
暴露端口 8899
    ↓
启动 server.py
```

### GPU 选择

```bash
# start.sh 自动选择最空闲 GPU
GPU_ID=$(nvidia-smi --query-gpu=index,memory.used \
         --format=csv,noheader,nounits | \
         sort -t',' -k2 -n | head -1 | cut -d',' -f1)
```

### 端口映射

```yaml
ports:
  - "0.0.0.0:8899:8899"  # 对所有 IP 开放
```

### 卷挂载

```yaml
volumes:
  - ./outputs:/app/outputs              # 输出目录
  - huggingface_cache:/root/.cache/...  # 模型缓存
```

## 🔐 安全考虑

### 当前实现

- ✅ CORS 启用（开发模式）
- ✅ 错误处理
- ✅ 参数验证

### 生产建议

- 🔒 添加认证（JWT/API Key）
- 🔒 速率限制
- 🔒 HTTPS（反向代理）
- 🔒 输入过滤
- 🔒 日志审计

## 📊 性能指标

### 延迟

- **首次加载**: ~30-60 秒（下载模型）
- **后续加载**: ~5-10 秒（从缓存）
- **生成延迟**: ~200ms（流式）
- **总体延迟**: ~1-3 秒（短文本）

### 显存占用

- **Medium (3B)**: ~8GB
- **Small (1B)**: ~4GB（预估）
- **Tiny (400M)**: ~2GB（预估）
- **Nano (150M)**: ~1GB（预估）

### 吞吐量

- **单请求**: ~1-2 秒/句
- **并发**: 取决于 GPU 和模型大小
- **批处理**: 支持（需修改代码）

## 🔧 扩展性

### 水平扩展

```yaml
# docker-compose.yml
services:
  orpheus-1:
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
  orpheus-2:
    environment:
      - NVIDIA_VISIBLE_DEVICES=1
```

### 负载均衡

```
Nginx/HAProxy
    ↓
┌─────┬─────┬─────┐
│ GPU0│ GPU1│ GPU2│
└─────┴─────┴─────┘
```

### 模型并行

- 当前: 单 GPU 单模型
- 可扩展: 多 GPU 模型并行（需修改 vLLM 配置）

## 📝 配置文件

### .env

```bash
PORT=8899                    # 服务端口
GPU_IDLE_TIMEOUT=60          # 空闲超时
NVIDIA_VISIBLE_DEVICES=0     # GPU ID
```

### docker-compose.yml

```yaml
runtime: nvidia              # 启用 GPU
environment: ...             # 环境变量
ports: ...                   # 端口映射
volumes: ...                 # 卷挂载
```

### mcp_config.json

```json
{
  "mcpServers": {
    "orpheus-tts": {
      "command": "python3",
      "args": ["mcp_server.py"]
    }
  }
}
```

## 🐛 调试技巧

### 查看日志

```bash
# 容器日志
docker-compose logs -f

# GPU 日志
nvidia-smi dmon

# Python 日志
docker exec orpheus-tts tail -f /var/log/app.log
```

### 性能分析

```python
# 添加到 server.py
import time

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    print(f"Request took {diff:.2f}s")
    return response
```

### GPU 监控

```bash
# 实时监控
watch -n 1 nvidia-smi

# 详细信息
nvidia-smi -q -d MEMORY,UTILIZATION
```

## 🎓 最佳实践

1. **开发环境**: 使用 `GPU_IDLE_TIMEOUT=30`
2. **生产环境**: 使用 `GPU_IDLE_TIMEOUT=600`
3. **高并发**: 部署多个实例 + 负载均衡
4. **低延迟**: 预加载模型 + 增加超时时间
5. **低显存**: 使用更小的模型 + 及时释放

## 📚 参考资料

- [vLLM 文档](https://docs.vllm.ai/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Docker 文档](https://docs.docker.com/)
