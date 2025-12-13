import sys
sys.path.insert(0, 'orpheus_tts_pypi')

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flasgger import Swagger
from orpheus_tts import OrpheusModel
from gpu_manager import gpu_manager
import wave
import io
import os
import uuid
import time
import base64
import tempfile

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# 输出目录配置 - 使用宿主机挂载路径保护隐私
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/app/outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_CONFIGS = {
    "medium-3b": "canopylabs/orpheus-3b-0.1-ft",
    "small-1b": "canopylabs/orpheus-3b-0.1-ft",
    "tiny-400m": "canopylabs/orpheus-3b-0.1-ft",
    "nano-150m": "canopylabs/orpheus-3b-0.1-ft"
}

VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]

def load_model(model_name):
    return OrpheusModel(
        model_name=MODEL_CONFIGS[model_name], 
        max_model_len=2048,
        gpu_memory_utilization=0.7
    )

# 预加载模型到显存
def preload_models():
    """启动时预加载默认模型到显存"""
    print("🚀 Preloading model to GPU...")
    start_time = time.time()
    try:
        model = gpu_manager.get_model("medium-3b", lambda: load_model("medium-3b"))
        elapsed = time.time() - start_time
        print(f"✅ Model preloaded in {elapsed:.2f}s")
        return True
    except Exception as e:
        print(f"⚠️  Model preload failed: {e}")
        return False

@app.route('/')
def index():
    return render_template_string(UI_HTML)

@app.route('/health')
def health():
    """健康检查
    ---
    tags:
      - System
    responses:
      200:
        description: 服务正常
    """
    return jsonify({'status': 'ok', 'gpu_status': gpu_manager.get_status()})

@app.route('/api/generate', methods=['POST'])
def generate():
    """生成语音
    ---
    tags:
      - TTS
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: 要转换的文本
            model_size:
              type: string
              enum: [medium, small, tiny, nano]
              default: medium
            voice:
              type: string
              enum: [tara, leah, jess, leo, dan, mia, zac, zoe, custom]
              default: tara
            voice_audio:
              type: string
              description: Base64编码的参考音频（用于零样本克隆）
            temperature:
              type: number
              default: 0.6
            top_p:
              type: number
              default: 0.8
            repetition_penalty:
              type: number
              default: 1.3
    responses:
      200:
        description: 生成成功
    """
    start_time = time.time()
    
    data = request.json
    text = data.get('text', '')
    model_size = data.get('model_size', 'medium')
    voice = data.get('voice', 'tara')
    voice_audio = data.get('voice_audio')  # Base64 encoded audio
    temperature = data.get('temperature', 0.6)
    top_p = data.get('top_p', 0.8)
    repetition_penalty = data.get('repetition_penalty', 1.3)
    
    model_name = f"{model_size}-3b" if model_size == "medium" else f"{model_size}-1b"
    if model_name not in MODEL_CONFIGS:
        model_name = "medium-3b"
    
    try:
        model_load_start = time.time()
        model = gpu_manager.get_model(model_name, lambda: load_model(model_name))
        model_load_time = time.time() - model_load_start
        
        # 处理零样本语音克隆
        if voice == "custom" and voice_audio:
            # TODO: 实现自定义语音克隆
            # 当前版本使用默认语音
            voice = "tara"
        
        generation_start = time.time()
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            
            for audio_chunk in model.generate_speech(
                prompt=text,
                voice=voice,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty
            ):
                wf.writeframes(audio_chunk)
        
        generation_time = time.time() - generation_start
        total_time = time.time() - start_time
        
        audio_buffer.seek(0)
        
        # 添加计时信息到响应头
        response = send_file(audio_buffer, mimetype='audio/wav', as_attachment=True, download_name='output.wav')
        response.headers['X-Model-Load-Time'] = f"{model_load_time:.3f}"
        response.headers['X-Generation-Time'] = f"{generation_time:.3f}"
        response.headers['X-Total-Time'] = f"{total_time:.3f}"
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offload', methods=['POST'])
def offload():
    """释放 GPU 显存
    ---
    tags:
      - System
    parameters:
      - name: model
        in: query
        type: string
        description: 要释放的模型名称（不指定则释放全部）
    responses:
      200:
        description: 释放成功
    """
    model_name = request.args.get('model')
    gpu_manager.force_offload(model_name)
    return jsonify({'status': 'offloaded', 'gpu_status': gpu_manager.get_status()})

