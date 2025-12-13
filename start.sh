#!/bin/bash

set -e

echo "🚀 Orpheus TTS Docker 启动脚本"
echo "================================"

# 检查 nvidia-docker
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ 错误: nvidia-smi 未找到，请确保安装了 NVIDIA 驱动"
    exit 1
fi

echo "✅ NVIDIA 驱动检测成功"

# 自动选择显存占用最少的 GPU
echo "🔍 正在检测最空闲的 GPU..."
GPU_ID=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | \
         sort -t',' -k2 -n | head -1 | cut -d',' -f1)

if [ -z "$GPU_ID" ]; then
    echo "❌ 错误: 无法检测到可用的 GPU"
    exit 1
fi

GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU_ID)
echo "✅ 选择 GPU $GPU_ID (当前显存占用: ${GPU_MEM} MB)"

# 创建 .env 文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
fi

# 设置环境变量
export NVIDIA_VISIBLE_DEVICES=$GPU_ID

# 检查端口占用
PORT=${PORT:-8899}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || ss -tuln | grep -q ":$PORT "; then
    echo "⚠️  警告: 端口 $PORT 已被占用"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建输出目录
mkdir -p outputs

# 启动 Docker Compose
echo "🐳 启动 Docker 容器..."
docker-compose up -d --build

echo ""
echo "✅ 启动成功！"
echo "================================"
echo "📊 访问信息:"
echo "  - UI 界面: http://0.0.0.0:$PORT"
echo "  - API 文档: http://0.0.0.0:$PORT/apidocs"
echo "  - 健康检查: http://0.0.0.0:$PORT/health"
echo ""
echo "🎮 使用的 GPU: $GPU_ID"
echo ""
echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo "================================"
