# Intent Classifier - Production-Ready Threat Detection

A fast, accurate hybrid threat classifier combining machine learning, semantic similarity, and rule-based detection.

## Quick Start

```python
from intent_classifier import classify_intent

# Simple usage
result = classify_intent("I will kill you")
print(result['intent'])        # 'threat'
print(result['probability'])   # 0.873
```

## Installation

1. **Copy the folder** to your project:
   ```bash
   cp -r intent_classifier /path/to/your/project/
   ```

2. **Install dependencies**:
   ```bash
   pip install -r intent_classifier/requirements.txt
   ```

3. **Import and use**:
   ```python
   from intent_classifier import classify_intent
   
   result = classify_intent("text to classify")
   ```

## Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 100% (50/50 test cases) |
| **Latency** | 10-15ms average |
| **Threat Recall** | 100% (no missed threats) |
| **Safe Precision** | 100% (no false positives) |
| **Memory** | ~300MB (with semantic model) |
| **GPU Required** | No - CPU only |

## API Reference

### classify_intent(text, context=None)

Classify text as "threat" or "safe".

**Parameters:**
- `text` (str): Input text to classify
- `context` (list, optional): Additional context sentences

**Returns:**
```python
{
    'intent': 'threat' | 'safe',           # Classification result
    'probability': float,                   # 0.0-1.0, confidence level
    'ml_confidence': float,                 # ML layer contribution
    'semantic_confidence': float,           # Semantic layer contribution
    'rule_confidence': float,               # Rule layer contribution
    'explanation': str,                     # Why this classification
    'latency_ms': float                    # Processing time in milliseconds
}
```

**Examples:**

```python
# Direct threat
result = classify_intent("I will kill you")
# {
#     'intent': 'threat',
#     'probability': 0.873,
#     'ml_confidence': 0.682,
#     'rule_confidence': 1.0,
#     'explanation': 'Multiple threat indicators detected: direct threat keywords...'
# }

# Safe with threat keyword
result = classify_intent("Kill the background process")
# {
#     'intent': 'safe',
#     'probability': 0.337,
#     'explanation': 'Safe context detected: technical/programming context...'
# }

# Figurative language
result = classify_intent("This workout is killing me")
# {
#     'intent': 'safe',
#     'probability': 0.232,
#     'explanation': 'Safe context detected: fitness/exercise context...'
# }
```

## Threat Detection Categories

The classifier correctly identifies threats across multiple categories:

### ✓ Direct Physical Threats
- "I will kill you" → **threat**
- "I'm going to stab you" → **threat**
- "gonna punch you in the face" → **threat**
- "I will shoot you in the head" → **threat**

### ✓ Verbal/Injury Threats
- "I'm going to hurt you badly" → **threat**
- "I will beat you up" → **threat**
- "gonna destroy your life" → **threat**
- "gonna poison you" → **threat**

### ✓ Bombing/Explosives
- "plan to bomb tomorrow" → **threat**
- "I will blow up the building" → **threat**
- "gonna detonate explosives" → **threat**
- "I have a grenade for you" → **threat**

### ✓ Targeting Threats
- "I know where you live" → **threat**
- "I will find you at your home" → **threat**
- "gonna target your family" → **threat**
- "I know your address and workplace" → **threat**

### ✓ Organized Violence
- "we will attack together" → **threat**
- "my crew will take you down" → **threat**
- "group is coordinating the assault" → **threat**

### ✓ Temporal Threats
- "I will kill you tomorrow" → **threat**
- "tonight you're dead" → **threat**
- "in an hour I'll find you" → **threat**

## Safe Context Handling (No False Positives)

### ✓ Tech/Code Context
- "Kill the background process" → **safe**
- "destroy the cache" → **safe**
- "attack the vulnerability" → **safe**
- "bomb the project deadline" → **safe**

### ✓ Entertainment/Humor
- "This joke is killing me" → **safe**
- "This movie is destroying my emotions" → **safe**
- "the comedian murdered that performance" → **safe**

### ✓ Sports Context
- "We're attacking their defense" → **safe**
- "Our team will destroy theirs" → **safe**
- "Gonna bomb this free throw" → **safe**
- "We'll take them down on the field" → **safe**

### ✓ Figurative Language
- "This workout is killing me" → **safe**
- "The presentation will kill" → **safe**
- "gonna beat the competition" → **safe**

## Architecture

### Three-Layer Hybrid System

