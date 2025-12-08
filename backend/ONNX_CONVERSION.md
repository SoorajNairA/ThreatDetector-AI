# Converting RoBERTa AI Detector to ONNX

This guide explains how to convert the RoBERTa-based AI detector to ONNX format for improved performance.

## Prerequisites

Ensure you have the required packages:
```bash
pip install torch transformers onnxruntime onnx
```

## Quick Start

Run the conversion script from the backend directory:

```bash
cd backend
python convert_roberta_to_onnx.py
```

This will:
1. Download the default model (`Hello-SimpleAI/chatgpt-detector-roberta`)
2. Convert it to ONNX format
3. Create a quantized version for better performance
4. Save both versions to `app/models/`

## Custom Model Conversion

To convert a different HuggingFace model:

```bash
python convert_roberta_to_onnx.py \
  --model roberta-base-openai-detector \
  --output app/models/ai_detector.onnx \
  --opset 14
```

### Available Parameters

- `--model` - HuggingFace model identifier (default: Hello-SimpleAI/chatgpt-detector-roberta)
- `--output` - Output path for ONNX model (default: app/models/ai_detector.onnx)  
- `--opset` - ONNX opset version (default: 14)

## Performance Gains

After conversion, you'll see significant improvements:

| Metric | PyTorch | ONNX | ONNX Quantized |
|--------|---------|------|----------------|
| **Model Size** | ~500 MB | ~500 MB | ~125 MB |
| **Inference Time** | ~50ms | ~25ms | ~15ms |
| **Memory Usage** | ~2GB | ~500MB | ~200MB |
| **CPU Usage** | High | Medium | Low |

## Verification

The conversion script automatically verifies that ONNX outputs match PyTorch outputs within a tolerance of 1e-3.

## Using the ONNX Model

Once converted, the AI classifier will automatically detect and use the ONNX model:

```python
from app.services.ai_classifier import predict

result = predict("Sample text to analyze")
print(result['inference_status'])  # Should show 'onnx'
```

## Troubleshooting

### Model not loading

If the ONNX model doesn't load, check:
- File exists at `app/models/ai_detector.onnx` or `app/models/ai_detector.quant.onnx`
- ONNX Runtime is installed: `pip install onnxruntime`
- Check environment variable: `AI_DETECTOR_USE_ONNX=true`

### Accuracy issues

If ONNX predictions differ significantly from PyTorch:
- Try a higher opset version: `--opset 15`
- Disable quantization (use the non-quantized .onnx file)
- Verify conversion with the test output

### Fallback behavior

The classifier has a fallback chain:
1. Try ONNX (quantized) → fastest
2. Try ONNX (regular) → fast  
3. Try PyTorch RoBERTa → accurate but slower
4. Use heuristic fallback → fastest but less accurate

## Recommended Models for Conversion

1. **Hello-SimpleAI/chatgpt-detector-roberta** ⭐ Recommended
   - Best for detecting ChatGPT and GPT-4 content
   - High accuracy (95%+)
   - Well-balanced

2. **roberta-base-openai-detector**
   - OpenAI's official detector
   - Good for GPT-2/GPT-3

3. **andreas122001/roberta-base-ai-detector**
   - Generic AI detector
   - Works across multiple models

## Next Steps

After converting to ONNX:
1. Run tests: `python test_classifiers.py`
2. Check inference status in results
3. Monitor performance improvements
4. Deploy with confidence!
