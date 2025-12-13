#!/bin/bash
# Orpheus TTS v1.5 启动脚本 - 包含模型预加载

echo "🚀 Starting Orpheus TTS v1.5..."
echo "📦 Features: Model Preloading + Voice Cloning + Timing Display"

# 启动服务并预加载模型
python3 -c "
import sys
sys.path.insert(0, 'orpheus_tts_pypi')
from server import app, preload_models
import os

# 预加载模型
preload_models()

# 启动服务
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8899)), debug=False)
"
