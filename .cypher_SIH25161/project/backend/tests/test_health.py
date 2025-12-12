"""Test health endpoint"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test that /health endpoint returns status ok"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_content_type():
    """Test that /health endpoint returns JSON"""
    response = client.get("/health")
    
    assert response.headers["content-type"] == "application/json"
