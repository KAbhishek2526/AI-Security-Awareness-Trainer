"""API routes for Person 1 Scenarios."""
from fastapi import APIRouter
from typing import List
from app.schemas.scenario import ScenarioSchema
from app.services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
service = ScenarioService()


@router.get("/", response_model=List[ScenarioSchema])
def list_scenarios():
    return service.get_all()
