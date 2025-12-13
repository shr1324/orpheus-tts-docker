import torch
import time
import threading
import os

class GPUManager:
    def __init__(self, idle_timeout=60):
        self.models = {}
        self.last_used = {}
        self.idle_timeout = int(os.environ.get('GPU_IDLE_TIMEOUT', idle_timeout))
        self.lock = threading.Lock()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        def cleanup():
            while True:
                time.sleep(10)
                self._cleanup_idle_models()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_idle_models(self):
        with self.lock:
            current_time = time.time()
            to_remove = []
            for name, last_time in self.last_used.items():
                if current_time - last_time > self.idle_timeout:
                    to_remove.append(name)
            
            for name in to_remove:
                if name in self.models:
                    del self.models[name]
                    del self.last_used[name]
                    torch.cuda.empty_cache()
    
    def get_model(self, model_name, load_func):
        with self.lock:
            if model_name not in self.models:
                self.models[model_name] = load_func()
            self.last_used[model_name] = time.time()
            return self.models[model_name]
    
    def force_offload(self, model_name=None):
        with self.lock:
            if model_name:
                if model_name in self.models:
                    del self.models[model_name]
                    del self.last_used[model_name]
            else:
                self.models.clear()
                self.last_used.clear()
            torch.cuda.empty_cache()
    
    def get_status(self):
        with self.lock:
            return {
                'loaded_models': list(self.models.keys()),
                'gpu_memory': torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
            }

gpu_manager = GPUManager()
