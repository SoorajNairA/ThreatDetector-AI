"""
Online Learning API Endpoints

Endpoints:
- POST /analyze - Analyze text with online learning model
- GET /training/status - Get training status
- POST /training/run - Trigger training
- POST /training/feedback - Submit feedback correction
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.auth import get_current_user
from app.services.supabase_client import supabase
from app.services.online_learning_classifier import get_online_classifier
from app.services.training_service import get_training_service


router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    store_for_training: bool = Field(default=True, description="Store features for training (requires user consent)")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class PrivacySettingsRequest(BaseModel):
    """Request model for updating privacy settings."""
    allow_training_data: bool = Field(..., description="Allow data to be used for model training")


class PrivacySettingsResponse(BaseModel):
    """Response model for privacy settings."""
    allow_training_data: bool
    training_consent_at: Optional[datetime]
    message: str


class AnalyzeResponse(BaseModel):
    """Response model for text analysis."""
    intent: str
    confidence: float
    class_probabilities: dict
    model_version: Optional[str]
    static_intent: str
    static_probability: float
    feature_extraction_ms: float
    total_latency_ms: float
    model_status: str
    timestamp: datetime


class TrainingStatusResponse(BaseModel):
    """Response model for training status."""
    is_training: bool
    untrained_samples: int
    model_version: Optional[str]
    total_training_samples: int
    last_trained: Optional[datetime]
    feature_dim: Optional[int]
    model_loaded: bool


class TrainingRunRequest(BaseModel):
    """Request model for training run."""
    batch_size: int = Field(default=100, ge=10, le=1000)
    max_samples: int = Field(default=1000, ge=10, le=10000)


class TrainingRunResponse(BaseModel):
    """Response model for training run."""
    status: str
    samples_trained: int
    batches_processed: Optional[int]
    model_version: Optional[str]
    total_training_samples: Optional[int]
    elapsed_seconds: Optional[float]
    samples_per_second: Optional[float]
    message: Optional[str]


class FeedbackRequest(BaseModel):
    """Request model for feedback correction."""
    record_id: UUID = Field(..., description="Training data record ID")
    corrected_label: str = Field(..., description="Corrected label")
    retrain: bool = Field(default=False, description="Retrain immediately")


class FeedbackResponse(BaseModel):
    """Response model for feedback."""
    status: str
    message: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze text using online learning model.
    
    Returns risk assessment with intent classification.
    Optionally stores features for future training (requires user consent).
    """
    try:
        classifier = get_online_classifier()
        
        # Predict
        result = classifier.predict(request.text)
        
        # Store for training if requested AND user has granted consent
        consent_verified = False
        user_id = current_user.get("user_id")
        
        if request.store_for_training and user_id:
            # Check user consent
            consent_result = supabase.table("accounts").select("allow_training_data").eq("id", user_id).execute()
            if consent_result.data and len(consent_result.data) > 0:
                consent_verified = consent_result.data[0].get("allow_training_data", False)
            
            # Only store if consent granted
            if consent_verified:
                training_service = get_training_service(supabase)
                
                # Store in background with consent flag
                background_tasks.add_task(
                    training_service.store_training_sample,
                    account_id=UUID(user_id),
                    feature_vector=result['feature_vector'],
                    label=result['intent'],
                    confidence=result['confidence'],
                    source='inference',
                    metadata=request.metadata or {},
                    consent_verified=True
                )
        
        return AnalyzeResponse(
            intent=result['intent'],
            confidence=result['confidence'],
            class_probabilities=result['class_probabilities'],
            model_version=result['model_version'],
            static_intent=result['static_intent'],
            static_probability=result['static_probability'],
            feature_extraction_ms=result['feature_extraction_ms'],
            total_latency_ms=result['total_latency_ms'],
            model_status=result['model_status'],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/training/status", response_model=TrainingStatusResponse)
async def get_training_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current training status and model information.
    
    Returns untrained sample count, model version, and training stats.
    """
    try:
        training_service = get_training_service(supabase)
        user_id = current_user.get("user_id")
        account_id = UUID(user_id) if user_id else None
        
        status = await training_service.get_training_status(account_id)
        
        return TrainingStatusResponse(
            is_training=status['is_training'],
            untrained_samples=status['untrained_samples'],
            model_version=status['model_version'],
            total_training_samples=status['total_training_samples'],
            last_trained=status['last_trained'],
            feature_dim=status['feature_dim'],
            model_loaded=status['model_loaded']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/training/run", response_model=TrainingRunResponse)
async def run_training(
    request: TrainingRunRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger training on untrained samples.
    
    Runs training in the background and returns immediately.
    Use GET /training/status to monitor progress.
    """
    try:
        training_service = get_training_service(supabase)
        user_id = current_user.get("user_id")
        account_id = UUID(user_id) if user_id else None
        
        # Run training in background
        background_tasks.add_task(
            training_service.train_on_new_data,
            account_id=account_id,
            batch_size=request.batch_size,
            max_samples=request.max_samples
        )
        
        return TrainingRunResponse(
            status='started',
            samples_trained=0,
            batches_processed=None,
            model_version=None,
            total_training_samples=None,
            elapsed_seconds=None,
            samples_per_second=None,
            message='Training started in background'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


@router.post("/training/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback to correct a classification.
    
    Updates the label for a training sample.
    Optionally retrains immediately on the corrected sample.
    """
    try:
        training_service = get_training_service(supabase)
        
        result = await training_service.apply_feedback(
            record_id=request.record_id,
            corrected_label=request.corrected_label,
            retrain=request.retrain
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return FeedbackResponse(
            status=result['status'],
            message=result['message']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")


@router.get("/model/info")
async def get_model_info():
    """Get information about the loaded model."""
    try:
        classifier = get_online_classifier()
        
        return {
            'model_version': classifier.model_version,
            'total_training_samples': classifier.training_samples,
            'last_trained': classifier.last_trained.isoformat() if classifier.last_trained else None,
            'feature_dim': classifier.feature_dim,
            'model_loaded': classifier.model is not None,
            'classes': classifier.classes.tolist(),
            'model_type': 'SGDClassifier (Logistic Regression with partial_fit)'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.get("/privacy", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current privacy settings for training data usage.
    
    Returns whether user has consented to use their data for model training.
    """
    try:
        user_id = current_user.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        result = supabase.table("accounts").select(
            "allow_training_data, training_consent_at"
        ).eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        
        data = result.data[0]
        
        return PrivacySettingsResponse(
            allow_training_data=data.get("allow_training_data", False),
            training_consent_at=data.get("training_consent_at"),
            message="Privacy settings retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get privacy settings: {str(e)}")


@router.post("/privacy", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    request: PrivacySettingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update privacy settings for training data usage.
    
    When enabled, your analysis data will be used to improve model accuracy.
    When disabled, your data will NOT be stored or used for training.
    
    Note: This only affects future data. Previously stored data remains unchanged.
    """
    try:
        user_id = current_user.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        # Update account with new consent setting
        update_data = {
            "allow_training_data": request.allow_training_data,
            "training_consent_at": datetime.now().isoformat()
        }
        
        result = supabase.table("accounts").update(update_data).eq(
            "id", user_id
        ).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        
        data = result.data[0]
        
        message = (
            "Training data usage enabled. Your data will help improve model accuracy."
            if request.allow_training_data
            else "Training data usage disabled. Your data will not be used for training."
        )
        
        return PrivacySettingsResponse(
            allow_training_data=data["allow_training_data"],
            training_consent_at=data.get("training_consent_at"),
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update privacy settings: {str(e)}")

