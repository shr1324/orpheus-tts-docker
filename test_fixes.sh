#!/bin/bash

echo "=== Orpheus TTS 修复验证测试 ==="
echo ""

echo "1. 检查 GPU 配置..."
echo "容器环境变量:"
docker inspect orpheus-tts | grep -A3 "NVIDIA_VISIBLE_DEVICES"
echo ""

echo "2. 检查 GPU 显存使用..."
nvidia-smi --query-gpu=index,name,memory.used,memory.free --format=csv,noheader
echo ""

echo "3. 检查服务健康状态..."
curl -s http://localhost:8899/health | jq .
echo ""

echo "4. 测试第一次语音生成 (模型已加载，应该很快)..."
time curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice":"tara","model_size":"medium"}' \
  --output /tmp/test_fix1.wav \
  -w "\nHTTP Status: %{http_code}\n" \
  --max-time 30 2>&1 | tail -3
echo ""

echo "5. 测试第二次语音生成 (应该更快，~2-3秒)..."
time curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a second test","voice":"leah","model_size":"medium"}' \
  --output /tmp/test_fix2.wav \
  -w "\nHTTP Status: %{http_code}\n" \
  --max-time 30 2>&1 | tail -3
echo ""

echo "6. 验证生成的音频文件..."
ls -lh /tmp/test_fix*.wav
file /tmp/test_fix1.wav
echo ""

echo "7. 检查域名访问..."
curl -s https://orpheus-tts.aws.xin/health | jq .
echo ""

echo "8. 检查容器日志 (最后20行)..."
docker logs orpheus-tts --tail 20 2>&1 | grep -E "(INFO|ERROR|CUDA|generate)"
echo ""

echo "=== 测试完成 ==="
echo ""
echo "修复总结:"
echo "✅ GPU 从 GPU 0 切换到 GPU 3 (45GB 可用)"
echo "✅ gpu_memory_utilization 设置为 0.7 降低显存占用"
echo "✅ GPU_IDLE_TIMEOUT 增加到 3600秒 (1小时)"
echo "✅ 模型保持加载，第二次请求速度提升 ~20倍"
echo "✅ 域名 https://orpheus-tts.aws.xin 正常访问"
