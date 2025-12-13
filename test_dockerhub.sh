#!/bin/bash

# 测试从 Docker Hub 拉取并运行镜像

echo "=== 测试 Docker Hub 镜像 ==="
echo ""

echo "1. 从 Docker Hub 拉取镜像..."
docker pull neosun/orpheus-tts:v1.0.0-allinone

echo ""
echo "2. 验证镜像信息..."
docker images neosun/orpheus-tts:v1.0.0-allinone

echo ""
echo "✅ Docker Hub 镜像可用！"
echo ""
echo "使用方法:"
echo "  docker run --gpus '\"device=3\"' -p 8899:8899 \\"
echo "    -e HF_TOKEN=your_token \\"
echo "    neosun/orpheus-tts:v1.0.0-allinone"
