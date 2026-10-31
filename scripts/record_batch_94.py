"""Record Batch 94 simulation results in PostgreSQL."""
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
            "d1aad216",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.39, "fitness": 0.15, "turnover": 0.1103, "sub_universe_sharpe": 0.65},
            "Candidate 1 (Cash Flow SUE Surprise & Yield in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL / 1 WARNING. Unit warning on actual_cashflow_per_share (TSPrice) - anl4_cfps (Unit[]). Sharpe 0.39 below cutoff.",
            "REJECTED",
        ),
        (
            "d9e5a836",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.66, "fitness": 0.27, "turnover": 0.0742, "sub_universe_sharpe": 0.26},
            "Candidate 2 (Balance Sheet Deleveraging & Cash Solvency in TOP1000 Subindustry, Decay 5): 4 PASS / 3 FAIL. Low turnover 7.42%, but Sharpe 0.66 below cutoff.",
            "REJECTED",
        ),
        (
            "2a9532a9",
            "TOP1000",
            "Subindustry",
            6,
            {"sharpe": 0.85, "fitness": 0.36, "turnover": 0.2117, "sub_universe_sharpe": 0.85},
            "Candidate 3 (Long-Horizon LEAP VRP Contango in TOP1000 Subindustry, Decay 6): 5 PASS / 2 FAIL. Sub-universe Sharpe 0.85, Sharpe 0.85, Turnover 21.17%. Needs parameter optimization.",
            "NEEDS_REVISION",
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
    print("Batch 94 simulation results logged successfully in PostgreSQL.")
