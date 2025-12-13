# 🔑 HuggingFace Token 设置指南

Orpheus TTS 使用的模型是 **gated model**（需要授权访问），因此您需要：

## 📋 步骤

### 1. 创建 HuggingFace 账号

访问 [HuggingFace](https://huggingface.co/join) 注册账号（如果已有账号可跳过）

### 2. 获取 Access Token

1. 登录后访问：https://huggingface.co/settings/tokens
2. 点击 "New token"
3. 选择 "Read" 权限即可
4. 复制生成的 token

### 3. 同意模型使用条款

访问模型页面并同意条款：
- https://huggingface.co/canopylabs/orpheus-3b-0.1-ft

点击 "Agree and access repository"

### 4. 配置 Token

#### 方法 1: 使用 .env 文件（推荐）

```bash
# 编辑 .env 文件
nano .env

# 添加你的 token
HF_TOKEN=hf_your_actual_token_here
```

#### 方法 2: 直接设置环境变量

```bash
export HF_TOKEN=hf_your_actual_token_here
./start.sh
```

#### 方法 3: 在容器内登录

```bash
docker exec -it orpheus-tts huggingface-cli login
# 输入你的 token
```

### 5. 重启服务

```bash
docker-compose down
./start.sh
```

## ✅ 验证

启动后，检查日志确认模型加载成功：

```bash
docker-compose logs -f
```

应该看到类似信息：
```
INFO: Model loaded successfully
```

## ❓ 常见问题

### Q: 为什么需要 token？

A: Orpheus TTS 模型是 gated model，需要用户同意使用条款后才能访问。这是 HuggingFace 的标准做法。

### Q: Token 安全吗？

A: Token 只存储在您的本地 `.env` 文件中，不会被上传或分享。请不要将包含 token 的 `.env` 文件提交到 git。

### Q: 忘记 token 怎么办？

A: 可以在 https://huggingface.co/settings/tokens 重新生成一个新的 token。

### Q: 401 Unauthorized 错误

A: 确保：
1. Token 正确复制（包括 `hf_` 前缀）
2. 已在模型页面同意条款
3. Token 有 "Read" 权限
4. 重启了服务

## 📚 相关链接

- [HuggingFace Tokens 文档](https://huggingface.co/docs/hub/security-tokens)
- [Orpheus TTS 模型页面](https://huggingface.co/canopylabs/orpheus-3b-0.1-ft)
- [Orpheus TTS GitHub](https://github.com/canopyai/Orpheus-TTS)
