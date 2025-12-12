"""
Configuration for the Intent Classifier hybrid system.
Defines paths, weights, thresholds, and model parameters.
"""

from pathlib import Path

# ============================================================================
# Paths
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
MODEL_DIR = PROJECT_ROOT / "model"
RULES_DIR = PROJECT_ROOT / "rules"
TESTS_DIR = PROJECT_ROOT / "tests"

# Model artifacts
TFIDF_MODEL_PATH = MODEL_DIR / "tfidf.pkl"
LOGISTIC_MODEL_PATH = MODEL_DIR / "logistic.pkl"
KEYWORDS_PATH = RULES_DIR / "keywords.json"

# ============================================================================
# Fusion Weights (sum to 1.0)
# ============================================================================
FUSION_WEIGHTS = {
    "ml": 0.40,           # TF-IDF + Logistic Regression (reduced)
    "semantic": 0.15,     # MiniLM cosine similarity (reduced)
    "rule": 0.45          # Keyword/regex matching (increased - strong signal for threats)
}

# ============================================================================
# Decision Threshold
# ============================================================================
THREAT_THRESHOLD = 0.50  # Lowered for better threat detection sensitivity

# ============================================================================
# Semantic Similarity Configuration
# ============================================================================
SEMANTIC_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Threat reference sentences for semantic similarity
THREAT_REFERENCE_SENTENCES = [
    "we will attack",
    "I will hurt him",
    "plan the bombing",
    "take them down",
    "I will kill you",
    "eliminate the target",
    "destroy everything",
    "burn it down",
    "we're going to shoot",
    "prepare for violence"
]

# ============================================================================
# ML Model Configuration
# ============================================================================
TFIDF_CONFIG = {
    "max_features": 5000,
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.95,
    "lowercase": True,
    "strip_accents": "unicode",
    "stop_words": "english"
}

LOGISTIC_REGRESSION_CONFIG = {
    "C": 1.0,
    "max_iter": 300,
    "solver": "liblinear",
    "random_state": 42,
    "class_weight": "balanced"
}

# ============================================================================
# Training Configuration
# ============================================================================
TRAINING_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "stratify": True,
    "min_samples": 100  # Minimum samples per class
}

# ============================================================================
# Performance Targets
# ============================================================================
PERFORMANCE_TARGETS = {
    "accuracy": 0.85,           # Target >= 85%
    "max_latency_ms": 40,       # Total prediction time < 40ms
    "ml_latency_ms": 10,        # ML prediction < 10ms
    "semantic_latency_ms": 25,  # MiniLM embedding < 25ms
    "rule_latency_ms": 2,       # Rule matching < 2ms
    "max_ram_mb": 300           # RAM usage < 300MB
}

# ============================================================================
# Error Handling & Fallback
# ============================================================================
FALLBACK_CONFIG = {
    "use_fallback_on_ml_error": True,
    "fallback_layers": ["semantic", "rule"],  # Use only semantic + rule if ML fails
    "default_safe_on_error": True,  # Default to "safe" if all layers fail
}

# ============================================================================
# Rule Engine Configuration
# ============================================================================
RULE_CONFIG = {
    "normalize": True,          # Normalize text (lowercase, punctuation removal)
    "lemmatize": False,         # Use lemmatization (slower, but more accurate)
    "min_match_score": 0.0,     # Minimum score to classify as threat (0.0 = any match)
    "max_matches_to_score": 10  # Only count up to N matches (prevent spam)
}

# ============================================================================
# Logging & Debug
# ============================================================================
DEBUG = False
VERBOSE = True
LOG_PREDICTIONS = False

# ============================================================================
# Test Configuration
# ============================================================================
TEST_CONFIG = {
    "num_test_samples": 100,
    "test_timeout_ms": 50,
    "performance_threshold": 0.85
}
