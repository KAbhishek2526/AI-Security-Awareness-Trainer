"""API routes for Person 2 AI Coach."""
from fastapi import APIRouter
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.services.ai_service import AIService

router = APIRouter(prefix="/coach", tags=["coach"])
service = AIService()


@router.post("/analyze", response_model=AIAnalysisSchema)
def analyze_attempt(attempt: ScenarioAttemptSchema):
    return service.analyze_user_attempt(attempt)
