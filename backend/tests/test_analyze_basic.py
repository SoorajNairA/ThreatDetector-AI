"""Test analyze endpoint basic functionality"""
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


def test_analyze_basic():
    """Test basic /analyze endpoint functionality"""
    # Mock the Supabase insert to avoid actual database calls in tests
    with patch('app.routes.analyze.insert_threat'):
        payload = {
            "text": "Click here to verify your bank account password urgently!"
        }
        
        response = client.post("/analyze", json=payload)
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields exist
        assert "risk_level" in data
        assert "risk_score" in data
        assert "analysis" in data
        assert "timestamp" in data
        
        # Check risk_level is valid
        assert data["risk_level"] in ["HIGH", "MEDIUM", "LOW"]
        
        # Check risk_score is in valid range
        assert 0.0 <= data["risk_score"] <= 1.0
        
        # Check analysis contains required fields
        analysis = data["analysis"]
        assert "intent" in analysis
        assert "ai_generated" in analysis
        assert "keywords" in analysis
        assert "url_detected" in analysis


def test_analyze_high_risk_text():
    """Test that high-risk text gets appropriate classification"""
    with patch('app.routes.analyze.insert_threat'):
        # Text with many threat indicators
        payload = {
            "text": "URGENT: Click here to verify your bank account login password immediately! "
                   "Your account will be suspended. Win prizes by confirming now!"
        }
        
        response = client.post("/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect high risk due to multiple keywords
        assert data["risk_level"] in ["HIGH", "MEDIUM"]
        assert len(data["analysis"]["keywords"]) > 0


def test_analyze_low_risk_text():
    """Test that benign text gets low classification"""
    with patch('app.routes.analyze.insert_threat'):
        payload = {
            "text": "Hello, how are you today? The weather is nice."
        }
        
        response = client.post("/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be low risk
        assert data["risk_level"] == "LOW"


def test_analyze_missing_text():
    """Test that missing text field returns error"""
    response = client.post("/analyze", json={})
    
    # Should return 422 Unprocessable Entity for missing required field
    assert response.status_code == 422


def test_analyze_with_metadata():
    """Test analyze endpoint with optional metadata"""
    with patch('app.routes.analyze.insert_threat'):
        payload = {
            "text": "Test message",
            "metadata": {
                "source": "email",
                "user_id": "test123"
            }
        }
        
        response = client.post("/analyze", json=payload)
        
        assert response.status_code == 200
