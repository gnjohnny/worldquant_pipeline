"""Record Batch 86 simulation results in PostgreSQL."""
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
            "63a78736",
            "TOP1000",
            "Subindustry",
            6,
            {"sharpe": 1.35, "fitness": 0.67, "turnover": 0.3850, "sub_universe_sharpe": 0.77},
            "Candidate 1 (5-Day Linear Decay Microstructure in TOP1000 Subindustry, Decay 6): 6 PASS / 1 FAIL. Sharpe 1.35 > 1.25 PASS, Turnover 38.50% in [1%, 70%] PASS, Sub-universe 0.77 PASS. Fitness 0.67 failed the mandatory cutoff of 1.50 due to 38.50% turnover.",
            "NEEDS_REVISION",
        ),
        (
            "58f1564b",
            "TOP1000",
            "Subindustry",
            6,
            {"sharpe": 1.93, "fitness": 0.76, "turnover": 0.7430, "sub_universe_sharpe": 0.99},
            "Candidate 2 (10-Day TS Rank Microstructure in TOP1000 Subindustry, Decay 6): 4 PASS / 3 FAIL. Outstanding Sharpe 1.93, but Turnover 74.30% exceeded 70% threshold, keeping Fitness at 0.76.",
            "NEEDS_REVISION",
        ),
        (
            "e42333e3",
            "TOP1000",
            "Subindustry",
            6,
            {"sharpe": 1.14, "fitness": 0.49, "turnover": 0.3895, "sub_universe_sharpe": 0.71},
            "Candidate 3 (VWAP Deviation Smoothing in TOP1000 Subindustry, Decay 6): 5 PASS / 2 FAIL. Sharpe 1.14 and Fitness 0.49 failed cutoffs.",
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
    print("Batch 86 simulation results logged successfully in PostgreSQL.")
