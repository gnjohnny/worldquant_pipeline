"""Record Batch 93 simulation results in PostgreSQL."""
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
    batch_records = [
        (
            "c6eb0f3f",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.00, "fitness": 0.00, "turnover": 0.4973, "sub_universe_sharpe": -0.18},
            "Candidate 1 (Put-Call Implied Volatility Smirk in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. High turnover 49.73% and zero Sharpe.",
            "REJECTED",
        ),
        (
            "cc1ff31b",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.49, "fitness": 0.18, "turnover": 0.1520, "sub_universe_sharpe": 0.05},
            "Candidate 2 (Analyst Consensus Earnings Yield vs Dispersion in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Turnover 15.20% clean, but Sharpe 0.49 below cutoff.",
            "REJECTED",
        ),
        (
            "e4db10ac",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.41, "fitness": -0.11, "turnover": 0.2754, "sub_universe_sharpe": -0.19},
            "Candidate 3 (Idiosyncratic Variance Dislocation Normalization in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Failed weight concentration and Sharpe cutoff.",
            "REJECTED",
        ),
    ]

    for cid_prefix, universe, neut, decay, metrics, reason, decision in batch_records:
        cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith(cid_prefix)).first()
        if cand:
            exp = Experiment(
                candidate_id=cand.id,
                status="COMPLETED",
                universe=universe,
                delay=1,
                decay=decay,
                neutralization=neut,
                truncation=0.0100,
            )
            session.add(exp)
            session.flush()

            for k, v in metrics.items():
                session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

            cand.status = decision
            dec = Decision(
                candidate_id=cand.id,
                decision=decision,
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)

    session.commit()
    print("Batch 93 simulation results logged successfully in PostgreSQL.")
