"""Unit test for application health check."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.api.routes import health_check
from app.core.config import settings


def test_health_endpoint():
    """Verify health endpoint returns 200 OK and expected structure."""
    response = health_check()
    assert response.status == "ok"
    assert response.app_name == settings.app_name
    assert response.modules["person1_scenarios"] == "ready"
    assert response.modules["person2_ai_coach"] == "ready"
    assert response.modules["person3_risk_engine"] == "ready"
    assert response.modules["person4_dashboard"] == "ready"
