"""
Updated Threat Analysis Endpoint with Encryption
Replaces app/routes/analyze.py
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from datetime import datetime, timezone
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.ai_classifier import predict as ai_predict
from app.services.intent_classifier import predict as intent_predict
from app.services.stylometry_classifier import predict as style_predict
from app.services.url_classifier import predict as url_predict
from app.services.keyword_classifier import predict as keyword_predict
from app.services.account_service import get_account_service
from app.services.encryption import get_encryption_service
from app.services.supabase_client import supabase
from app.services.audit import log_audit_event
from app.middleware.auth import get_account_from_api_key
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Ensemble weights for combining classifier scores
WEIGHTS = {
    "ai": 0.4,
    "intent": 0.3,
    "style": 0.15,
    "url": 0.1,
    "keyword": 0.05
}


@router.post("/analyze", response_model=AnalyzeResponse, tags=["analyze"])
async def analyze_threat(
    analyze_request: AnalyzeRequest,
    request: Request,
    account_info: dict = Depends(get_account_from_api_key)
):
    """
    Analyze text content for potential threats with encryption
    
    This endpoint:
    1. Validates API key and identifies account
    2. Runs classifier analysis on the text
    3. Encrypts sensitive data with per-account key
    4. Stores encrypted results in database (unless sandbox mode)
    5. Returns comprehensive threat assessment
    
    Args:
        analyze_request: AnalyzeRequest containing text and optional metadata
        request: FastAPI request object
        account_info: Account info from API key validation
        
    Returns:
        AnalyzeResponse with risk assessment and detailed analysis
    """
    account_id = account_info["account_id"]
    logger.info(f"Received analyze request from account: {account_id}")
    
    # Log API usage
    await log_audit_event(
        account_id=account_id,
        event_type="analyze_called",
        metadata={"sandbox": analyze_request.sandbox},
        request=request
    )
    
    # Initialize results and scores
    results = {}
    scores = {"ai": 0.0, "intent": 0.0, "style": 0.0, "url": 0.0, "keyword": 0.0}
    
    # ========================================================================
    # 1. AI Classifier
    # ========================================================================
    try:
        ai_result = ai_predict(analyze_request.text)
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
        intent_result = intent_predict(analyze_request.text)
        results["intent"] = intent_result.get("intent", "unknown")
        results["intent_confidence"] = intent_result.get("confidence", 0.0)
        scores["intent"] = float(intent_result.get("confidence", 0.0))
        logger.info(f"Intent classifier: {scores['intent']:.3f}")
    except Exception as e:
        logger.error(f"Intent classifier failed: {e}")
        results["intent"] = "unknown"
        results["intent_confidence"] = 0.0
        scores["intent"] = 0.0
    
    # ========================================================================
    # 3. Stylometry Classifier
    # ========================================================================
    try:
        style_result = style_predict(analyze_request.text)
        results["style_score"] = style_result.get("style_score", 0.0)
        human_likeness = float(style_result.get("style_score", 0.0))
        scores["style"] = 1.0 - human_likeness
        logger.info(f"Style classifier: {scores['style']:.3f}")
    except Exception as e:
        logger.error(f"Stylometry classifier failed: {e}")
        results["style_score"] = 0.0
        scores["style"] = 0.5
    
    # ========================================================================
    # 4. URL Classifier
    # ========================================================================
    try:
        url_result = url_predict(analyze_request.text)
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
        keyword_result = keyword_predict(analyze_request.text)
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
    
    # Determine risk level
    if risk_score >= 0.8:
        risk_level = "HIGH"
    elif risk_score >= 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    logger.info(f"Final risk score: {risk_score:.3f} ({risk_level})")
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # ========================================================================
    # 7. Store Encrypted Data (unless sandbox mode)
    # ========================================================================
    if not analyze_request.sandbox:
        try:
            # Get account encryption key
            account_service = get_account_service()
            account_key = account_service.get_account_key(account_id)
            
            # Encrypt sensitive text
            encryption_service = get_encryption_service()
            text_enc, nonce, tag = encryption_service.encrypt_data(
                account_key, 
                analyze_request.text
            )
            
            # Build threat record with encrypted data
            threat_record = {
                "account_id": account_id,
                "text_enc": text_enc,
                "nonce": nonce,
                "tag": tag,
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "intent": results.get("intent", "unknown"),
                "ai_generated": results.get("ai_generated", False),
                "timestamp": timestamp,
                "style_score": results.get("style_score", 0.0),
                "url_detected": results.get("url_detected", False),
                "domains": results.get("domains", []),
                "keywords": results.get("keywords", [])
            }
            
            # Store in database
            supabase.table("threats").insert(threat_record).execute()
            
            logger.info(f"Encrypted threat record stored for account: {account_id}")
            
        except Exception as e:
            logger.error(f"Failed to store encrypted threat record: {e}")
            # Continue - don't fail request if storage fails
    else:
        logger.info("Sandbox mode: skipping database storage")
    
    # ========================================================================
    # 8. Return Analysis Response
    # ========================================================================
    from app.models import AnalysisDetail
    
    analysis_detail = AnalysisDetail(
        ai_generated=results.get("ai_generated", False),
        ai_confidence=results.get("ai_confidence", 0.0),
        human_confidence=results.get("human_confidence", 0.0),
        intent=results.get("intent", "unknown"),
        intent_confidence=results.get("intent_confidence", 0.0),
        style_score=results.get("style_score", 0.0),
        url_detected=results.get("url_detected", False),
        url_score=results.get("url_score", 0.0),
        domains=results.get("domains", []),
        keywords=results.get("keywords", []),
        keyword_score=results.get("keyword_score", 0.0)
    )
    
    return AnalyzeResponse(
        risk_level=risk_level,
        risk_score=float(risk_score),
        analysis=analysis_detail,
        timestamp=timestamp,
        message="Analysis completed successfully"
    )
