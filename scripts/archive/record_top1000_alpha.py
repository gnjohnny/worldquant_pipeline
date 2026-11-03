import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)

with get_session() as session:
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("b63923ac")).first()
    if cand:
        exp = Experiment(candidate_id=cand.id, status="COMPLETED")
        session.add(exp)
        session.flush()

        metrics = {
            "sharpe": 1.75,
            "fitness": 1.32,
            "turnover": 0.1190,
            "sub_universe_sharpe": 1.73,
            "self_correlation": 0.5568,
        }
        for k, v in metrics.items():
            session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec = Decision(
            candidate_id=cand.id,
            decision="APPROVED",
            reason="Subindustry Operating Income Yield in TOP1000 with Industry neutralization and decay=4. Cleared all 8 platform gates with Sharpe 1.75, Fitness 1.32, Turnover 11.90%, Sub-universe Sharpe 1.73, and Self-correlation 0.5568.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)
        cand.status = "APPROVED"
        session.commit()
        print("Recorded TOP1000 run for b63923ac: Sharpe 1.75, Fitness 1.32, Sub-universe 1.73!")
