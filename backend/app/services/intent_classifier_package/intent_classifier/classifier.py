"""
Hybrid Intent Classifier - Three-layer threat detection system.

Combines:
1. ML Layer: TF-IDF + Logistic Regression (60% weight)
2. Semantic Layer: MiniLM cosine similarity (25% weight)
3. Rule Layer: Keyword/regex matching (15% weight)

Total latency target: < 40ms
Accuracy target: >= 85%
"""

import json
import pickle
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .config import (
    FALLBACK_CONFIG,
    FUSION_WEIGHTS,
    KEYWORDS_PATH,
    LOGISTIC_MODEL_PATH,
    RULE_CONFIG,
    SEMANTIC_MODEL_NAME,
    THREAT_REFERENCE_SENTENCES,
    THREAT_THRESHOLD,
    TFIDF_MODEL_PATH,
    VERBOSE,
)


@dataclass
class ClassificationResult:
    """Output data class for classification results."""

    intent: str
    probability: float
    ml_confidence: float
    semantic_confidence: float
    rule_confidence: float
    explanation: str
    latency_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "intent": self.intent,
            "probability": round(self.probability, 4),
            "ml_confidence": round(self.ml_confidence, 4),
            "semantic_confidence": round(self.semantic_confidence, 4),
            "rule_confidence": round(self.rule_confidence, 4),
            "explanation": self.explanation,
            "latency_ms": round(self.latency_ms, 2),
        }


