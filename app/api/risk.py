"""API routes for Person 3 Risk Engine (Person 4 Integration)."""
from fastapi import APIRouter
from app.schemas.risk import RiskProfileSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["risk"])
service = RiskService()


@router.get("/profile/{user_id}", response_model=RiskProfileSchema)
def get_profile(user_id: str):
    """Retrieve user security risk profile."""
    return service.get_user_risk_profile(user_id)


@router.post("/update", response_model=RiskProfileSchema)
def update_profile(analysis: AIAnalysisSchema):
    """Update user security profile with AI analysis."""
    return service.record_analysis_and_update_risk(analysis)
