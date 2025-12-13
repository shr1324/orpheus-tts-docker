#!/bin/bash

# Orpheus TTS v1.0.0 快速启动脚本
# 模型: canopylabs/orpheus-3b-0.1-ft (bfloat16, 3B params)

set -e

echo "=== Orpheus TTS v1.0.0 (bfloat16-3b) 启动 ==="
echo ""

# 检查 HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "错误: 请设置 HF_TOKEN 环境变量"
    echo "使用方法: export HF_TOKEN=your_token"
    exit 1
fi

# 配置参数
GPU_ID=${GPU_ID:-3}
PORT=${PORT:-8899}
IDLE_TIMEOUT=${IDLE_TIMEOUT:-3600}

echo "配置信息:"
echo "  GPU: $GPU_ID"
echo "  端口: $PORT"
echo "  Idle Timeout: ${IDLE_TIMEOUT}s"
echo "  镜像: orpheus-tts:v1.0.0-allinone"
echo ""

# 停止旧容器
if docker ps -a | grep -q orpheus-tts; then
    echo "停止旧容器..."
    docker stop orpheus-tts 2>/dev/null || true
    docker rm orpheus-tts 2>/dev/null || true
fi

# 启动新容器
echo "启动容器..."
docker run -d \
  --name orpheus-tts \
  --gpus "device=$GPU_ID" \
  -p $PORT:$PORT \
  -e PORT=$PORT \
  -e GPU_IDLE_TIMEOUT=$IDLE_TIMEOUT \
  -e HF_TOKEN=$HF_TOKEN \
  -v $(pwd)/outputs:/app/outputs \
  --restart unless-stopped \
  orpheus-tts:v1.0.0-allinone

echo ""
echo "容器已启动！"
echo ""
echo "等待服务就绪 (约30秒)..."
sleep 30

# 健康检查
echo "检查服务状态..."
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "✅ 服务运行正常！"
    echo ""
    echo "访问地址:"
    echo "  Web UI: http://localhost:$PORT"
    echo "  API 文档: http://localhost:$PORT/docs"
    echo "  健康检查: http://localhost:$PORT/health"
    echo ""
    echo "查看日志: docker logs -f orpheus-tts"
else
    echo "⚠️  服务可能还在启动中，请稍后检查"
    echo "查看日志: docker logs -f orpheus-tts"
fi
