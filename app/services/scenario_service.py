"""
Scenario Service Interface (Person 1 Ownership)
Exposes business logic for fetching, filtering, and evaluating scenario interactions.
"""

from typing import List, Optional
from app.schemas.scenario import ScenarioSchema
from app.scenarios.scenario_engine import ScenarioEngine
from app.core.constants import ThreatCategory, DifficultyLevel


class ScenarioService:
    """Service wrapping scenario engine logic."""

    def __init__(self, engine: Optional[ScenarioEngine] = None):
        self.engine = engine or ScenarioEngine()

    def get_all(self) -> List[ScenarioSchema]:
        """Fetch all scenarios."""
        return self.engine.list_scenarios()

    def get_scenario(self, scenario_id: str) -> ScenarioSchema:
        """Fetch scenario by ID."""
        return self.engine.get_by_id(scenario_id)

    def get_recommended_scenario(
        self,
        category: ThreatCategory,
        difficulty: DifficultyLevel
    ) -> Optional[ScenarioSchema]:
        """Fetch scenario matching recommended category and difficulty."""
        matching = self.engine.filter_scenarios(category=category, difficulty=difficulty)
        if matching:
            return matching[0]
        # Fallback to category only if exact difficulty isn't found
        fallback = self.engine.filter_scenarios(category=category)
        return fallback[0] if fallback else (self.engine.list_scenarios()[0] if self.engine.list_scenarios() else None)
