# AI Detector Models

This directory contains ONNX models for AI-generated text detection.

## Converting RoBERTa to ONNX

To convert a HuggingFace RoBERTa model to ONNX format for faster inference:

```bash
# From the backend directory
python convert_roberta_to_onnx.py --model Hello-SimpleAI/chatgpt-detector-roberta --output app/models/ai_detector.onnx
```

### Supported Models

1. **Hello-SimpleAI/chatgpt-detector-roberta** (Recommended)
   - Fine-tuned for ChatGPT detection
   - High accuracy on AI-generated content
   - Good balance of speed and performance

2. **roberta-base-openai-detector**
   - OpenAI's official detector
   - Trained on GPT-2 outputs

3. **andreas122001/roberta-base-ai-detector**
   - Generic AI content detector
   - Works across multiple AI models

### Conversion Process

The conversion script will:
1. Download the HuggingFace model
2. Convert to ONNX format with dynamic shapes
3. Quantize to INT8 for 4x smaller size and faster inference
4. Validate conversion accuracy

### Performance Comparison

| Format | Size | Inference Time | Memory Usage |
|--------|------|----------------|--------------|
| PyTorch | ~500 MB | ~50ms | ~2GB RAM |
| ONNX | ~500 MB | ~25ms | ~500MB RAM |
| ONNX Quantized | ~125 MB | ~15ms | ~200MB RAM |

### Usage

The AI classifier automatically detects and uses ONNX models if available:

```python
from app.services.ai_classifier import predict

result = predict("This is a test text to analyze")
print(result['inference_status'])  # 'onnx', 'pytorch', or 'heuristic'
```

### Environment Variables

- `AI_DETECTOR_USE_ONNX=true/false` - Enable/disable ONNX (default: true)
- `AI_DETECTOR_MODEL=<model_name>` - HuggingFace model for PyTorch fallback
- `AI_DETECTOR_TOKENIZER=<tokenizer_name>` - Tokenizer for ONNX model
- `AI_DETECT_THRESHOLD=0.5` - Classification threshold (0-1)

## Model Files

Place converted models in this directory:
- `ai_detector.onnx` - Full precision ONNX model
- `ai_detector.quant.onnx` - Quantized ONNX model (preferred)

The classifier will automatically use the quantized version if available.
