# Intent Classifier - Setup Guide

## Quick Setup (5 minutes)

### Step 1: Copy the Package
```bash
cp -r intent_classifier /path/to/your/project/
```

### Step 2: Install Dependencies
```bash
cd /path/to/your/project
pip install -r intent_classifier/requirements.txt
```

Or install individually:
```bash
pip install scikit-learn>=1.0.0 sentence-transformers>=2.0.0 numpy>=1.20.0
```

### Step 3: Use in Your Code
```python
from intent_classifier import classify_intent

# Single prediction
result = classify_intent("I will kill you")
print(result['intent'])  # 'threat'
print(result['probability'])  # 0.873

# Batch processing
texts = ["I will kill you", "Let's go to the movies", "Kill the process"]
results = [classify_intent(text) for text in texts]
```

### Step 4: Test Installation
```bash
python example_usage.py
```

Expected output:
```
INTENT CLASSIFIER - USAGE EXAMPLES
============================================================================================

1. DIRECT THREAT DETECTION
----
Text: 'I will kill you tomorrow'
Intent: THREAT
Confidence: 78.9%
```

## What's Included

```
intent_classifier/
├── __init__.py              # Main API entry point
├── classifier.py            # Core classification engine
├── config.py                # Configuration settings
├── model/
│   ├── tfidf.pkl           # TF-IDF vectorizer (187KB)
│   └── logistic.pkl        # Logistic Regression model (41KB)
├── rules/
│   └── keywords.json       # 50+ threat phrases, 40+ safe keywords
├── requirements.txt        # Python dependencies
└── README.md              # Full documentation
```

## Integration Examples

### Flask Web Service
```python
from flask import Flask, request, jsonify
from intent_classifier import classify_intent

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    text = data.get('text', '')
    result = classify_intent(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### Django View
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from intent_classifier import classify_intent

@require_http_methods(["POST"])
def classify_threat(request):
    import json
    data = json.loads(request.body)
    text = data.get('text', '')
    result = classify_intent(text)
    return JsonResponse(result)
```

### FastAPI Endpoint
```python
from fastapi import FastAPI
from pydantic import BaseModel
from intent_classifier import classify_intent

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/classify")
def classify_text(input_data: TextInput):
    result = classify_intent(input_data.text)
    return result
```

### Batch Processing
```python
from intent_classifier import classify_intent
import pandas as pd

# Process CSV file
df = pd.read_csv('messages.csv')
df['intent'] = df['text'].apply(lambda x: classify_intent(x)['intent'])
df['confidence'] = df['text'].apply(lambda x: classify_intent(x)['probability'])
df.to_csv('classified_messages.csv', index=False)
```

### Real-time Chat Monitoring
```python
from intent_classifier import classify_intent

def monitor_chat_message(user_id, message):
    result = classify_intent(message)
    
    if result['intent'] == 'threat':
        # Alert moderators
        print(f"ALERT: Threat detected from user {user_id}")
        print(f"Message: {message}")
        print(f"Confidence: {result['probability']:.1%}")
        # Log to database
        log_threat(user_id, message, result['probability'])
    
    return result

def log_threat(user_id, message, confidence):
    # Your logging logic here
    pass
```

## Performance Tips

1. **First Run Optimization**: The semantic model (~330MB) downloads on first use.
   - Cache it during application startup: `from intent_classifier import get_classifier; get_classifier()`

2. **Batch Processing**: Process multiple texts in parallel using ThreadPool/ProcessPool:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   from intent_classifier import classify_intent
   
   texts = [...1000 items...]
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = list(executor.map(classify_intent, texts))
   ```

3. **Caching Results**: Cache predictions for duplicate inputs:
   ```python
   from functools import lru_cache
   from intent_classifier import classify_intent
   
   @lru_cache(maxsize=1000)
   def classify_cached(text):
       return classify_intent(text)
   ```

## Configuration Customization

Edit `config.py` to adjust:

```python
# 1. Change fusion weights (adjust how much each layer contributes)
FUSION_WEIGHTS = {
    "ml": 0.50,        # Increase ML weight
    "semantic": 0.20,  # Increase semantic
    "rule": 0.30       # Decrease rule
}

# 2. Change threshold (lower = more sensitive to threats)
THREAT_THRESHOLD = 0.45  # was 0.50

# 3. Disable semantic layer (for faster inference, less memory)
# Edit _load_semantic_layer() in classifier.py to skip loading
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sklearn'"
**Solution**: Install scikit-learn
```bash
pip install scikit-learn
```

### Issue: "Model files not found"
**Solution**: Ensure the folder structure is correct:
```
your_project/
└── intent_classifier/
    ├── __init__.py
    ├── model/
    │   ├── tfidf.pkl
    │   └── logistic.pkl
    └── rules/
        └── keywords.json
```

### Issue: Semantic model takes too long to load
**Solution**: Pre-load it on app startup:
```python
# In your main application file
from intent_classifier import get_classifier
print("Loading classifier...")
classifier = get_classifier()
print("Ready!")
```

### Issue: High memory usage
**Solution**: The semantic model (~300MB) is lazy-loaded. If you don't need semantic matching:
1. Edit `classifier.py`
2. Comment out the semantic layer call in `__init__`
3. Adjust fusion weights accordingly

## API Response Examples

### Threat Example
```json
{
    "intent": "threat",
    "probability": 0.873,
    "ml_confidence": 0.682,
    "semantic_confidence": 0.0,
    "rule_confidence": 1.0,
    "explanation": "Multiple threat indicators detected: direct threat keywords (kill), intent indicator (will), addressing target (you)",
    "latency_ms": 12.34
}
```

### Safe Example
```json
{
    "intent": "safe",
    "probability": 0.337,
    "ml_confidence": 0.603,
    "semantic_confidence": 0.0,
    "rule_confidence": 0.1,
    "explanation": "Safe context detected: technical/programming context (process, background)",
    "latency_ms": 8.51
}
```

## Next Steps

1. Run `python example_usage.py` to test basic functionality
2. Review README.md for detailed API documentation
3. Integrate into your application
4. Monitor predictions and adjust configuration if needed
5. Consider retraining with your domain-specific data for best results

## Support

- **Documentation**: See README.md in the classifier folder
- **Examples**: Run `python example_usage.py`
- **Configuration**: Edit `intent_classifier/config.py`
- **Training**: Use `intent_classifier.train_model.ModelTrainer` for custom data

## Version Info

- **Package Version**: 1.0.0
- **Status**: Production Ready ✓
- **Python**: 3.8+
- **Dependencies**: scikit-learn, sentence-transformers, numpy

---

**Ready to use!** Copy the `intent_classifier` folder to your project and start classifying.
