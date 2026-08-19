"""API routes for Person 3 Risk Engine."""
from fastapi import APIRouter
from app.schemas.risk import RiskProfileSchema
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["risk"])
service = RiskService()


@router.get("/profile/{user_id}", response_model=RiskProfileSchema)
def get_profile(user_id: str):
    return service.get_user_risk_profile(user_id)
