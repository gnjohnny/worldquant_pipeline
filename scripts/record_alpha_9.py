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
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f37ccff2")).first()
    if cand:
        exp = Experiment(candidate_id=cand.id, status="COMPLETED")
        session.add(exp)
        session.flush()

        metrics = {
            "sharpe": 1.74,
            "fitness": 1.36,
            "turnover": 0.1218,
            "sub_universe_sharpe": 1.33,
            "self_correlation": 0.4259,
        }
        for k, v in metrics.items():
            session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec = Decision(
            candidate_id=cand.id,
            decision="APPROVED",
            reason="Alpha 9: Subindustry Analyst Consensus Adjusted Net Income Yield Valuation Breakout. Cleared all 8 platform gates in TOP1000 with Sharpe 1.74, Fitness 1.36, Turnover 12.18%, Sub-universe Sharpe 1.33, and low Self-correlation 0.4259.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)
        cand.status = "APPROVED"
        session.commit()
        print(f"Recorded and approved Alpha 9: {cand.id} ({cand.expression_raw})")
