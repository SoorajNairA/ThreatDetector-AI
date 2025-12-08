import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np
import os
from pathlib import Path

# ============================================================================
# MODEL INITIALIZATION (runs once when module is imported)
# ============================================================================

MODEL_DIR = Path(__file__).parent.parent / "models"
# Prefer a quantized model if present
QUANT_MODEL_PATH = MODEL_DIR / "ai_vs_human.quant.onnx"
MODEL_PATH = QUANT_MODEL_PATH if QUANT_MODEL_PATH.exists() else MODEL_DIR / "ai_vs_human.onnx"
TOKENIZER_NAME = "distilroberta-base"  # or your fine-tuned model path

# Load tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    print(f"✓ Tokenizer loaded: {TOKENIZER_NAME}")
except Exception as e:
    print(f"⚠ Warning: Tokenizer load failed: {e}")
    tokenizer = None

# Load ONNX model
session = None
try:
    if MODEL_PATH.exists():
        session = ort.InferenceSession(
            str(MODEL_PATH),
            providers=["CPUExecutionProvider"]
        )
        print(f"✓ ONNX model loaded: {MODEL_PATH}")
    else:
        print(f"⚠ Warning: ONNX model not found at {MODEL_PATH}")
        print("  Using stub implementation for now.")
except Exception as e:
    print(f"⚠ Warning: ONNX model load failed: {e}")
    print("  Falling back to stub implementation.")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def softmax(logits):
    """Compute softmax probabilities from logits."""
    logits = np.asarray(logits, dtype=np.float32)
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


def tokenize_text(text, max_length=512):
    """
    Tokenize text using the RoBERTa tokenizer.
    
    Args:
        text: Input text string
        max_length: Maximum sequence length (default 512)
    
    Returns:
        Dictionary with 'input_ids' and 'attention_mask' as numpy arrays
    """
    if tokenizer is None:
        raise RuntimeError("Tokenizer not loaded. Check TOKENIZER_NAME.")
    
    # Tokenize (may return numpy arrays or framework tensors)
    encoded = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        max_length=max_length,
        padding="max_length"
    )

    def _to_numpy(x):
        # HuggingFace can return numpy arrays or backend tensors
        try:
            # For numpy arrays this is a no-op; for torch tensors use .numpy()
            if hasattr(x, "numpy"):
                return x.numpy()
        except Exception:
            pass
        return np.array(x)

    input_ids = _to_numpy(encoded["input_ids"]).astype(np.int64)
    attention_mask = _to_numpy(encoded["attention_mask"]).astype(np.int64)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }


# ============================================================================
# MAIN PREDICTION FUNCTION
# ============================================================================

def predict(text: str) -> dict:
    """
    Predict whether text is AI-generated using RoBERTa + ONNX.
    
    Args:
        text: Plain text string (decrypted if needed)
    
    Returns:
        Dictionary:
        {
            "ai_generated": bool,         # True if AI confidence >= threshold
            "ai_confidence": float,       # Probability of AI generation [0, 1]
            "human_confidence": float,    # Probability of human origin [0, 1]
            "inference_status": "success" or "fallback"
        }
    
    Raises:
        ValueError: If text is empty or tokenization fails
    """
    
    # Input validation
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string")
    
    text = text.strip()
    if len(text) == 0:
        raise ValueError("Input text cannot be empty")

    # Decision configuration
    # Read threshold from environment variable if provided, else default 0.5
    try:
        DEFAULT_THRESHOLD = float(os.environ.get("AI_DETECT_THRESHOLD", "0.5"))
    except Exception:
        DEFAULT_THRESHOLD = 0.5
    # Border region width around threshold where we apply ensemble logic
    BORDER = float(os.environ.get("AI_DETECT_BORDER", "0.05"))

    # ========================================================================
    # INFERENCE PATH 1: ONNX Model (Production)
    # ========================================================================
    if session is not None and tokenizer is not None:
        try:
            # 1. Tokenize
            inputs = tokenize_text(text)
            
            # 2. Run ONNX inference
            outputs = session.run(None, inputs)

            # ONNX outputs may vary in type (list, numpy array, sparse),
            # so coerce to a numpy array safely.
            logits_raw = outputs[0]
            logits_arr = np.asarray(logits_raw)

            # Normalize shape: accept (1,2) or (2,) and handle gracefully
            if logits_arr.ndim == 2 and logits_arr.shape[0] >= 1:
                logits_vec = logits_arr[0]
            elif logits_arr.ndim == 1:
                logits_vec = logits_arr
            else:
                # Fallback: flatten and take first two elements
                logits_vec = logits_arr.flatten()[:2]

            # 3. Compute probabilities
            probs = softmax(logits_vec)
            human_prob = float(probs[0])
            ai_prob = float(probs[1])

            # 4. Automatic decision with ensemble for borderline cases
            # If confidence is clearly above/below threshold, respect it.
            if ai_prob >= DEFAULT_THRESHOLD + BORDER:
                decision = True
            elif ai_prob <= DEFAULT_THRESHOLD - BORDER:
                decision = False
            else:
                # Borderline: consult lightweight ensemble of other classifiers
                # to make an automatic decision without user intervention.
                ensemble_score = ai_prob * 0.6

                # Import other local classifiers (best-effort)
                style_score = 0.5
                keyword_score = 0.0
                url_score = 0.0
                try:
                    try:
                        # Prefer package-relative import
                        from .stylometry_classifier import predict as style_pred
                        from .keyword_classifier import predict as kw_pred
                        from .url_classifier import predict as url_pred
                    except Exception:
                        # Fallback absolute imports
                        from stylometry_classifier import predict as style_pred
                        from keyword_classifier import predict as kw_pred
                        from url_classifier import predict as url_pred

                    s = style_pred(text).get("style_score", 0.5)
                    # stylometry: higher score means more human-like, so invert for AI-likelihood
                    style_score = 1.0 - float(s)

                    keyword_score = float(kw_pred(text).get("keyword_score", 0.0))
                    url_score = float(url_pred(text).get("url_score", 0.0))
                except Exception:
                    # If any auxiliary classifier fails, ignore and rely on ai_prob
                    pass

                # Weighted ensemble (tunable)
                ensemble_score += style_score * 0.2
                ensemble_score += keyword_score * 0.1
                ensemble_score += url_score * 0.1

                decision = ensemble_score >= DEFAULT_THRESHOLD

            return {
                "ai_generated": bool(decision),
                "ai_confidence": ai_prob,
                "human_confidence": human_prob,
                "inference_status": "success"
            }
        
        except Exception as e:
            print(f"⚠ ONNX inference failed: {e}")
            print("  Falling back to stub implementation.")
    
    # ========================================================================
    # INFERENCE PATH 2: Stub Implementation (Fallback)
    # ========================================================================
    # Simple heuristic based on text features (for development/testing)
    words = text.lower().split()
    word_count = len(words)
    unique_words = len(set(words))
    diversity = unique_words / (word_count + 1)
    
    # Heuristic: higher diversity & longer text → more human-like
    ai_confidence = max(0.0, min(1.0, 0.5 - (diversity * 0.3) - (word_count / 100) * 0.2))
    
    return {
        "ai_generated": ai_confidence >= 0.5,
        "ai_confidence": ai_confidence,
        "human_confidence": 1.0 - ai_confidence,
        "inference_status": "fallback (stub)"
    }
