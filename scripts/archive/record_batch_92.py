"""Record Batch 92 simulation results in PostgreSQL."""
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
            "39fca65a",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.84, "fitness": 0.43, "turnover": 0.1066, "sub_universe_sharpe": 1.02},
            "Candidate 1 (Domestic EBIT Yield & Operating Momentum in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe 0.84, Sub-universe Sharpe 1.02, Turnover 10.66%.",
            "NEEDS_REVISION",
        ),
        (
            "39306b0f",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 0.89, "fitness": 0.46, "turnover": 0.0983, "sub_universe_sharpe": 1.07},
            "Candidate 2 (Domestic Operating Margin Convexity Expansion in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe 0.89, Sub-universe Sharpe 1.07, Turnover 9.83%.",
            "NEEDS_REVISION",
        ),
        (
            "5ee9e75a",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": 1.00, "fitness": 0.63, "turnover": 0.1305, "sub_universe_sharpe": 1.04},
            "Candidate 3 (Domestic Core Profitability & Forward Cash Flow Yield Synergy in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe 1.00, Sub-universe Sharpe 1.04, Turnover 13.05%.",
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
    print("Batch 92 simulation results logged successfully in PostgreSQL.")
