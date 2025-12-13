FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY orpheus_tts_pypi /app/orpheus_tts_pypi
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8899

# v1.5: 使用启动脚本支持模型预加载
CMD ["bash", "-c", "python3 -c 'import sys; sys.path.insert(0, \"orpheus_tts_pypi\"); from server import app, preload_models; import os; preload_models(); app.run(host=\"0.0.0.0\", port=int(os.environ.get(\"PORT\", 8899)), debug=False)'"]
