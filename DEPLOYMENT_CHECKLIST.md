# 🚀 Orpheus TTS 部署检查清单

## 📋 部署前检查

### 系统环境

- [ ] 已安装 Docker
  ```bash
  docker --version
  ```

- [ ] 已安装 Docker Compose
  ```bash
  docker-compose --version
  ```

- [ ] 已安装 NVIDIA 驱动
  ```bash
  nvidia-smi
  ```

- [ ] 已安装 nvidia-docker
  ```bash
  docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
  ```

- [ ] GPU 显存充足（至少 8GB）
  ```bash
  nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits
  ```

### 端口检查

- [ ] 端口 8899 未被占用（或修改 `.env` 中的 `PORT`）
  ```bash
  ss -tuln | grep 8899
  ```

### 文件检查

- [ ] 所有必需文件存在
  ```bash
  ls -l Dockerfile docker-compose.yml requirements.txt .env.example start.sh
  ```

- [ ] 启动脚本有执行权限
  ```bash
  ls -l start.sh test_deployment.sh
  ```

## 🚀 部署步骤

### 1. 创建环境配置

- [ ] 复制环境变量文件
  ```bash
  cp .env.example .env
  ```

- [ ] 根据需要修改 `.env`
  ```bash
  nano .env
  # 修改 PORT, GPU_IDLE_TIMEOUT 等
  ```

### 2. 启动服务

- [ ] 运行启动脚本
  ```bash
  ./start.sh
  ```

- [ ] 等待容器启动完成
  ```bash
  docker-compose logs -f
  # 看到 "Running on http://0.0.0.0:8899" 表示成功
  ```

### 3. 验证部署

- [ ] 健康检查通过
  ```bash
  curl http://0.0.0.0:8899/health
  # 应返回 {"status": "ok", ...}
  ```

- [ ] UI 可访问
  ```bash
  curl -I http://0.0.0.0:8899/
  # 应返回 HTTP/1.1 200 OK
  ```

- [ ] API 文档可访问
  ```bash
  curl -I http://0.0.0.0:8899/apidocs
  # 应返回 HTTP/1.1 200 OK
  ```

### 4. 功能测试

- [ ] 运行测试脚本
  ```bash
  ./test_deployment.sh
  ```

- [ ] 测试 UI 生成
  - 打开浏览器访问 http://0.0.0.0:8899
  - 输入测试文本
  - 点击生成
  - 播放音频

- [ ] 测试 API 生成
  ```bash
  curl -X POST http://0.0.0.0:8899/api/generate \
    -H "Content-Type: application/json" \
    -d '{"text": "This is a test.", "voice": "tara"}' \
    --output test.wav
  
  # 检查文件
  file test.wav
  # 应显示: RIFF (little-endian) data, WAVE audio
  ```

- [ ] 测试 GPU 状态
  ```bash
  curl http://0.0.0.0:8899/health | jq '.gpu_status'
  ```

- [ ] 测试 GPU 释放
  ```bash
  curl -X POST http://0.0.0.0:8899/api/offload
  ```

## 🎯 MCP 部署（可选）

### 1. 配置 MCP 服务器

- [ ] 复制 MCP 配置
  ```bash
  cp mcp_config.json ~/.config/mcp/config.json
  # 或根据你的 MCP 客户端配置路径
  ```

- [ ] 修改配置中的路径
  ```bash
  nano ~/.config/mcp/config.json
  # 修改 args 中的路径为实际路径
  ```

### 2. 测试 MCP

- [ ] 启动 MCP 服务器
  ```bash
  python3 mcp_server.py
  ```

- [ ] 测试 MCP 工具（使用你的 MCP 客户端）
  ```python
  # 列出模型
  result = await mcp.call_tool("list_models", {})
  
  # 生成语音
  result = await mcp.call_tool(
      "generate_speech",
      {"text": "Hello", "output_path": "/tmp/test.wav"}
  )
  ```

## 📊 监控检查

### 容器状态

- [ ] 容器正在运行
  ```bash
  docker-compose ps
  # 应显示 State: Up
  ```

- [ ] 容器日志正常
  ```bash
  docker-compose logs --tail=50
  # 无错误信息
  ```

### GPU 状态

- [ ] GPU 被容器使用
  ```bash
  nvidia-smi
  # 应看到 orpheus-tts 进程
  ```

- [ ] 显存占用正常
  ```bash
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
  # 首次加载后应该在 8GB 左右
  ```

### 网络状态

- [ ] 端口正在监听
  ```bash
  ss -tuln | grep 8899
  # 应显示 LISTEN 状态
  ```

- [ ] 可从其他机器访问（如果需要）
  ```bash
  # 从其他机器
  curl http://<服务器IP>:8899/health
  ```

## 🔧 性能优化（可选）

### 预加载模型

- [ ] 修改 `server.py` 添加预加载代码
  ```python
  # 在 if __name__ == '__main__' 之前
  for model_name in ["medium-3b"]:
      try:
          gpu_manager.get_model(model_name, lambda: load_model(model_name))
      except:
          pass
  ```

- [ ] 重启服务
  ```bash
  docker-compose restart
  ```

### 调整超时

- [ ] 根据使用场景调整 `GPU_IDLE_TIMEOUT`
  ```bash
  # 开发: 30 秒
  # 生产: 600 秒
  nano .env
  docker-compose restart
  ```

## 🔐 安全加固（生产环境）

### 基础安全

- [ ] 修改默认端口
- [ ] 配置防火墙规则
- [ ] 限制访问 IP
- [ ] 添加速率限制

### 高级安全

- [ ] 添加认证中间件（JWT/API Key）
- [ ] 配置 HTTPS（Nginx/Caddy）
- [ ] 启用日志审计
- [ ] 设置资源限制

## 📝 文档检查

- [ ] 阅读 [QUICK_START.md](QUICK_START.md)
- [ ] 阅读 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- [ ] 阅读 [MCP_GUIDE.md](MCP_GUIDE.md)（如果使用 MCP）
- [ ] 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)（了解架构）

## 🐛 故障排除

### 常见问题

- [ ] 如果端口被占用 → 修改 `.env` 中的 `PORT`
- [ ] 如果显存不足 → 访问 `/api/offload` 释放显存
- [ ] 如果模型下载慢 → 设置 `HF_ENDPOINT=https://hf-mirror.com`
- [ ] 如果 GPU 不可用 → 检查 `nvidia-smi` 和 `nvidia-docker`
- [ ] 如果 vLLM 报错 → 回退到 `vllm==0.7.3`

### 日志查看

- [ ] 查看容器日志
  ```bash
  docker-compose logs -f
  ```

- [ ] 查看 GPU 日志
  ```bash
  nvidia-smi dmon
  ```

## ✅ 部署完成

恭喜！如果所有检查项都通过，你的 Orpheus TTS 服务已成功部署！

### 访问信息

- **UI 界面**: http://0.0.0.0:8899
- **API 文档**: http://0.0.0.0:8899/apidocs
- **健康检查**: http://0.0.0.0:8899/health

### 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看 GPU
nvidia-smi

# 测试部署
./test_deployment.sh
```

### 下一步

- [ ] 集成到你的应用
- [ ] 配置监控和告警
- [ ] 设置自动备份
- [ ] 优化性能参数
- [ ] 添加安全措施

---

**需要帮助？**
- 查看文档: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- 提交 Issue: [GitHub Issues](https://github.com/canopyai/Orpheus-TTS/issues)
