"""Record Batch 83 simulation results in PostgreSQL."""
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
            "d3e02ace",
            "TOP1000",
            "Subindustry",
            4,
            {"sharpe": -0.86, "fitness": -0.39, "turnover": 0.3105, "sub_universe_sharpe": -0.35},
            "Candidate 1 (Supply-Chain Customer Return Diffusion in TOP1000 Subindustry, Decay 4): 5 PASS / 2 FAIL. Sharpe -0.86 and Fitness -0.39 fail cutoffs. Raw customer return signal showed negative predictive drift.",
            "REJECTED",
        ),
        (
            "f381efd0",
            "TOP1000",
            "Subindustry",
            4,
            {"sharpe": -0.38, "fitness": -0.18, "turnover": 0.1528, "sub_universe_sharpe": 0.02},
            "Candidate 2 (Market Maker Gamma Support Buffer in TOP1000 Subindustry, Decay 4): 5 PASS / 2 FAIL. Sharpe -0.38 and Fitness -0.18 fail cutoffs. Put breakeven buffer alone lacked sufficient cross-sectional discriminatory power.",
            "REJECTED",
        ),
        (
            "ab50aa7f",
            "TOP1000",
            "Subindustry",
            4,
            {"sharpe": -0.50, "fitness": -0.33, "turnover": 0.0376, "sub_universe_sharpe": -0.23},
            "Candidate 3 (Non-Linear Derivative Product in TOP1000 Subindustry, Decay 4): 5 PASS / 2 FAIL. Sharpe -0.50 and Fitness -0.33 fail cutoffs. Multiplying rank derivatives distorted cross-sectional distribution and created negative drift.",
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
    print("Batch 83 simulation results logged successfully in PostgreSQL.")
