# Orpheus TTS 量化模型

## 当前状态

### 已部署模型
- **模型**: canopylabs/orpheus-3b-0.1-ft (完整精度 bfloat16)
- **显存占用**: ~38.77 GB (使用 gpu_memory_utilization=0.7)
- **GPU**: NVIDIA L40S GPU 3
- **性能**: 
  - 首次加载: ~48秒
  - 后续请求: ~2.5秒
  - Idle timeout: 3600秒 (1小时)

## HuggingFace 上可用的量化版本

### GGUF 格式 (需要 llama.cpp)
**仓库**: [QuantFactory/orpheus-3b-0.1-ft-GGUF](https://huggingface.co/QuantFactory/orpheus-3b-0.1-ft-GGUF)

| 量化级别 | 文件大小 | 显存需求估算 |
|---------|---------|-------------|
| Q2_K    | 1.6 GB  | ~2-3 GB     |
| Q3_K_S  | 1.82 GB | ~2.5-3.5 GB |
| Q3_K_M  | 1.97 GB | ~2.7-3.7 GB |
| Q3_K_L  | 2.1 GB  | ~2.9-3.9 GB |
| Q4_K_S  | 2.27 GB | ~3.1-4.1 GB |
| Q4_0    | 2.26 GB | ~3.1-4.1 GB |
| Q4_1    | 2.47 GB | ~3.3-4.3 GB |
| Q4_K_M  | 2.36 GB | ~3.2-4.2 GB |
| Q5_K_S  | 2.67 GB | ~3.5-4.5 GB |
| Q5_0    | 2.67 GB | ~3.5-4.5 GB |
| Q5_1    | 2.88 GB | ~3.7-4.7 GB |
| Q5_K_M  | 2.73 GB | ~3.6-4.6 GB |
| Q6_K    | 3.11 GB | ~4.0-5.0 GB |
| Q8_0    | 4.03 GB | ~5.0-6.0 GB |

**注意**: GGUF 格式需要使用 llama.cpp 而不是 vLLM，需要重写推理代码。

### AWQ/GPTQ 格式 (兼容 vLLM)
**状态**: ❌ 目前 HuggingFace 上没有 Orpheus 的 AWQ 或 GPTQ 量化版本

如果需要在当前架构下使用量化模型，需要：
1. 自行创建 AWQ/GPTQ 量化版本
2. 或者切换到 llama.cpp 架构使用 GGUF 模型

## 多语言模型

Canopy Labs 还发布了多语言研究版本：

- **中文**: canopylabs/3b-zh-ft-research_release
- **法语**: canopylabs/3b-fr-ft-research_release
- **印地语**: canopylabs/3b-hi-ft-research_release
- **韩语**: canopylabs/3b-ko-ft-research_release
- **西班牙语/意大利语**: canopylabs/3b-es_it-ft-research_release

这些模型同样是完整精度，显存需求与英文版本相似。

## 优化建议

### 当前配置优化
1. ✅ 已设置 `gpu_memory_utilization=0.7` 降低显存占用
2. ✅ 已设置 `GPU_IDLE_TIMEOUT=3600` 保持模型加载
3. ✅ 使用独立 GPU (GPU 3) 避免与其他进程冲突

### 进一步优化选项
1. **降低 max_model_len**: 从 2048 降到 1024 可节省 KV cache 显存
2. **使用 FP8 量化**: vLLM 支持 FP8，但需要模型支持
3. **创建 AWQ 量化版本**: 可将显存占用降至 ~10-15GB

## 参考链接

- [Orpheus GitHub](https://github.com/canopyai/Orpheus-TTS)
- [Orpheus 博客](https://canopylabs.ai/model-releases)
- [多语言模型发布](https://canopylabs.ai/releases/orpheus_can_speak_any_language)
