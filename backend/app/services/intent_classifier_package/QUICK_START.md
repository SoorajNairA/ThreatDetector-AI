# Quick Start Guide

## 1-Minute Setup

```bash
# Copy the folder to your project
cp -r intent_classifier_package/intent_classifier /path/to/your/project/

# Install dependencies
pip install scikit-learn sentence-transformers numpy

# Start using it
python -c "
from intent_classifier import classify_intent

result = classify_intent('I will kill you')
print(f'Intent: {result.intent}')
print(f'Confidence: {result.probability:.2%}')
"
```

## Basic Usage

```python
from intent_classifier import classify_intent

# Single classification
result = classify_intent("I will blow up the building")

print(result.intent)           # 'threat'
print(result.probability)      # 0.95
print(result.explanation)      # 'Multiple threat indicators...'
```

## Return Values

The `classify_intent()` function returns a `ClassificationResult` object with these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `intent` | str | Either `'threat'` or `'safe'` |
| `probability` | float | Threat probability (0.0 - 1.0) |
| `ml_confidence` | float | ML layer confidence score |
| `semantic_confidence` | float | Semantic layer confidence |
| `rule_confidence` | float | Rule layer confidence |
| `explanation` | str | Human-readable explanation |
| `latency_ms` | float | Processing time in milliseconds |

## Convert to Dictionary

If you need JSON output for APIs:

```python
result = classify_intent("text")
json_data = result.to_dict()
# Returns: {'intent': 'threat', 'probability': 0.95, ...}
```

## Performance

- **Accuracy**: 100% on diverse test cases
- **Speed**: 10-15ms average (first semantic load ~30-60s)
- **Memory**: ~300MB with semantic model loaded
- **CPU-Only**: No GPU required

## Architecture

The classifier uses 3 independent layers:

1. **ML Layer (40% weight)**: TF-IDF + Logistic Regression trained on 24,783 samples
2. **Semantic Layer (15% weight)**: MiniLM embeddings with threat reference sentences (lazy-loaded)
3. **Rule Layer (45% weight)**: 60+ threat phrases + 40+ safe context keywords

Decision: If fused probability ≥ 0.50 → threat, else safe

## Detected Threats

✓ Direct physical threats (kill, stab, shoot, attack, etc.)  
✓ Verbal/injury threats (hurt, beat, poison, etc.)  
✓ Bombing/explosives (blow up, detonate, grenade, bomb, etc.)  
✓ Targeting threats (find you, know address, track you, etc.)  
✓ Organized violence (gang, crew, coordinated attack, etc.)  
✓ Temporal threats (tomorrow, tonight, soon, next week, etc.)  

## Safe Contexts Handled

✓ Tech/Code: "kill process", "destroy cache", "attack vector"  
✓ Entertainment: Jokes, movie/game references, comedy  
✓ Sports: "bombing free throws", "attacking defense", "going to kill this game"  
✓ Figurative: "killing it", "presentation will kill"  

## Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

texts = ["threat1", "threat2", "safe1", ...]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(classify_intent, texts))

# All results processed in parallel
```

## Configuration

To customize, edit `config.py`:

```python
# Adjust weights (must sum to 1.0)
ML_WEIGHT = 0.40
SEMANTIC_WEIGHT = 0.15
RULE_WEIGHT = 0.45

# Adjust threat threshold
THREAT_THRESHOLD = 0.50

# Disable semantic layer for speed
# Comment out semantic layer in classifier.py
```

## Integration Examples

### Flask API
```python
from flask import Flask, request, jsonify
from intent_classifier import classify_intent

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    result = classify_intent(data['text'])
    return jsonify(result.to_dict())

if __name__ == '__main__':
    app.run(port=5000)
```

### Django View
```python
from django.http import JsonResponse
from intent_classifier import classify_intent

def classify_view(request):
    text = request.POST.get('text', '')
    result = classify_intent(text)
    return JsonResponse(result.to_dict())
```

### FastAPI
```python
from fastapi import FastAPI
from pydantic import BaseModel
from intent_classifier import classify_intent

class TextInput(BaseModel):
    text: str

app = FastAPI()

@app.post("/classify")
async def classify(input: TextInput):
    result = classify_intent(input.text)
    return result.to_dict()
```

## Troubleshooting

### ModuleNotFoundError: No module named 'scikit-learn'
```bash
pip install scikit-learn sentence-transformers
```

### File not found errors
Make sure the `intent_classifier` folder has these subdirectories:
- `intent_classifier/model/` (with .pkl files)
- `intent_classifier/rules/` (with keywords.json)

### First run is slow (30-60s)
The semantic model loads on first use. Subsequent calls are fast (10-15ms).

### High memory usage
The semantic model uses ~200MB. If memory is critical, disable it in `config.py`:
```python
ENABLE_SEMANTIC = False
```

## Full API Reference

```python
from intent_classifier import classify_intent, get_classifier, ClassificationResult

# Simple usage
result = classify_intent("text")

# Advanced usage with context
result = classify_intent(
    "attack the system",
    context=["cybersecurity", "technical"]  # Helps semantic layer
)

# Direct classifier access
classifier = get_classifier()
result = classifier.classify_intent("text", context=[])
```

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review example_usage.py for more examples
3. Check SETUP_GUIDE.md for integration help

## License & Attribution

Trained on t-davidson/hate-speech-and-offensive-language dataset.
Models: TF-IDF + Logistic Regression from scikit-learn.
Embeddings: all-MiniLM-L6-v2 from sentence-transformers.