UI_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orpheus TTS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f0f; color: #e0e0e0; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; margin-bottom: 30px; color: #fff; }
        .card { background: #1a1a1a; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #b0b0b0; }
        textarea, select, input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #2a2a2a; color: #e0e0e0; font-size: 14px; }
        textarea { min-height: 120px; resize: vertical; font-family: inherit; }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        button { width: 100%; padding: 14px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .progress { height: 4px; background: #333; border-radius: 2px; overflow: hidden; margin: 20px 0; display: none; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: 0%; transition: width 0.3s; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .status { text-align: center; margin: 15px 0; color: #888; }
        .gpu-status { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #2a2a2a; border-radius: 8px; margin-bottom: 20px; }
        .gpu-status button { width: auto; padding: 8px 16px; font-size: 14px; }
        audio { width: 100%; margin-top: 15px; }
        .lang-switch { position: absolute; top: 20px; right: 20px; }
        @media (max-width: 768px) { .row { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <select class="lang-switch" id="language" onchange="switchLanguage()">
        <option value="en">English</option>
        <option value="zh-CN">简体中文</option>
    </select>
    
    <div class="container">
        <h1 data-i18n="title">Orpheus TTS</h1>
        
        <div class="card">
            <div class="gpu-status">
                <span data-i18n="gpu">GPU: <span id="gpu-status">-</span></span>
                <button onclick="offloadGPU()" data-i18n="offload">释放显存</button>
            </div>
            
            <div class="form-group">
                <label data-i18n="text">文本</label>
                <textarea id="text" placeholder="输入要转换的文本..."></textarea>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label data-i18n="model">模型</label>
                    <select id="model">
                        <option value="medium-3b">Medium (3B)</option>
                        <option value="small-1b">Small (1B) - 即将推出</option>
                        <option value="tiny-400m">Tiny (400M) - 即将推出</option>
                        <option value="nano-150m">Nano (150M) - 即将推出</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label data-i18n="voice">声音</label>
                    <select id="voice">
                        <option value="tara">Tara</option>
                        <option value="leah">Leah</option>
                        <option value="jess">Jess</option>
                        <option value="leo">Leo</option>
                        <option value="dan">Dan</option>
                        <option value="mia">Mia</option>
                        <option value="zac">Zac</option>
                        <option value="zoe">Zoe</option>
                        <option value="custom">🎤 自定义语音克隆</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group" id="voice-clone-section" style="display: none;">
                <label data-i18n="voiceFile">参考音频文件（用于零样本克隆）</label>
                <input type="file" id="voice-file" accept="audio/*" style="padding: 8px;">
                <small style="color: #888; display: block; margin-top: 5px;">上传3-10秒的清晰语音样本</small>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>Temperature: <span id="temp-val">0.6</span></label>
                    <input type="range" id="temperature" min="0.1" max="1.5" step="0.1" value="0.6" oninput="document.getElementById('temp-val').textContent=this.value">
                </div>
                
                <div class="form-group">
                    <label>Top P: <span id="topp-val">0.8</span></label>
                    <input type="range" id="top_p" min="0.1" max="1.0" step="0.1" value="0.8" oninput="document.getElementById('topp-val').textContent=this.value">
                </div>
            </div>
            
            <div class="form-group">
                <label>Repetition Penalty: <span id="rep-val">1.3</span></label>
                <input type="range" id="repetition_penalty" min="1.0" max="2.0" step="0.1" value="1.3" oninput="document.getElementById('rep-val').textContent=this.value">
            </div>
            
            <button onclick="generate()" data-i18n="generate">生成语音</button>
            
            <div class="progress" id="progress">
                <div class="progress-bar"></div>
            </div>
            
            <div class="status" id="status"></div>
            
            <audio id="audio" controls style="display:none"></audio>
            
            <div id="timing" style="display:none"></div>
        </div>
    </div>
    
    <script>
        const i18n = {
            'en': {
                title: 'Orpheus TTS',
                gpu: 'GPU: ',
                offload: 'Offload GPU',
                text: 'Text',
                model: 'Model',
                voice: 'Voice',
                generate: 'Generate Speech',
                generating: 'Generating...',
                success: 'Generated successfully!',
                error: 'Error: '
            },
            'zh-CN': {
                title: 'Orpheus TTS 语音合成',
                gpu: 'GPU: ',
                offload: '释放显存',
                text: '文本',
                model: '模型',
                voice: '声音',
                generate: '生成语音',
                generating: '生成中...',
                success: '生成成功！',
                error: '错误: '
            }
        };
        
        let currentLang = 'zh-CN';
        
        function switchLanguage() {
            currentLang = document.getElementById('language').value;
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[currentLang][key]) {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        el.placeholder = i18n[currentLang][key];
                    } else {
                        const parts = el.innerHTML.split('<span');
                        if (parts.length > 1) {
                            el.innerHTML = i18n[currentLang][key] + '<span' + parts[1];
                        } else {
                            el.textContent = i18n[currentLang][key];
                        }
                    }
                }
            });
        }
        
        async function updateGPUStatus() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('gpu-status').textContent = 
                    `${data.gpu_status.gpu_memory.toFixed(2)} GB (${data.gpu_status.loaded_models.length} models)`;
            } catch (e) {
                document.getElementById('gpu-status').textContent = 'Error';
            }
        }
        
        async function generate() {
            const text = document.getElementById('text').value;
            if (!text) return alert('请输入文本');
            
            const btn = event.target;
            const voice = document.getElementById('voice').value;
            const voiceFile = document.getElementById('voice-file').files[0];
            
            btn.disabled = true;
            btn.textContent = i18n[currentLang].generating;
            document.getElementById('progress').style.display = 'block';
            document.getElementById('status').textContent = '';
            document.getElementById('timing').style.display = 'none';
            
            try {
                const requestData = {
                    text,
                    model_size: 'medium',
                    voice,
                    temperature: parseFloat(document.getElementById('temperature').value),
                    top_p: parseFloat(document.getElementById('top_p').value),
                    repetition_penalty: parseFloat(document.getElementById('repetition_penalty').value)
                };
                
                // 处理自定义语音克隆
                if (voice === 'custom' && voiceFile) {
                    const reader = new FileReader();
                    requestData.voice_audio = await new Promise((resolve) => {
                        reader.onload = () => resolve(reader.result.split(',')[1]);
                        reader.readAsDataURL(voiceFile);
                    });
                }
                
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(requestData)
                });
                
                if (!res.ok) throw new Error(await res.text());
                
                // 获取计时信息
                const modelLoadTime = res.headers.get('X-Model-Load-Time') || '0';
                const generationTime = res.headers.get('X-Generation-Time') || '0';
                const totalTime = res.headers.get('X-Total-Time') || '0';
                
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const audio = document.getElementById('audio');
                audio.src = url;
                audio.style.display = 'block';
                audio.play();
                
                // 显示计时信息
                const timingDiv = document.getElementById('timing');
                timingDiv.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;">
                        <div style="text-align: center; padding: 10px; background: #2a2a2a; border-radius: 8px;">
                            <div style="font-size: 12px; color: #888;">模型加载</div>
                            <div style="font-size: 20px; font-weight: bold; color: #667eea;">${modelLoadTime}s</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: #2a2a2a; border-radius: 8px;">
                            <div style="font-size: 12px; color: #888;">音频生成</div>
                            <div style="font-size: 20px; font-weight: bold; color: #764ba2;">${generationTime}s</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: #2a2a2a; border-radius: 8px;">
                            <div style="font-size: 12px; color: #888;">总耗时</div>
                            <div style="font-size: 20px; font-weight: bold; color: #4ade80;">${totalTime}s</div>
                        </div>
                    </div>
                `;
                timingDiv.style.display = 'block';
                
                document.getElementById('status').textContent = i18n[currentLang].success;
                updateGPUStatus();
            } catch (e) {
                document.getElementById('status').textContent = i18n[currentLang].error + e.message;
            } finally {
                btn.disabled = false;
                btn.textContent = i18n[currentLang].generate;
                document.getElementById('progress').style.display = 'none';
            }
        }
        
        async function offloadGPU() {
            await fetch('/api/offload', {method: 'POST'});
            updateGPUStatus();
        }
        
        updateGPUStatus();
        setInterval(updateGPUStatus, 5000);
        switchLanguage();
        
        // 语音克隆选项切换
        document.getElementById('voice').addEventListener('change', function() {
            const voiceCloneSection = document.getElementById('voice-clone-section');
            voiceCloneSection.style.display = this.value === 'custom' ? 'block' : 'none';
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8899)), debug=False)
