"""Threat analysis endpoint"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.ai_classifier import predict as ai_predict
from app.services.intent_classifier import predict as intent_predict
from app.services.stylometry_classifier import predict as style_predict
from app.services.url_classifier import predict as url_predict
from app.services.keyword_classifier import predict as keyword_predict
from app.services.supabase_client import insert_threat
from app.services.auth import get_current_user
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Ensemble weights for combining classifier scores
WEIGHTS = {
    "ai": 0.35,
    "intent": 0.35,
    "style": 0.10,
    "url": 0.12,
    "keyword": 0.08
}


@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyze"])
async def analyze_threat(
    request: AnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze text content for potential threats.
    
    This endpoint:
    1. Validates API key and identifies user
    2. Runs classifier analysis on the text
    3. Stores results in Supabase linked to user
    4. Returns comprehensive threat assessment
    
    Args:
        request: AnalyzeRequest containing text and optional metadata
        current_user: User info from API key (injected)
        
    Returns:
        AnalyzeResponse with risk assessment and detailed analysis
    """
    user_id = current_user.get("user_id")
    logger.info(f"Received analyze request from user: {user_id or 'global'}")
    
    # Initialize results and scores
    results = {}
    scores = {"ai": 0.0, "intent": 0.0, "style": 0.0, "url": 0.0, "keyword": 0.0}
    
    # ========================================================================
    # 1. AI Classifier
    # ========================================================================
    try:
        ai_result = ai_predict(request.text)
        results["ai_generated"] = ai_result.get("ai_generated", False)
        results["ai_confidence"] = ai_result.get("ai_confidence", 0.0)
        results["human_confidence"] = ai_result.get("human_confidence", 0.0)
        scores["ai"] = float(ai_result.get("ai_confidence", 0.0))
        logger.info(f"AI classifier: {scores['ai']:.3f}")
    except Exception as e:
        logger.error(f"AI classifier failed: {e}")
        results["ai_generated"] = False
        results["ai_confidence"] = 0.0
        results["human_confidence"] = 1.0
        scores["ai"] = 0.0
    
    # ========================================================================
    # 2. Intent Classifier
    # ========================================================================
    try:
        intent_result = intent_predict(request.text)
        results["intent"] = intent_result.get("intent", "unknown")
        results["intent_confidence"] = intent_result.get("intent_confidence", 0.0)
        
        # Map intent to threat score
        intent_threat_map = {
            "phishing": 0.9,
            "scam": 0.85,
            "propaganda": 0.7,
            "spam": 0.6,
            "unknown": 0.3
        }
        intent_score = intent_threat_map.get(results["intent"], 0.3)
        scores["intent"] = float(intent_score)
        logger.info(f"Intent classifier: {results['intent']} ({scores['intent']:.3f})")
    except Exception as e:
        logger.error(f"Intent classifier failed: {e}")
        results["intent"] = "unknown"
        results["intent_confidence"] = 0.0
        scores["intent"] = 0.0
    
    # ========================================================================
    # 3. Stylometry Classifier
    # ========================================================================
    try:
        style_result = style_predict(request.text)
        results["style_score"] = style_result.get("style_score", 0.0)
        # Stylometry returns human-likeness [0-1], invert to get risk score
        human_likeness = float(style_result.get("style_score", 0.0))
        scores["style"] = 1.0 - human_likeness  # Convert to AI-likeness/risk
        logger.info(f"Style classifier: {scores['style']:.3f} (human-likeness: {human_likeness:.3f})")
    except Exception as e:
        logger.error(f"Stylometry classifier failed: {e}")
        results["style_score"] = 0.0
        scores["style"] = 0.5  # Neutral risk if classifier fails
    
    # ========================================================================
    # 4. URL Classifier
    # ========================================================================
    try:
        url_result = url_predict(request.text)
        results["url_detected"] = url_result.get("url_detected", False)
        results["url_score"] = url_result.get("url_score", 0.0)
        results["domains"] = url_result.get("domains", [])
        scores["url"] = float(url_result.get("url_score", 0.0))
        logger.info(f"URL classifier: {scores['url']:.3f}")
    except Exception as e:
        logger.error(f"URL classifier failed: {e}")
        results["url_detected"] = False
        results["url_score"] = 0.0
        results["domains"] = []
        scores["url"] = 0.0
    
    # ========================================================================
    # 5. Keyword Classifier
    # ========================================================================
    try:
        keyword_result = keyword_predict(request.text)
        results["keywords"] = keyword_result.get("keywords", [])
        results["keyword_score"] = keyword_result.get("keyword_score", 0.0)
        scores["keyword"] = float(keyword_result.get("keyword_score", 0.0))
        logger.info(f"Keyword classifier: {scores['keyword']:.3f}")
    except Exception as e:
        logger.error(f"Keyword classifier failed: {e}")
        results["keywords"] = []
        results["keyword_score"] = 0.0
        scores["keyword"] = 0.0
    
    # ========================================================================
    # 6. Compute Weighted Ensemble Score
    # ========================================================================
    risk_score = (
        WEIGHTS["ai"] * scores["ai"] +
        WEIGHTS["intent"] * scores["intent"] +
        WEIGHTS["style"] * scores["style"] +
        WEIGHTS["url"] * scores["url"] +
        WEIGHTS["keyword"] * scores["keyword"]
    )
    
    # Boost risk score when multiple high-risk signals are present
    high_risk_indicators = 0
    if results["intent"] in ["phishing", "scam"]:
        high_risk_indicators += 1
    if scores["url"] >= 0.8:
        high_risk_indicators += 1
    if scores["keyword"] >= 0.8:
        high_risk_indicators += 1
    if scores["ai"] >= 0.8:
        high_risk_indicators += 1
    
    # Apply multiplicative boost for multiple indicators
    if high_risk_indicators >= 3:
        risk_score = min(1.0, risk_score * 1.15)  # 15% boost, cap at 100%
    elif high_risk_indicators >= 2:
        risk_score = min(1.0, risk_score * 1.08)  # 8% boost
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    logger.info(f"Final risk score: {risk_score:.3f} ({risk_level})")
    logger.info(f"Component scores: {scores}")
    
    analysis_result = {
        "risk_score": float(risk_score),
        "risk_level": risk_level,
        "analysis": results,
        "component_scores": scores
    }
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Build threat record for database
    threat_record = {
        "text": request.text,
        "risk_level": analysis_result["risk_level"],
        "risk_score": analysis_result["risk_score"],
        "intent": analysis_result["analysis"].get("intent", "unknown"),
        "ai_generated": analysis_result["analysis"].get("ai_generated", False),
        "actor": "unknown",  # Placeholder - can be extracted from metadata in future
        "user_id": user_id,  # Link to user
        "timestamp": timestamp,
        "ai_confidence": analysis_result["analysis"].get("ai_confidence", 0.0),
        "intent_confidence": analysis_result["analysis"].get("intent_confidence", 0.0),
        "style_score": analysis_result["analysis"].get("style_score", 0.0),
        "url_detected": analysis_result["analysis"].get("url_detected", False),
        "domains": analysis_result["analysis"].get("domains", []),
        "keywords": analysis_result["analysis"].get("keywords", [])
    }
    
    # Store in Supabase only if not in sandbox mode
    if not request.sandbox:
        try:
            insert_threat(threat_record)
            logger.info("Threat record stored successfully")
        except Exception as e:
            logger.error(f"Failed to store threat record: {e}")
            # Continue execution - don't fail the request if storage fails
    else:
        logger.info("Sandbox mode: skipping database storage")
    
    # Return analysis response
    return {
        "risk_level": analysis_result["risk_level"],
        "risk_score": analysis_result["risk_score"],
        "analysis": analysis_result["analysis"],
        "timestamp": timestamp
    }
