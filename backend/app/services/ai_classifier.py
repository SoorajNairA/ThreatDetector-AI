from transformers import AutoTokenizer
import numpy as np
import os
from pathlib import Path

# PyTorch only imported if ONNX fallback needed
try:
    from transformers import AutoModelForSequenceClassification
    import torch
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    torch = None

# ============================================================================
# MODEL INITIALIZATION (runs once when module is imported)
# ============================================================================

# Check for ONNX model first (faster), fallback to PyTorch
MODEL_DIR = Path(__file__).parent.parent / "models"
ONNX_MODEL_PATH = MODEL_DIR / "ai_detector.onnx"
QUANT_ONNX_PATH = MODEL_DIR / "ai_detector.quant.onnx"

# Try to use ONNX model if available
use_onnx = False
onnx_session = None

if os.environ.get("AI_DETECTOR_USE_ONNX", "true").lower() == "true":
    try:
        import onnxruntime as ort
        
        # Prefer quantized model for better performance
        model_path = QUANT_ONNX_PATH if QUANT_ONNX_PATH.exists() else ONNX_MODEL_PATH
        
        if model_path.exists():
            onnx_session = ort.InferenceSession(
                str(model_path),
                providers=["CPUExecutionProvider"]
            )
            use_onnx = True
            print(f"[OK] ONNX AI detector loaded: {model_path.name}")
            print(f"[OK] Model size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"[INFO] ONNX not available: {e}")

# Fallback to PyTorch RoBERTa model
tokenizer = None
model = None
device = None

if not use_onnx:
    if not PYTORCH_AVAILABLE:
        print("[WARNING] PyTorch not available and ONNX not found. Using heuristic fallback.")
    else:
        # Using RoBERTa-based AI detection model
        # Options: "roberta-base-openai-detector" (OpenAI's detector)
        #          "Hello-SimpleAI/chatgpt-detector-roberta" (ChatGPT detector)
        #          "andreas122001/roberta-base-ai-detector" (Generic AI detector)
        MODEL_NAME = os.environ.get("AI_DETECTOR_MODEL", "Hello-SimpleAI/chatgpt-detector-roberta")
        
        # Device configuration
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            model.to(device)
            model.eval()  # Set to evaluation mode
            print(f"[OK] RoBERTa AI detector loaded: {MODEL_NAME}")
            print(f"[OK] Using device: {device}")
        except Exception as e:
            print(f"[WARNING] RoBERTa model load failed: {e}")
            print("  Falling back to heuristic implementation.")
            tokenizer = None
            model = None
else:
    # Load tokenizer for ONNX model
    try:
        # Use the tokenizer from the model that was converted
        TOKENIZER_NAME = os.environ.get("AI_DETECTOR_TOKENIZER", "Hello-SimpleAI/chatgpt-detector-roberta")
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    except Exception as e:
        print(f"[WARNING] Tokenizer load failed: {e}")
        tokenizer = None

# ============================================================================
# MAIN PREDICTION FUNCTION
# ============================================================================

def predict(text: str) -> dict:
    """
    Predict whether text is AI-generated using RoBERTa transformer model.
    
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
    try:
        DEFAULT_THRESHOLD = float(os.environ.get("AI_DETECT_THRESHOLD", "0.5"))
    except Exception:
        DEFAULT_THRESHOLD = 0.5

    # ========================================================================
    # INFERENCE PATH 1: ONNX Model (Fastest)
    # ========================================================================
    if use_onnx and onnx_session is not None and tokenizer is not None:
        try:
            # 1. Tokenize with padding and truncation
            inputs = tokenizer(
                text,
                return_tensors="np",
                truncation=True,
                max_length=512,
                padding="max_length"
            )
            
            # 2. Prepare ONNX inputs
            onnx_inputs = {k: v for k, v in inputs.items()}
            
            # 3. Run ONNX inference
            outputs = onnx_session.run(None, onnx_inputs)
            logits = outputs[0][0]  # Get logits for single input
            
            # 4. Compute probabilities
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / np.sum(exp_logits)
            
            # Model output format: [human_prob, ai_prob] or [ai_prob, human_prob]
            # Most AI detectors use [human, ai] format
            if probs[1] > probs[0]:
                human_prob = float(probs[0])
                ai_prob = float(probs[1])
            else:
                ai_prob = float(probs[0])
                human_prob = float(probs[1])
            
            # Make decision
            decision = ai_prob >= DEFAULT_THRESHOLD

            return {
                "ai_generated": bool(decision),
                "ai_confidence": ai_prob,
                "human_confidence": human_prob,
                "inference_status": "onnx"
            }
        
        except Exception as e:
            print(f"[WARNING] ONNX inference failed: {e}")
            print("  Falling back to PyTorch or heuristic.")
    
    # ========================================================================
    # INFERENCE PATH 2: PyTorch RoBERTa Model
    # ========================================================================
    if model is not None and tokenizer is not None:
        try:
            # 1. Tokenize with padding and truncation
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding="max_length"
            )
            
            # Move inputs to device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # 2. Run inference with no gradient computation
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits[0]  # Get logits for single input
            
            # 3. Compute probabilities
            probs = torch.nn.functional.softmax(logits, dim=-1)
            probs_np = probs.cpu().numpy()
            
            # Model output format depends on the specific model
            # Most AI detectors: [human_prob, ai_prob]
            # Some may be: [ai_prob, human_prob]
            # Check model config or use heuristic
            if probs_np[1] > probs_np[0]:
                # Assume index 1 is AI
                human_prob = float(probs_np[0])
                ai_prob = float(probs_np[1])
            else:
                # Swap if needed
                ai_prob = float(probs_np[0])
                human_prob = float(probs_np[1])
            
            # Make decision
            decision = ai_prob >= DEFAULT_THRESHOLD

            return {
                "ai_generated": bool(decision),
                "ai_confidence": ai_prob,
                "human_confidence": human_prob,
                "inference_status": "pytorch"
            }
        
        except Exception as e:
            print(f"[WARNING] PyTorch inference failed: {e}")
            print("  Falling back to heuristic implementation.")
    
    # ========================================================================
    # INFERENCE PATH 3: Enhanced Heuristic Fallback
    # ========================================================================
    # Comprehensive heuristic based on multiple text features
    
    import re
    from collections import Counter
    
    ai_score = 0.0
    human_score = 0.0
    
    # 1. Check for common AI phrases (strong signal)
    ai_phrases = [
        r'it is important to note', r'it is worth noting', r'in conclusion',
        r'in summary', r'furthermore', r'moreover', r'nevertheless',
        r'therefore', r'thus', r'hence', r'aforementioned',
        r'various factors', r'numerous', r'utilize', r'facilitate',
        r'demonstrate', r'illustrate', r'emphasize', r'it should be noted',
        r'one must consider', r'this approach', r'these findings',
        r'the data suggests', r'comprehensive', r'particular'
    ]
    
    text_lower = text.lower()
    ai_phrase_count = sum(1 for phrase in ai_phrases if re.search(phrase, text_lower))
    if ai_phrase_count >= 2:
        ai_score += 0.4
    elif ai_phrase_count == 1:
        ai_score += 0.2
    
    # 2. Check for human expressions (strong signal)
    human_expressions = [
        r'\blol\b', r'\bomg\b', r'\bwtf\b', r'\blmao\b',
        r'\byeah\b', r'\bnah\b', r'\bkinda\b', r'\bgonna\b',
        r'\bwanna\b', r'\bsorta\b', r'\bdude\b', r'\bguys\b',
        r'\bi mean\b', r'\bbasically\b', r'\bobviously\b',
        r'\btotally\b', r'\blike\b.*\blike\b'
    ]
    
    human_expr_count = sum(1 for expr in human_expressions if re.search(expr, text_lower))
    if human_expr_count >= 2:
        human_score += 0.5
    elif human_expr_count == 1:
        human_score += 0.25
    
    # 3. Sentence length variance (AI = uniform, Human = varied)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        sent_lengths = [len(s.split()) for s in sentences]
        avg_len = sum(sent_lengths) / len(sent_lengths)
        variance = sum((x - avg_len) ** 2 for x in sent_lengths) / len(sent_lengths)
        
        if variance > 50:  # High variance = human
            human_score += 0.2
        elif variance < 10:  # Low variance = AI
            ai_score += 0.2
    
    # 4. Personal pronouns (more common in human text)
    words = text_lower.split()
    personal_pronouns = ['i', 'me', 'my', 'mine', 'we', 'us', 'our']
    pronoun_count = sum(1 for word in words if word in personal_pronouns)
    if len(words) > 0:
        pronoun_ratio = pronoun_count / len(words)
        if pronoun_ratio > 0.05:
            human_score += 0.15
    
    # 5. Vocabulary diversity (AI = very diverse, Human = moderate)
    if len(words) >= 20:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio > 0.75:  # Very diverse = AI
            ai_score += 0.2
        elif unique_ratio < 0.5:  # Repetitive = human
            human_score += 0.15
    
    # 6. Formal transitional phrases
    if re.search(r'\b(firstly|secondly|thirdly|finally|lastly)\b', text_lower):
        ai_score += 0.15
    
    # 7. Questions and exclamations
    question_count = text.count('?')
    exclamation_count = text.count('!')
    if question_count + exclamation_count >= 2:
        human_score += 0.15
    
    # 8. Typos and informal patterns (human indicator)
    typo_patterns = [r'\b(teh|hte|adn|taht|waht)\b', r'\s{2,}']
    has_typos = any(re.search(pattern, text) for pattern in typo_patterns)
    if has_typos:
        human_score += 0.2
    
    # Make final decision
    total_score = ai_score + human_score
    if total_score == 0:
        # No strong signals, default to human with low confidence
        ai_confidence = 0.35
        human_confidence = 0.65
        label = "human"
    else:
        # Normalize scores to probabilities
        ai_confidence = ai_score / total_score
        human_confidence = human_score / total_score
        label = "ai" if ai_confidence > human_confidence else "human"
    
    # Keep raw probabilities without additional normalization
    return {
        "label": label,
        "confidence": float(max(ai_confidence, human_confidence)),
        "ai_probability": float(ai_confidence),
        "human_probability": float(human_confidence),
        "ai_generated": label == "ai",
        "ai_confidence": float(ai_confidence),
        "human_confidence": float(human_confidence),
        "inference_status": "heuristic (enhanced)"
    }
