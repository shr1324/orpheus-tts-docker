# Orpheus TTS API Documentation

## 📖 Overview

Orpheus TTS provides a RESTful API for text-to-speech generation with multiple access methods:

- **Interactive Swagger UI**: http://localhost:8899/apidocs/
- **OpenAPI Spec**: http://localhost:8899/apispec_1.json
- **Web UI**: http://localhost:8899/ (includes API Docs link)

## 🚀 Quick Start

### Health Check

```bash
curl http://localhost:8899/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "v2.0.0-awq-4bit",
  "model": "Hariprasath28/orpheus-3b-4bit-AWQ",
  "gpu_status": {
    "gpu_memory": 29.825,
    "loaded_models": ["medium-3b"]
  }
}
```

## 🎤 Generate Speech

### Endpoint

```
POST /api/generate
```

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "text": "Hello world, this is a test.",
  "voice": "tara",
  "temperature": 0.7,
  "top_p": 0.9,
  "repetition_penalty": 1.1
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | ✅ Yes | - | Text to convert to speech |
| `voice` | string | ✅ Yes | - | Voice name (see available voices below) |
| `temperature` | float | ❌ No | 0.7 | Sampling temperature (0.1-1.0) |
| `top_p` | float | ❌ No | 0.9 | Nucleus sampling threshold (0.1-1.0) |
| `repetition_penalty` | float | ❌ No | 1.1 | Repetition penalty (1.0-2.0) |

### Response

**Success (200):**
- Content-Type: `audio/wav`
- Binary WAV audio file (24kHz, 16-bit, mono)

**Response Headers:**
```
X-Model-Load-Time: 0.000
X-Generation-Time: 1.456
X-Total-Time: 1.456
X-Model-Version: v2.0.0-awq-4bit
```

**Error (500):**
```json
{
  "error": "Error message"
}
```

### Examples

#### Basic Usage

```bash
curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is a test.",
    "voice": "tara"
  }' \
  --output output.wav
```

#### With Custom Parameters

```bash
curl -X POST http://localhost:8899/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a more expressive speech with custom parameters.",
    "voice": "leo",
    "temperature": 0.8,
    "top_p": 0.95,
    "repetition_penalty": 1.2
  }' \
  --output custom.wav
```

#### Python Example

```python
import requests

url = "http://localhost:8899/api/generate"
payload = {
    "text": "Hello from Python!",
    "voice": "tara",
    "temperature": 0.7
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    
    # Check timing headers
    print(f"Generation time: {response.headers.get('X-Generation-Time')}s")
    print(f"Total time: {response.headers.get('X-Total-Time')}s")
else:
    print(f"Error: {response.json()}")
```

#### JavaScript Example

```javascript
async function generateSpeech(text, voice) {
  const response = await fetch('http://localhost:8899/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      voice: voice,
      temperature: 0.7
    })
  });

  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Play audio
    const audio = new Audio(url);
    audio.play();
    
    // Check timing
    console.log('Generation time:', response.headers.get('X-Generation-Time'));
  } else {
    console.error('Error:', await response.json());
  }
}

generateSpeech('Hello from JavaScript!', 'tara');
```

## 🎨 Available Voices

| Voice | Gender | Description |
|-------|--------|-------------|
| `tara` | Female | Clear and professional |
| `leah` | Female | Warm and friendly |
| `jess` | Female | Energetic and expressive |
| `mia` | Female | Soft and gentle |
| `leo` | Male | Deep and authoritative |
| `dan` | Male | Casual and conversational |
| `zac` | Male | Young and dynamic |
| `zoe` | Female | Bright and cheerful |

## 🔧 GPU Management

### Offload Model from GPU

Free GPU memory by unloading the model.

```bash
curl -X POST http://localhost:8899/api/offload
```

**Response:**
```json
{
  "status": "offloaded",
  "gpu_status": {
    "gpu_memory": 0.0,
    "loaded_models": []
  }
}
```

**Note:** Model will be automatically reloaded on next generation request (~50s load time).

## 📊 Performance Tips

### 1. Model Preloading
The model is preloaded on container startup, so first request is fast (~1.5s).

### 2. Batch Processing
For multiple requests, keep the container running to avoid reload overhead.

### 3. Parameter Tuning

**For faster generation:**
- Lower `temperature` (0.5-0.7)
- Higher `top_p` (0.9-0.95)

**For more expressive speech:**
- Higher `temperature` (0.8-1.0)
- Lower `top_p` (0.7-0.85)

### 4. Text Length
- Short text (< 20 words): ~1.5s
- Medium text (20-50 words): ~3-5s
- Long text (> 50 words): ~8-10s

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**: Deploy behind Nginx with SSL
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Authentication**: Add API key authentication
4. **CORS**: Configure CORS for specific origins

### Example Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name tts.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8899;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Rate limiting
        limit_req zone=api burst=10 nodelay;
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## 🐛 Troubleshooting

### Error: "CUDA out of memory"

**Solution:**
1. Check GPU memory: `nvidia-smi`
2. Offload model: `curl -X POST http://localhost:8899/api/offload`
3. Reduce `gpu_memory_utilization` in server config

### Error: "Model not found"

**Solution:**
1. Check HuggingFace token is set
2. Verify model access permissions
3. Check container logs: `docker logs orpheus-tts`

### Slow Generation

**Possible causes:**
1. First request after offload (model loading ~50s)
2. GPU busy with other processes
3. Long text input

**Solution:**
- Keep model loaded (don't offload)
- Check GPU usage: `nvidia-smi`
- Split long text into smaller chunks

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8899/apidocs/
- **OpenAPI Spec**: http://localhost:8899/apispec_1.json
- **GitHub**: https://github.com/neosun100/orpheus-tts-docker
- **Docker Hub**: https://hub.docker.com/r/neosun/orpheus-tts
- **Original Model**: https://huggingface.co/canopylabs/orpheus-3b-0.1-ft

## 💡 Examples Repository

Check out the `examples/` directory for more code samples:
- Python client library
- Node.js integration
- Batch processing scripts
- Voice cloning examples

## 🤝 Support

- **Issues**: https://github.com/neosun100/orpheus-tts-docker/issues
- **Discussions**: https://github.com/neosun100/orpheus-tts-docker/discussions

---

**Last Updated**: 2025-12-14  
**Version**: v2.0.0
