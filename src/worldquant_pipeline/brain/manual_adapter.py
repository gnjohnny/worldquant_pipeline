"""Manual-first WorldQuant BRAIN platform adapter."""
from dataclasses import dataclass
from typing import Any

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.storage.models import AlphaCandidate


@dataclass
class SimulationCard:
    """Complete simulation specification formatted for WorldQuant BRAIN web dashboard."""
    candidate_id: str
    expression: str
    region: str
    universe: str
    delay: int
    decay: int
    neutralization: str
    truncation: float
    hypothesis_title: str
    economic_rationale: str
    intended_horizon: str


class ManualBrainAdapter:
    """Prepares and formats candidate alphas for manual execution on WorldQuant BRAIN."""

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        settings = get_settings()
        self.defaults = defaults or settings.research_config.get("simulation_defaults", {
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 4,
            "neutralization": "Subindustry",
            "truncation": 0.0100,
        })

    def format_candidate(self, candidate: AlphaCandidate) -> SimulationCard:
        """Build a simulation card for a candidate."""
        hypo = candidate.hypothesis
        return SimulationCard(
            candidate_id=candidate.id,
            expression=candidate.expression_raw,
            region=self.defaults.get("region", "USA"),
            universe=self.defaults.get("universe", "TOP3000"),
            delay=int(self.defaults.get("delay", 1)),
            decay=int(self.defaults.get("decay", 4)),
            neutralization=self.defaults.get("neutralization", "Subindustry"),
            truncation=float(self.defaults.get("truncation", 0.0100)),
            hypothesis_title=hypo.title if hypo else "Unknown",
            economic_rationale=hypo.economic_rationale if hypo else "None",
            intended_horizon=hypo.intended_horizon if hypo else "5d",
        )
