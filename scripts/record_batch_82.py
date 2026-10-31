"""Record Batch 82 simulation results in PostgreSQL."""
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
            "42f371e0",
            "TOP1000",
            "Industry",
            4,
            {"sharpe": 1.51, "fitness": 1.10, "turnover": 0.1338, "sub_universe_sharpe": 1.33, "self_correlation": 0.6356},
            "Candidate 1 (Cash Flow Yield in TOP1000 Industry Neutral, Decay 4): 8 PASS. Sharpe 1.51 > 1.25 PASS, Turnover 13.38% PASS, Sub-universe 1.33 PASS, Self-correlation 0.6356 < 0.70 PASS. However, Fitness is 1.10 which is below Gold Consultant mandatory cutoff of 1.50 (GOOD). Marked as NEEDS_REVISION per Gold Track Invariant #1.",
            "NEEDS_REVISION",
        ),
        (
            "02e5cb74",
            "TOP1000",
            "Market",
            4,
            {"sharpe": 1.55, "fitness": 1.59, "turnover": 0.1167, "sub_universe_sharpe": 1.56, "self_correlation": 0.7445},
            "Candidate 2 (Operating Leverage in TOP1000 Market Neutral, Decay 4): 7 PASS / 1 FAIL. Sharpe 1.55 and Fitness 1.59 (GOOD) achieved, but Self-correlation is 0.7445 > 0.70 cutoff against Alpha 27. High correlation failure due to formula template recycling.",
            "NEEDS_REVISION",
        ),
        (
            "55420399",
            "TOP1000",
            "Sector",
            4,
            {"sharpe": 1.84, "fitness": 1.31, "turnover": 0.3482, "sub_universe_sharpe": 1.54, "self_correlation": 0.8004},
            "Candidate 3 (Option Skew & VRP in TOP1000 Sector Neutral, Decay 4): 7 PASS / 1 FAIL. Sharpe 1.84 and Fitness 1.31, but Self-correlation 0.8004 > 0.70 cutoff. Correlated with earlier option/volatility alphas due to identical 3-term linear polynomial combination.",
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
    print("Batch 82 simulation results logged successfully in PostgreSQL.")