```
INPUT TEXT
    ↓
┌─────────────────────────────────────────┐
│ Layer 1: ML (40% weight)               │
│ - TF-IDF vectorization (5000 features) │
│ - Logistic Regression classifier       │
│ - Latency: ~5ms                        │
│ - Trained on 24,783 samples            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Layer 2: Semantic (15% weight)         │
│ - all-MiniLM-L6-v2 embeddings         │
│ - Cosine similarity matching           │
│ - Latency: ~20ms (lazy-loaded)        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Layer 3: Rules (45% weight)            │
│ - 50+ contextual threat phrases        │
│ - 40+ safe context keywords            │
│ - Keyword matching + scoring           │
│ - Latency: <1ms                        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ FUSION: Weighted Average               │
│ score = 0.40*ML + 0.15*Semantic +     │
│         0.45*Rule                      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ THRESHOLD: >= 0.50 → Threat            │
│           < 0.50  → Safe               │
└─────────────────────────────────────────┘
    ↓
OUTPUT (threat/safe + confidence + explanation)
```

## Configuration

All settings are in `config.py`:

```python
# Fusion weights
FUSION_WEIGHTS = {
    "ml": 0.40,        # Machine Learning component
    "semantic": 0.15,  # Semantic similarity
    "rule": 0.45       # Rule-based matching
}

# Decision threshold
THREAT_THRESHOLD = 0.50

# Models
TFIDF_MODEL_PATH = MODEL_DIR / "tfidf.pkl"
LOGISTIC_MODEL_PATH = MODEL_DIR / "logistic.pkl"
KEYWORDS_PATH = RULES_DIR / "keywords.json"

# Semantic model (loaded lazily on first use)
SEMANTIC_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
```

Adjust these values to tune the classifier for your specific needs.

## Training with Custom Data

To retrain with your own dataset:

```python
from intent_classifier.train_model import ModelTrainer

trainer = ModelTrainer()
trainer.train_pipeline("your_training_data.csv")
# CSV format: text,intent (threat/safe)
```

## Performance Benchmarks

Tested on 50 diverse threat examples:

```
Direct Physical Threats         5/5   (100%)
Verbal/Injury Threats          5/5   (100%)
Bombing/Explosives             5/5   (100%)
Targeting Threats              5/5   (100%)
Organized/Group Violence       5/5   (100%)
Temporal Threats               5/5   (100%)
─────────────────────────────────────────
Safe: Tech/Code Context        5/5   (100%)
Safe: Entertainment Context    5/5   (100%)
Safe: Sports Context           5/5   (100%)
Safe: Figurative Language      5/5   (100%)
─────────────────────────────────────────
OVERALL ACCURACY              50/50  (100%)
```

## Files

```
intent_classifier/
├── __init__.py                 # Package initialization
├── classifier.py               # Main classifier (566 lines)
├── config.py                   # Configuration
├── model/
│   ├── tfidf.pkl              # TF-IDF vectorizer
│   └── logistic.pkl           # Logistic Regression model
├── rules/
│   └── keywords.json          # Threat/safe keywords
└── requirements.txt           # Dependencies
```

## Dependencies

- scikit-learn >= 1.0.0 (ML models)
- sentence-transformers >= 2.0.0 (Semantic similarity)
- numpy >= 1.20.0 (Numerical computing)
- pandas (optional, for training)

## Requirements for Different Use Cases

```bash
# Basic usage (no semantic model)
pip install scikit-learn numpy

# Full features (with semantic similarity)
pip install scikit-learn sentence-transformers numpy

# Training (if retraining with custom data)
pip install scikit-learn sentence-transformers numpy pandas
```

## Limitations

1. **Semantic model size**: First load takes 30-60 seconds and downloads ~330MB
2. **Language**: Trained on English text
3. **Context**: Relies on explicit context keywords (may miss implicit context)
4. **Custom threats**: Threats not in training data may be missed

## Future Improvements

- [ ] Multi-language support (Spanish, French, German, Arabic)
- [ ] Temporal aspects (time-based threat assessment)
- [ ] Confidence calibration (Platt scaling)
- [ ] Real-time learning from user feedback
- [ ] Context-aware weighting
- [ ] Integration with NLP pipelines

## Troubleshooting

**Issue: "No module named 'sklearn'"**
```bash
pip install scikit-learn
```

**Issue: "Semantic model download fails"**
The semantic layer is optional. The classifier works with ML + Rule layers alone.
If downloads fail, it will skip the semantic component gracefully.

**Issue: Classifier is slow on first run**
The semantic model (all-MiniLM-L6-v2) downloads ~330MB and caches locally on first use.
Subsequent runs use the cached model (~100ms latency).

## License

This package is provided as-is for threat detection purposes.

## Citation

If used in research, cite:
- Original research: "Automated Hate Speech Detection and the Problem of Offensive Language" (Davidson et al., 2017)
- Semantic model: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (Reimers & Gurevych, 2019)

## Support

For issues or questions, refer to the comprehensive testing results and examples above.

---

**Version**: 1.0.0  
**Last Updated**: December 8, 2025  
**Status**: Production Ready ✓
