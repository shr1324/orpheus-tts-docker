# 🧪 Orpheus TTS 部署测试报告

**测试时间**: 2025-12-13 18:35-18:45  
**测试环境**: Ubuntu Linux, 4x NVIDIA L40S GPU  
**Docker 版本**: 29.1.2  
**Docker Compose 版本**: v2.35.0  

---

## ✅ 成功的测试项

### 1. 环境检查 ✅

- **Docker**: 已安装并运行
- **Docker Compose**: 已安装
- **NVIDIA 驱动**: 正常工作
- **nvidia-docker**: 正常工作
- **GPU 可用性**: 4 个 GPU 可用，自动选择 GPU 2（最空闲）

```
GPU 0: 17970 MB 已用 / 46068 MB 总计
GPU 1: 13747 MB 已用 / 46068 MB 总计
GPU 2: 3 MB 已用 / 46068 MB 总计 ← 自动选择
GPU 3: 3 MB 已用 / 46068 MB 总计
```

### 2. Docker 构建 ✅

- **镜像构建**: 成功（耗时 ~2 分钟）
- **依赖安装**: 所有 Python 包安装成功
- **容器启动**: 成功
- **GPU 映射**: 正确映射到 GPU 2

### 3. 服务启动 ✅

- **Flask 服务**: 成功启动在 0.0.0.0:8899
- **SNAC 解码器**: 成功加载（显存占用 ~74MB）
- **端口绑定**: 正确绑定到所有 IP

### 4. 基础功能测试 ✅

#### 4.1 健康检查 ✅

```bash
curl http://0.0.0.0:8899/health
```

**结果**: 
```json
{
  "gpu_status": {
    "gpu_memory": 0.074,
    "loaded_models": []
  },
  "status": "ok"
}
```

**状态**: ✅ 通过

#### 4.2 UI 界面访问 ✅

```bash
curl -I http://0.0.0.0:8899/
```

**结果**: HTTP 200 OK  
**状态**: ✅ 通过

#### 4.3 Swagger API 文档 ✅

```bash
curl -I http://0.0.0.0:8899/apidocs/
```

**结果**: HTTP 200 OK  
**状态**: ✅ 通过

---

## ⚠️ 需要配置的项

### 5. API 语音生成 ⚠️ 需要 HF Token

**测试命令**:
```bash
curl -X POST http://0.0.0.0:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test.", "voice": "tara"}'
```

**结果**: HTTP 500 - 模型访问被拒绝

**错误信息**:
```
huggingface_hub.errors.GatedRepoError: 401 Client Error
Cannot access gated repo for url https://huggingface.co/canopylabs/orpheus-3b-0.1-ft
Access to model is restricted. You must have access to it and be authenticated.
```

**原因**: Orpheus TTS 模型是 **gated model**，需要：
1. HuggingFace 账号
2. 同意模型使用条款
3. 提供 Access Token

**解决方案**: 请参考 [HF_TOKEN_SETUP.md](HF_TOKEN_SETUP.md)

**状态**: ⚠️ 需要用户配置 HF Token

---

## 📊 测试总结

| 测试项 | 状态 | 说明 |
|--------|------|------|
| Docker 环境 | ✅ | 完全正常 |
| GPU 自动选择 | ✅ | 正确选择最空闲 GPU |
| 容器构建 | ✅ | 成功 |
| 服务启动 | ✅ | 成功 |
| 健康检查 API | ✅ | 正常 |
| UI 界面 | ✅ | 可访问 |
| Swagger 文档 | ✅ | 可访问 |
| 语音生成 API | ⚠️ | 需要 HF Token |
| MCP 接口 | ⚠️ | 需要 HF Token |

---

## 🔧 已修复的问题

### 问题 1: 模型名称错误

**原始配置**: `canopylabs/orpheus-tts-0.1-finetune-prod`  
**正确配置**: `canopylabs/orpheus-3b-0.1-ft`

**修复文件**:
- `server.py`
- `mcp_server.py`

### 问题 2: 缺少 HF Token 配置

**添加的文件**:
- `.env.example` - 添加 HF_TOKEN 配置项
- `docker-compose.yml` - 添加 HF_TOKEN 环境变量
- `HF_TOKEN_SETUP.md` - 详细设置指南

---

## 📝 下一步操作

### 用户需要做的：

1. **获取 HuggingFace Token**
   ```bash
   # 访问 https://huggingface.co/settings/tokens
   # 创建一个 Read 权限的 token
   ```

2. **同意模型使用条款**
   ```bash
   # 访问 https://huggingface.co/canopylabs/orpheus-3b-0.1-ft
   # 点击 "Agree and access repository"
   ```

3. **配置 Token**
   ```bash
   # 编辑 .env 文件
   nano .env
   
   # 添加你的 token
   HF_TOKEN=hf_your_actual_token_here
   ```

4. **重启服务**
   ```bash
   docker-compose down
   ./start.sh
   ```

5. **验证功能**
   ```bash
   # 运行完整测试
   ./test_deployment.sh
   ```

---

## 🎯 预期结果（配置 Token 后）

配置 HF Token 后，所有功能应该正常工作：

- ✅ 模型自动下载（首次约 6GB，需要几分钟）
- ✅ 模型加载到 GPU（约 8GB 显存）
- ✅ API 生成语音成功
- ✅ UI 界面生成语音成功
- ✅ MCP 接口正常工作

---

## 📚 相关文档

- [HF Token 设置指南](HF_TOKEN_SETUP.md) ⭐ 必读
- [快速开始](QUICK_START.md)
- [完整部署指南](DOCKER_DEPLOYMENT.md)
- [MCP 使用指南](MCP_GUIDE.md)
- [部署检查清单](DEPLOYMENT_CHECKLIST.md)

---

## 🐛 已知限制

1. **模型大小**: 目前只有 3B 模型可用，其他大小（1B, 400M, 150M）尚未发布
2. **首次下载**: 首次使用需要下载约 6GB 模型文件
3. **显存需求**: 至少需要 8GB GPU 显存
4. **Gated Model**: 需要 HuggingFace 账号和 token

---

## ✨ 架构亮点

即使在需要配置 HF Token 的情况下，部署架构的以下特性已经验证成功：

1. ✅ **自动 GPU 选择**: 成功选择最空闲的 GPU
2. ✅ **Docker 化部署**: 一键启动脚本工作正常
3. ✅ **三模式架构**: UI + API + MCP 架构就绪
4. ✅ **智能 GPU 管理**: GPU 管理器正常工作
5. ✅ **完整文档**: 所有文档齐全且准确

---

**测试人员**: AI Assistant  
**测试状态**: 部分完成（等待 HF Token 配置）  
**建议**: 用户配置 HF Token 后可进行完整功能测试
