"""
Online Learning Intent Classifier

Stacks on top of the existing static intent classifier with:
- Frozen transformer embeddings (from existing model)
- Feature extraction (URL count, uppercase, punctuation, entropy, keyword score)
- Lightweight online learning model (Logistic Regression with partial_fit)
- Sub-50ms inference latency
"""

import json
import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

from app.services.intent_classifier import get_classifier as get_static_classifier


class OnlineLearningClassifier:
    """
    Online learning classifier that combines:
    1. Frozen embeddings from static intent classifier
    2. Extracted features (URL, uppercase, punctuation, entropy, keywords)
    3. Lightweight SGDClassifier with partial_fit
    """
    
    def __init__(self, model_dir: Optional[Path] = None):
        """Initialize the online learning classifier."""
        self.model_dir = model_dir or Path(__file__).parent.parent.parent / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Static classifier for frozen embeddings
        self.static_classifier = get_static_classifier()
        
        # Online learning components
        self.model = None
        self.scaler = None
        self.feature_dim = None
        self.model_version = None
        self.classes = np.array(['safe', 'threat', 'phishing', 'scam', 'spam', 'propaganda'])
        
        # Performance tracking
        self.training_samples = 0
        self.last_trained = None
        
        # Load existing model if available
        self._load_model()
    
    def extract_features(self, text: str) -> Dict:
        """
        Extract features from text.
        
        Features:
        - Frozen embeddings from static classifier (semantic + rule scores)
        - URL count and characteristics
        - Uppercase ratio
        - Punctuation ratio
        - Character entropy
        - Keyword scores
        
        Returns:
            Dictionary with features and metadata
        """
        import re
        import math
        from collections import Counter
        
        start_time = time.time()
        
        # Get frozen embeddings from static classifier
        static_result = self.static_classifier.classify_intent(text)
        
        # Core embeddings from static model (3 confidence scores)
        embeddings = np.array([
            static_result.ml_confidence,
            static_result.semantic_confidence,
            static_result.rule_confidence
        ])
        
        # Extract text features
        text_lower = text.lower()
        text_len = len(text)
        words = text.split()
        word_count = len(words)
        
        # URL features
        url_pattern = r'https?://[^\s<>"{}\\|^`\[\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        url_count = len(urls)
        has_url = float(url_count > 0)
        has_shortener = float(any(s in text_lower for s in ['bit.ly', 'tinyurl', 'goo.gl', 't.co']))
        
        # Case features
        uppercase_count = sum(1 for c in text if c.isupper())
        uppercase_ratio = uppercase_count / text_len if text_len > 0 else 0.0
        
        # Punctuation features
        punctuation_count = sum(1 for c in text if c in '!?.,;:')
        punctuation_ratio = punctuation_count / text_len if text_len > 0 else 0.0
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        # Entropy (character-level)
        if text_len > 0:
            char_counts = Counter(text)
            entropy = -sum((c/text_len) * math.log2(c/text_len) for c in char_counts.values())
        else:
            entropy = 0.0
        
        # Keyword scores (from existing keyword families)
        urgency_keywords = ['urgent', 'immediately', 'now', 'asap', 'quickly', 'deadline']
        financial_keywords = ['bank', 'account', 'payment', 'money', 'transfer', 'credit']
        credential_keywords = ['password', 'login', 'verify', 'confirm', 'credentials']
        
        urgency_score = sum(1 for kw in urgency_keywords if kw in text_lower) / len(urgency_keywords)
        financial_score = sum(1 for kw in financial_keywords if kw in text_lower) / len(financial_keywords)
        credential_score = sum(1 for kw in credential_keywords if kw in text_lower) / len(credential_keywords)
        
        # Word-level features
        avg_word_len = sum(len(w) for w in words) / word_count if word_count > 0 else 0.0
        
        # Sentence features
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        avg_sentence_len = word_count / sentence_count if sentence_count > 0 else 0.0
        
        # Combine all features
        extracted_features = np.array([
            # URL features (4)
            url_count,
            has_url,
            has_shortener,
            url_count / word_count if word_count > 0 else 0.0,
            
            # Case features (1)
            uppercase_ratio,
            
            # Punctuation features (3)
            punctuation_ratio,
            exclamation_count / text_len if text_len > 0 else 0.0,
            question_count / text_len if text_len > 0 else 0.0,
            
            # Entropy (1)
            entropy / 5.0,  # Normalize to ~[0, 1]
            
            # Keyword scores (3)
            urgency_score,
            financial_score,
            credential_score,
            
            # Word features (2)
            avg_word_len / 10.0,  # Normalize
            avg_sentence_len / 25.0,  # Normalize
            
            # Length features (2)
            min(text_len / 500.0, 1.0),  # Normalized text length
            min(word_count / 100.0, 1.0),  # Normalized word count
        ])
        
        # Concatenate embeddings + extracted features
        feature_vector = np.concatenate([embeddings, extracted_features])
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            'features': feature_vector,
            'static_intent': static_result.intent,
            'static_probability': static_result.probability,
            'feature_dim': len(feature_vector),
            'extraction_latency_ms': latency_ms
        }
    
    def predict(self, text: str) -> Dict:
        """
        Predict using online learning model stacked on static classifier.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        # Extract features
        feature_data = self.extract_features(text)
        features = feature_data['features'].reshape(1, -1)
        
        # Initialize model if not exists
        if self.model is None:
            self._initialize_model(feature_data['feature_dim'])
        
        # Scale features
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        # Predict with online model
        try:
            if self.model is None:
                raise ValueError("Model not initialized")
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(max(probabilities))
            
            # Get class probabilities
            class_probs = {cls: float(prob) for cls, prob in zip(self.classes, probabilities)}
            
        except Exception as e:
            # Fallback to static classifier
            print(f"[WARNING] Online model prediction failed: {e}")
            prediction = feature_data['static_intent']
            confidence = feature_data['static_probability']
            class_probs = {prediction: confidence}
        
        total_latency = (time.time() - start_time) * 1000
        
        return {
            'intent': prediction,
            'confidence': confidence,
            'class_probabilities': class_probs,
            'model_version': self.model_version,
            'static_intent': feature_data['static_intent'],
            'static_probability': feature_data['static_probability'],
            'feature_extraction_ms': feature_data['extraction_latency_ms'],
            'total_latency_ms': total_latency,
            'feature_vector': feature_data['features'].tolist(),
            'model_status': 'online' if self.model is not None else 'static_only'
        }
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Incrementally train the model with new samples.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (n_samples,)
            
        Returns:
            Training statistics
        """
        start_time = time.time()
        
        # Initialize model if needed
        if self.model is None:
            self._initialize_model(X.shape[1])
        
        # Initialize scaler if needed
        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            # Partial fit scaler
            self.scaler.partial_fit(X)
            X_scaled = self.scaler.transform(X)
        
        # Train model
        if self.model is None:
            self._initialize_model(X.shape[1])
        
        assert self.model is not None, "Model should be initialized"
        self.model.partial_fit(X_scaled, y, classes=self.classes)
        
        # Update stats
        self.training_samples += len(X)
        self.last_trained = datetime.now()
        self.model_version = f"v{self.training_samples}_{self.last_trained.strftime('%Y%m%d%H%M')}"
        
        training_time = (time.time() - start_time) * 1000
        
        return {
            'samples_trained': len(X),
            'total_samples': self.training_samples,
            'model_version': self.model_version,
            'training_time_ms': training_time
        }
    
    def save_model(self, filename: Optional[str] = None) -> str:
        """Save the model and scaler to disk."""
        if filename is None:
            filename = f"online_model_{self.model_version}.pkl"
        
        filepath = self.model_dir / filename
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_dim': self.feature_dim,
            'model_version': self.model_version,
            'training_samples': self.training_samples,
            'last_trained': self.last_trained,
            'classes': self.classes
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[OK] Model saved: {filepath}")
        return str(filepath)
    
    def _load_model(self):
        """Load the most recent model from disk."""
        # Find most recent model file
        model_files = list(self.model_dir.glob("online_model_*.pkl"))
        
        if not model_files:
            print("[INFO] No existing online model found, will initialize on first training")
            return
        
        # Get most recent
        latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_model, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_dim = model_data['feature_dim']
            self.model_version = model_data['model_version']
            self.training_samples = model_data['training_samples']
            self.last_trained = model_data.get('last_trained')
            self.classes = model_data.get('classes', self.classes)
            
            print(f"[OK] Loaded online model: {latest_model.name}")
            print(f"     Version: {self.model_version}, Samples: {self.training_samples}")
            
        except Exception as e:
            print(f"[WARNING] Failed to load model {latest_model}: {e}")
    
    def _initialize_model(self, feature_dim: int):
        """Initialize a new SGD classifier."""
        self.feature_dim = feature_dim
        
        # SGDClassifier with log loss = Logistic Regression with partial_fit
        self.model = SGDClassifier(
            loss='log_loss',  # Logistic regression
            penalty='l2',
            alpha=0.0001,
            max_iter=1000,
            tol=1e-3,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        self.scaler = StandardScaler()
        self.model_version = f"v0_init_{datetime.now().strftime('%Y%m%d%H%M')}"
        
        print(f"[OK] Initialized online learning model (feature_dim={feature_dim})")


# Global instance
_online_classifier = None


def get_online_classifier() -> OnlineLearningClassifier:
    """Get or create global online classifier instance."""
    global _online_classifier
    if _online_classifier is None:
        _online_classifier = OnlineLearningClassifier()
    return _online_classifier
