"""Record Batch 95 simulation results in PostgreSQL."""
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
            "8e911270",
            "TOP1000",
            "Industry",
            6,
            {"sharpe": 1.23, "fitness": 0.80, "turnover": 0.0880, "sub_universe_sharpe": 1.13},
            "Candidate 1 (Cash Flow Per Share Yield & Momentum in TOP1000 Industry, Decay 6): 5 PASS / 2 FAIL. Sharpe 1.23 (just 0.02 below cutoff), Sub-universe Sharpe 1.13 strong, Turnover 8.80% compressed.",
            "NEEDS_REVISION",
        ),
        (
            "fa4f79c1",
            "TOP1000",
            "Industry",
            5,
            {"sharpe": 0.94, "fitness": 0.58, "turnover": 0.1175, "sub_universe_sharpe": 1.03},
            "Candidate 2 (Domestic EBIT Convex Decile Yield in TOP1000 Industry, Decay 5): 5 PASS / 2 FAIL. Sharpe 0.94, Sub-universe Sharpe 1.03, Turnover 11.75%.",
            "NEEDS_REVISION",
        ),
        (
            "6f6cfd58",
            "TOP1000",
            "Market",
            6,
            {"sharpe": 1.28, "fitness": 1.41, "turnover": 0.0799, "sub_universe_sharpe": 1.15, "self_correlation": 0.8042},
            "Candidate 3 (1-Year LEAP VRP Contango in TOP1000 Market, Decay 6): 7 PASS / 1 FAIL. Sharpe 1.28 and Fitness 1.41 passed, but Self-correlation 0.8042 failed cutoff 0.70 due to overlap with 7c3e864f.",
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
    print("Batch 95 simulation results logged successfully in PostgreSQL.")
