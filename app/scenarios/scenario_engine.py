"""
Scenario Engine (Person 1 Ownership)
Handles scenario catalog loading, filtering by category/difficulty, and metadata lookup.
"""

import json
from pathlib import Path
from typing import List, Optional
from app.schemas.scenario import ScenarioSchema
from app.core.constants import ThreatCategory, DifficultyLevel
from app.core.exceptions import ScenarioNotFoundError, InvalidScenarioDataError


class ScenarioEngine:
    """Core scenario simulator engine owned by Person 1."""

    def __init__(self, data_path: Optional[str] = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = Path(__file__).parent / "data" / "scenarios.json"
        self._scenarios: List[ScenarioSchema] = []
        self.load_scenarios()

    def load_scenarios(self) -> None:
        """Load and validate scenarios from JSON storage."""
        if not self.data_path.exists():
            self._scenarios = []
            return
        
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self._scenarios = [ScenarioSchema(**item) for item in raw_data]
        except Exception as e:
            raise InvalidScenarioDataError(f"Failed to load scenarios from {self.data_path}: {e}")

    def list_scenarios(self) -> List[ScenarioSchema]:
        """Get all available scenarios."""
        return self._scenarios

    def get_by_id(self, scenario_id: str) -> ScenarioSchema:
        """Retrieve scenario by unique ID."""
        for sc in self._scenarios:
            if sc.scenario_id == scenario_id:
                return sc
        raise ScenarioNotFoundError(f"Scenario with ID '{scenario_id}' not found.")

    def filter_scenarios(
        self,
        category: Optional[ThreatCategory] = None,
        difficulty: Optional[DifficultyLevel] = None
    ) -> List[ScenarioSchema]:
        """Filter scenarios by threat category and/or difficulty level."""
        results = self._scenarios
        if category:
            results = [s for s in results if s.category == category]
        if difficulty:
            results = [s for s in results if s.difficulty == difficulty]
        return results