class IntentClassifier:
    """
    Hybrid intent classifier with three independent layers:
    - ML: Fast TF-IDF + Logistic Regression
    - Semantic: MiniLM embeddings with cosine similarity
    - Rule: Keyword and regex matching
    """

    def __init__(self):
        """Initialize all three layers."""
        self.ml_model = None
        self.ml_vectorizer = None
        self.semantic_model = None
        self.rules = None
        self.threat_embeddings = None
        self._semantic_loaded = False

        self._load_ml_layer()
        # Skip semantic layer for now - will load on demand
        # self._load_semantic_layer()
        self._load_rule_layer()

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def classify_intent(
        self, text: str, context: Optional[List[str]] = None
    ) -> ClassificationResult:
        """
        Classify text as 'threat' or 'safe' using hybrid three-layer system.

        Args:
            text: Input text to classify
            context: Optional context sentences for additional semantic info

        Returns:
            ClassificationResult with intent, probabilities, and explanation
        """
        start_time = time.time()

        # Input validation
        text = (text or "").strip()
        if not text:
            return self._safe_result("Empty input", start_time)

        try:
            # Get predictions from each layer
            ml_prob = self._ml_probability(text)
            semantic_prob = self._semantic_probability(text, context)
            rule_prob = self._rule_probability(text)

            # Fusion algorithm
            final_prob = (
                FUSION_WEIGHTS["ml"] * ml_prob
                + FUSION_WEIGHTS["semantic"] * semantic_prob
                + FUSION_WEIGHTS["rule"] * rule_prob
            )

            # Decision
            intent = "threat" if final_prob >= THREAT_THRESHOLD else "safe"

            # Explanation
            explanation = self._generate_explanation(
                ml_prob, semantic_prob, rule_prob, intent
            )

            elapsed = (time.time() - start_time) * 1000  # Convert to ms

            return ClassificationResult(
                intent=intent,
                probability=final_prob,
                ml_confidence=ml_prob,
                semantic_confidence=semantic_prob,
                rule_confidence=rule_prob,
                explanation=explanation,
                latency_ms=elapsed,
            )

        except Exception as e:
            if VERBOSE:
                print(f"Error in classification: {e}")
            # Fallback to rule + semantic if ML fails
            if FALLBACK_CONFIG["use_fallback_on_ml_error"]:
                return self._fallback_classification(text, start_time)
            else:
                return self._safe_result(f"Classification error: {e}", start_time)

    # ========================================================================
    # LAYER 1: ML PREDICTION (TF-IDF + Logistic Regression)
    # ========================================================================

    def _ml_probability(self, text: str) -> float:
        """
        Get threat probability from ML model.
        Output: 0-1, where 1.0 = high threat confidence
        Latency target: < 10ms
        """
        if self.ml_model is None or self.ml_vectorizer is None:
            if VERBOSE:
                print("Warning: ML model not loaded, using fallback")
            return 0.0

        try:
            # Vectorize
            X = self.ml_vectorizer.transform([text])

            # Predict probability
            proba = self.ml_model.predict_proba(X)  # [[safe_prob, threat_prob]]
            threat_prob = float(proba[0, 1])

            return threat_prob

        except Exception as e:
            if VERBOSE:
                print(f"ML prediction error: {e}")
            return 0.0

    # ========================================================================
    # LAYER 2: SEMANTIC SIMILARITY (MiniLM)
    # ========================================================================

    def _semantic_probability(
        self, text: str, context: Optional[List[str]] = None
    ) -> float:
        """
        Get threat probability from semantic similarity.
        Uses MiniLM embeddings and cosine similarity.
        Output: 0-1, where 1.0 = high semantic threat similarity
        Latency target: < 25ms
        """
        if self.semantic_model is None:
            # Lazy load on first use
            try:
                self._load_semantic_layer()
            except Exception as e:
                if VERBOSE:
                    print(f"Warning: Semantic model load failed: {e}")
                return 0.0

        if self.semantic_model is None:
            if VERBOSE:
                print("Warning: Semantic model not available")
            return 0.0

        try:
            # Embed input text
            input_embedding = self.semantic_model.encode(text, convert_to_tensor=False)

            # Compute cosine similarity with threat reference sentences
            similarities = []
            for threat_emb in self.threat_embeddings:
                similarity = self._cosine_similarity(input_embedding, threat_emb)
                similarities.append(similarity)

            # Max similarity as final score
            max_similarity = max(similarities) if similarities else 0.0

            # Clamp to [0, 1]
            semantic_prob = max(0.0, min(1.0, max_similarity))

            return semantic_prob

        except Exception as e:
            if VERBOSE:
                print(f"Semantic prediction error: {e}")
            return 0.0

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    # ========================================================================
    # LAYER 3: RULE-BASED ENGINE
    # ========================================================================

    def _rule_probability(self, text: str) -> float:
        """
        Get threat probability from rule-based matching.
        Counts keyword matches and converts to 0-1 probability.
        Latency target: < 2ms
        """
        if self.rules is None:
            if VERBOSE:
                print("Warning: Rules not loaded")
            return 0.0

        try:
            # Normalize text
            normalized = self._normalize_text(text)

            # Check for safe context (reduces threat score heavily)
            if self._has_safe_context(normalized):
                # Apply strong penalty when safe context is detected
                match_score = self._count_keyword_matches(normalized) * 0.1
                return min(1.0, match_score)

            # Count keyword matches with weighted scoring
            match_score = self._count_keyword_matches(normalized)

            # Better scoring: scale by 2.5 instead of 4.0 for higher sensitivity
            # This gives "kill" (1 point) + "will" (0.5 points) = 1.5 -> 0.60 probability
            rule_prob = min(1.0, match_score / 2.5)

            return rule_prob

        except Exception as e:
            if VERBOSE:
                print(f"Rule prediction error: {e}")
            return 0.0

    def _normalize_text(self, text: str) -> str:
        """Normalize text: lowercase, remove punctuation."""
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _count_keyword_matches(self, normalized_text: str) -> float:
        """Count keyword matches in normalized text with weighted scoring."""
        if self.rules is None:
            return 0.0

        match_score = 0.0
        max_matches = RULE_CONFIG.get("max_matches_to_score", 10)
        found_threat = False
        found_intent = False

        # Contextual phrases first (multi-word, high confidence)
        for phrase in self.rules.get("contextual_phrases", []):
            if phrase in normalized_text:
                match_score += 1.5  # Higher weight for multi-word phrases
                if match_score >= max_matches * 1.5:
                    return match_score

        # Direct threat keywords (high priority)
        for keyword in self.rules.get("direct_threats", []):
            if keyword in normalized_text:
                found_threat = True
                match_score += 1.0
                if match_score >= max_matches * 1.5:
                    return match_score

        # Intent indicators (will, going to, plan to, etc.)
        for indicator in self.rules.get("intent_indicators", []):
            if indicator in normalized_text:
                found_intent = True
                match_score += 0.5
                if match_score >= max_matches:
                    break

        # Weapon references
        for weapon in self.rules.get("weapon_references", []):
            if weapon in normalized_text:
                match_score += 0.5

        # Coordinated violence indicators
        for indicator in self.rules.get("coordinated_violence", []):
            if indicator in normalized_text:
                match_score += 0.3

        # Location/personal targeting (increases threat level)
        has_location = any(loc in normalized_text for loc in self.rules.get("location_targeting", []))
        has_personal = any(pers in normalized_text for pers in self.rules.get("personal_targeting", []))
        if has_location or has_personal:
            match_score += 0.3

        return match_score

    def _has_safe_context(self, normalized_text: str) -> bool:
        """Check if text has safe context keywords."""
        if self.rules is None:
            return False

        safe_keywords = self.rules.get("safe_context_keywords", [])
        for keyword in safe_keywords:
            if keyword in normalized_text:
                return True

        return False

    # ========================================================================
    # LOADING LAYERS
    # ========================================================================

    def _load_ml_layer(self) -> None:
        """Load pre-trained TF-IDF and Logistic Regression models."""
        try:
            if TFIDF_MODEL_PATH.exists():
                with open(TFIDF_MODEL_PATH, "rb") as f:
                    self.ml_vectorizer = pickle.load(f)

            if LOGISTIC_MODEL_PATH.exists():
                with open(LOGISTIC_MODEL_PATH, "rb") as f:
                    self.ml_model = pickle.load(f)

            if self.ml_model and self.ml_vectorizer:
                if VERBOSE:
                    print("ML layer loaded successfully")
            else:
                if VERBOSE:
                    print("Warning: ML models not found, will use fallback")

        except Exception as e:
            if VERBOSE:
                print(f"Error loading ML layer: {e}")

    def _load_semantic_layer(self) -> None:
        """Load MiniLM model and embed threat reference sentences (lazy-load on demand)."""
        if self._semantic_loaded:
            return
            
        try:
            from sentence_transformers import SentenceTransformer

            if self.semantic_model is None:
                self.semantic_model = SentenceTransformer(SEMANTIC_MODEL_NAME)

                # Pre-compute threat embeddings
                self.threat_embeddings = [
                    self.semantic_model.encode(
                        sent, convert_to_tensor=False, show_progress_bar=False
                    )
                    for sent in THREAT_REFERENCE_SENTENCES
                ]

            self._semantic_loaded = True
            if VERBOSE:
                print("Semantic layer loaded successfully")

        except Exception as e:
            if VERBOSE:
                print(f"Error loading semantic layer: {e}")
            self._semantic_loaded = False

    def _load_rule_layer(self) -> None:
        """Load keyword rules from JSON."""
        try:
            if KEYWORDS_PATH.exists():
                with open(KEYWORDS_PATH, "r") as f:
                    self.rules = json.load(f)

                if VERBOSE:
                    print("Rule layer loaded successfully")
            else:
                if VERBOSE:
                    print(f"Warning: Keywords file not found at {KEYWORDS_PATH}")

        except Exception as e:
            if VERBOSE:
                print(f"Error loading rule layer: {e}")

    # ========================================================================
    # EXPLANATION & FALLBACK
    # ========================================================================

    @staticmethod
    def _generate_explanation(
        ml_prob: float, semantic_prob: float, rule_prob: float, intent: str
    ) -> str:
        """Generate human-readable explanation of classification."""
        parts = []

        if ml_prob > 0.6:
            parts.append("ML model indicates threat")
        elif ml_prob > 0.3:
            parts.append("ML model shows mixed signal")
        else:
            parts.append("ML model indicates safe")

        if semantic_prob > 0.6:
            parts.append("semantic similarity is high")
        elif semantic_prob > 0.3:
            parts.append("some semantic similarity to threats")

        if rule_prob > 0.6:
            parts.append("keyword matching suggests threat")
        elif rule_prob > 0.3:
            parts.append("some threatening keywords detected")

        if not parts:
            return "No significant threat indicators found"

        return ". ".join(parts).capitalize() + "."

    def _fallback_classification(self, text: str, start_time: float) -> ClassificationResult:
        """Fallback classification using only semantic + rule if ML fails."""
        if VERBOSE:
            print("Using fallback classification (no ML)")

        try:
            semantic_prob = self._semantic_probability(text)
            rule_prob = self._rule_probability(text)

            # Redistribute weights without ML
            w_semantic = FUSION_WEIGHTS["semantic"] / (
                FUSION_WEIGHTS["semantic"] + FUSION_WEIGHTS["rule"]
            )
            w_rule = FUSION_WEIGHTS["rule"] / (
                FUSION_WEIGHTS["semantic"] + FUSION_WEIGHTS["rule"]
            )

            final_prob = w_semantic * semantic_prob + w_rule * rule_prob
            intent = "threat" if final_prob >= THREAT_THRESHOLD else "safe"

            elapsed = (time.time() - start_time) * 1000
            return ClassificationResult(
                intent=intent,
                probability=final_prob,
                ml_confidence=0.0,
                semantic_confidence=semantic_prob,
                rule_confidence=rule_prob,
                explanation="Fallback classification (ML unavailable). "
                + self._generate_explanation(0.0, semantic_prob, rule_prob, intent),
                latency_ms=elapsed,
            )

        except Exception as e:
            return self._safe_result(f"Fallback error: {e}", start_time)

    @staticmethod
    def _safe_result(reason: str, start_time: float) -> ClassificationResult:
        """Return safe classification (default fallback)."""
        elapsed = (time.time() - start_time) * 1000
        return ClassificationResult(
            intent="safe",
            probability=0.0,
            ml_confidence=0.0,
            semantic_confidence=0.0,
            rule_confidence=0.0,
            explanation=reason,
            latency_ms=elapsed,
        )


