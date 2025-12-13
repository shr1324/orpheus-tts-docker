# Orpheus TTS MCP 使用指南

## 什么是 MCP？

Model Context Protocol (MCP) 是一个开放协议，用于标准化应用程序如何向 LLM 提供上下文。通过 MCP，您可以通过编程方式调用 Orpheus TTS 的功能。

## 配置 MCP 服务器

### 1. 启动 MCP 服务器

```bash
python3 mcp_server.py
```

### 2. 配置 MCP 客户端

在您的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "orpheus-tts": {
      "command": "python3",
      "args": ["/path/to/Orpheus-TTS/mcp_server.py"],
      "env": {
        "GPU_IDLE_TIMEOUT": "600"
      }
    }
  }
}
```

## 可用工具

### 1. generate_speech

生成语音并保存到文件。

**参数：**
- `text` (string, 必需): 要转换的文本
- `output_path` (string, 必需): 输出文件路径（.wav）
- `model` (string, 可选): 模型名称，默认 "medium-3b"
  - 可选值: "medium-3b", "small-1b", "tiny-400m", "nano-150m"
  - 注意: 目前仅 medium-3b 可用
- `voice` (string, 可选): 声音，默认 "tara"
  - 可选值: "tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"
- `temperature` (float, 可选): 温度参数 (0.1-1.5)，默认 0.6
- `top_p` (float, 可选): Top-p 采样 (0.1-1.0)，默认 0.8
- `repetition_penalty` (float, 可选): 重复惩罚 (1.0-2.0)，默认 1.3

**返回：**
```json
{
  "status": "success",
  "output_path": "/path/to/output.wav",
  "model": "medium-3b",
  "voice": "tara"
}
```

**示例：**
```python
result = await mcp_client.call_tool(
    "generate_speech",
    {
        "text": "Hello, this is a test of Orpheus TTS.",
        "output_path": "/app/outputs/test.wav",
        "model": "medium-3b",
        "voice": "tara",
        "temperature": 0.7
    }
)
```

### 2. get_gpu_status

获取当前 GPU 状态。

**参数：** 无

**返回：**
```json
{
  "loaded_models": ["medium-3b"],
  "gpu_memory": 2.45
}
```

**示例：**
```python
status = await mcp_client.call_tool("get_gpu_status", {})
```

### 3. offload_gpu

释放 GPU 显存。

**参数：**
- `model_name` (string, 可选): 要释放的模型名称，不指定则释放全部

**返回：**
```json
{
  "status": "offloaded",
  "gpu_status": {
    "loaded_models": [],
    "gpu_memory": 0.0
  }
}
```

**示例：**
```python
# 释放特定模型
result = await mcp_client.call_tool("offload_gpu", {"model_name": "medium-3b"})

# 释放所有模型
result = await mcp_client.call_tool("offload_gpu", {})
```

### 4. list_models

列出所有可用的模型和声音。

**参数：** 无

**返回：**
```json
{
  "models": ["medium-3b", "small-1b", "tiny-400m", "nano-150m"],
  "voices": ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"],
  "note": "Currently only medium-3b is available. Other models coming soon."
}
```

**示例：**
```python
models = await mcp_client.call_tool("list_models", {})
```

## MCP vs API 的区别

| 特性 | MCP | API |
|------|-----|-----|
| 访问方式 | 程序化调用（通过 MCP 客户端） | HTTP 请求 |
| 适用场景 | AI Agent、自动化工具 | Web 应用、移动应用 |
| 返回格式 | 结构化数据 | HTTP 响应（JSON/文件） |
| GPU 管理 | 共享 GPU 管理器 | 共享 GPU 管理器 |
| 文档 | 工具函数注释 | Swagger UI |

## 使用建议

1. **长时间运行任务**: 使用 MCP 可以更好地管理长时间运行的任务
2. **批量处理**: MCP 适合批量处理多个文本转语音任务
3. **GPU 管理**: 定期调用 `get_gpu_status` 监控 GPU 使用情况
4. **错误处理**: 所有工具都会返回 `status` 字段，检查是否为 "success"

## 故障排除

### 问题：MCP 服务器无法启动

**解决方案：**
1. 检查 Python 环境是否正确
2. 确保所有依赖已安装：`pip install -r requirements.txt`
3. 检查 GPU 是否可用：`nvidia-smi`

### 问题：生成语音失败

**解决方案：**
1. 检查 GPU 显存是否充足
2. 尝试释放 GPU：调用 `offload_gpu`
3. 检查文本是否为空或过长

### 问题：模型加载慢

**解决方案：**
1. 首次加载需要下载模型，请耐心等待
2. 后续调用会使用缓存的模型
3. 调整 `GPU_IDLE_TIMEOUT` 以保持模型在内存中

## 完整示例

```python
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("orpheus-tts")
    
    # 列出可用模型
    models = await client.call_tool("list_models", {})
    print(f"Available models: {models['models']}")
    
    # 生成语音
    result = await client.call_tool(
        "generate_speech",
        {
            "text": "Man, the way social media has completely changed how we interact is just wild.",
            "output_path": "/app/outputs/demo.wav",
            "voice": "leo",
            "temperature": 0.7
        }
    )
    
    if result['status'] == 'success':
        print(f"Speech generated: {result['output_path']}")
    
    # 检查 GPU 状态
    status = await client.call_tool("get_gpu_status", {})
    print(f"GPU Memory: {status['gpu_memory']:.2f} GB")
    
    # 释放 GPU
    await client.call_tool("offload_gpu", {})

if __name__ == "__main__":
    asyncio.run(main())
```
