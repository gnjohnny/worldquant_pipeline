"""Record Batch 91 simulation results in PostgreSQL."""
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
            "5a1149d4",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.91, "fitness": 0.52, "turnover": 0.1103, "sub_universe_sharpe": 1.06},
            "Candidate 1 (Forward Cash Flow Yield & Consensus Revision Momentum in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Positive Sharpe 0.91, Sub-universe Sharpe 1.06 well above cutoff 0.48. Turnover 11.03% clean. Showing consistent positive traction.",
            "NEEDS_REVISION",
        ),
        (
            "ce72d4f4",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.20, "fitness": -0.02, "turnover": 0.6471, "sub_universe_sharpe": 0.24},
            "Candidate 2 (Retail Attention Surge & Social Buzz Reversal in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. High turnover 64.71% and negative Sharpe -0.20.",
            "REJECTED",
        ),
        (
            "e5961b72",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 1.00, "fitness": 0.57, "turnover": 0.1166, "sub_universe_sharpe": 1.05},
            "Candidate 3 (Core Domestic Operating Profitability EBIT Yield in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Strong Sharpe 1.00, Sub-universe Sharpe 1.05 passed cutoff 0.53, Turnover 11.66% ideal. High-conviction candidate for margin/momentum enhancement.",
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
    print("Batch 91 simulation results logged successfully in PostgreSQL.")
