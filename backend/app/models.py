"""Pydantic models and schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint"""
    text: str = Field(..., description="Text content to analyze")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    sandbox: Optional[bool] = Field(False, description="If true, results won't be stored")


class AnalysisDetail(BaseModel):
    """Detailed analysis breakdown"""
    ai_generated: bool
    ai_confidence: float
    human_confidence: float
    intent: str
    intent_confidence: float
    style_score: float
    url_detected: bool
    url_score: float
    domains: List[str]
    keywords: List[str]
    keyword_score: float


class AnalyzeResponse(BaseModel):
    """Response model for /analyze endpoint"""
    risk_level: str = Field(..., description="Risk level: HIGH, MEDIUM, or LOW")
    risk_score: float = Field(..., description="Computed risk score between 0 and 1")
    analysis: AnalysisDetail
    timestamp: str = Field(..., description="ISO timestamp of analysis")
    message: Optional[str] = Field(None, description="Optional status message")


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str


class StatsResponse(BaseModel):
    """Response model for /stats endpoint"""
    total: int
    high: int
    medium: int
    low: int
    actors: Optional[int] = None
    last: Optional[str] = None
