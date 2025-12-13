import sys
sys.path.insert(0, 'orpheus_tts_pypi')

from fastmcp import FastMCP
from orpheus_tts import OrpheusModel
from gpu_manager import gpu_manager
import wave
import os

mcp = FastMCP("Orpheus-TTS")

MODEL_CONFIGS = {
    "medium-3b": "canopylabs/orpheus-3b-0.1-ft",
    "small-1b": "canopylabs/orpheus-3b-0.1-ft",
    "tiny-400m": "canopylabs/orpheus-3b-0.1-ft",
    "nano-150m": "canopylabs/orpheus-3b-0.1-ft"
}

def load_model(model_name):
    return OrpheusModel(
        model_name=MODEL_CONFIGS[model_name], 
        max_model_len=2048,
        gpu_memory_utilization=0.7
    )

@mcp.tool()
def generate_speech(
    text: str,
    output_path: str,
    model: str = "medium-3b",
    voice: str = "tara",
    temperature: float = 0.6,
    top_p: float = 0.8,
    repetition_penalty: float = 1.3
) -> dict:
    """生成语音并保存到文件
    
    Args:
        text: 要转换的文本
        output_path: 输出文件路径（.wav）
        model: 模型名称 (medium-3b, small-1b, tiny-400m, nano-150m)
        voice: 声音 (tara, leah, jess, leo, dan, mia, zac, zoe)
        temperature: 温度参数 (0.1-1.5)
        top_p: Top-p 采样 (0.1-1.0)
        repetition_penalty: 重复惩罚 (1.0-2.0)
    
    Returns:
        生成结果
    """
    try:
        if model not in MODEL_CONFIGS:
            return {'status': 'error', 'error': f'Model {model} not supported'}
        
        model_obj = gpu_manager.get_model(model, lambda: load_model(model))
        
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            
            for audio_chunk in model_obj.generate_speech(
                prompt=text,
                voice=voice,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty
            ):
                wf.writeframes(audio_chunk)
        
        return {
            'status': 'success',
            'output_path': output_path,
            'model': model,
            'voice': voice
        }
    except Exception as e:
        gpu_manager.force_offload()
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def get_gpu_status() -> dict:
    """获取 GPU 状态
    
    Returns:
        GPU 状态信息
    """
    return gpu_manager.get_status()

@mcp.tool()
def offload_gpu(model_name: str = None) -> dict:
    """释放 GPU 显存
    
    Args:
        model_name: 要释放的模型名称（不指定则释放全部）
    
    Returns:
        操作结果
    """
    gpu_manager.force_offload(model_name)
    return {'status': 'offloaded', 'gpu_status': gpu_manager.get_status()}

@mcp.tool()
def list_models() -> dict:
    """列出所有可用模型
    
    Returns:
        模型列表
    """
    return {
        'models': list(MODEL_CONFIGS.keys()),
        'voices': ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"],
        'note': 'Currently only medium-3b is available. Other models coming soon.'
    }

if __name__ == "__main__":
    mcp.run()