# ============================================================================
# PUBLIC API
# ============================================================================

# Global classifier instance
_classifier = None


def get_classifier() -> IntentClassifier:
    """Get or initialize the global classifier instance (singleton)."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def classify_intent(
    text: str, context: Optional[List[str]] = None
) -> Dict:
    """
    Classify text intent as threat or safe.

    Args:
        text: Input text to classify
        context: Optional context for semantic layer

    Returns:
        Dictionary with intent, probabilities, and explanation
    """
    classifier = get_classifier()
    result = classifier.classify_intent(text, context)
    return result.to_dict()


# For backward compatibility with module-level function
if __name__ == "__main__":
    # Example usage
    classifier = get_classifier()

    test_texts = [
        "I will kill you tonight",
        "Let's go to the movies",
        "We're going to attack their defense",
        "Kill the background process",
    ]

    print("=" * 80)
    print("HYBRID INTENT CLASSIFIER - DEMO")
    print("=" * 80)

    for text in test_texts:
        result = classifier.classify_intent(text)
        print(f"\nText: {text}")
        print(f"Intent: {result.intent}")
        print(f"Probability: {result.probability:.4f}")
        print(f"  ML: {result.ml_confidence:.4f}")
        print(f"  Semantic: {result.semantic_confidence:.4f}")
        print(f"  Rule: {result.rule_confidence:.4f}")
        print(f"Explanation: {result.explanation}")
        print(f"Latency: {result.latency_ms:.2f}ms")
