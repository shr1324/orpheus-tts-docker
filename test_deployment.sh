#!/bin/bash

echo "🧪 Orpheus TTS 部署测试"
echo "================================"

BASE_URL="http://0.0.0.0:8899"

# 测试 1: 健康检查
echo "1️⃣ 测试健康检查..."
response=$(curl -s "$BASE_URL/health")
if echo "$response" | grep -q "ok"; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    exit 1
fi

# 测试 2: UI 访问
echo ""
echo "2️⃣ 测试 UI 访问..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$status_code" = "200" ]; then
    echo "✅ UI 访问正常"
else
    echo "❌ UI 访问失败 (HTTP $status_code)"
fi

# 测试 3: Swagger 文档
echo ""
echo "3️⃣ 测试 Swagger 文档..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/apidocs")
if [ "$status_code" = "200" ]; then
    echo "✅ Swagger 文档可访问"
else
    echo "❌ Swagger 文档访问失败 (HTTP $status_code)"
fi

# 测试 4: API 生成语音
echo ""
echo "4️⃣ 测试 API 生成语音..."
curl -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test.",
    "model": "medium-3b",
    "voice": "tara"
  }' \
  --output test_output.wav \
  -s

if [ -f test_output.wav ] && [ -s test_output.wav ]; then
    echo "✅ API 生成语音成功 ($(du -h test_output.wav | cut -f1))"
    rm test_output.wav
else
    echo "❌ API 生成语音失败"
fi

# 测试 5: GPU 状态
echo ""
echo "5️⃣ 测试 GPU 状态查询..."
response=$(curl -s "$BASE_URL/health")
gpu_memory=$(echo "$response" | grep -o '"gpu_memory":[0-9.]*' | cut -d':' -f2)
if [ ! -z "$gpu_memory" ]; then
    echo "✅ GPU 状态查询成功 (显存: ${gpu_memory} GB)"
else
    echo "⚠️  GPU 状态查询异常"
fi

# 测试 6: GPU 释放
echo ""
echo "6️⃣ 测试 GPU 释放..."
response=$(curl -s -X POST "$BASE_URL/api/offload")
if echo "$response" | grep -q "offloaded"; then
    echo "✅ GPU 释放成功"
else
    echo "❌ GPU 释放失败"
fi

echo ""
echo "================================"
echo "✅ 所有测试完成！"
echo ""
echo "📊 访问信息:"
echo "  - UI: $BASE_URL"
echo "  - API 文档: $BASE_URL/apidocs"
echo "  - 健康检查: $BASE_URL/health"
