"""Record Batch 100 simulation results in PostgreSQL."""
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
            "669672d4",
            "TOP3000",
            "Market",
            4,
            {"sharpe": 0.45, "fitness": 0.26, "turnover": 0.1831, "sub_universe_sharpe": 0.28},
            "Candidate 1 (Domestic EBIT Convexity in TOP3000 Market, Decay 4): 5 PASS / 2 FAIL. Sharpe 0.45, Fitness 0.26 below cutoffs.",
            "REJECTED",
        ),
        (
            "09c6b438",
            "TOP3000",
            "Market",
            4,
            {"sharpe": 0.85, "fitness": 0.62, "turnover": 0.1868, "sub_universe_sharpe": 0.73},
            "Candidate 2 (Free Cash Flow Yield in TOP3000 Market, Decay 4): 5 PASS / 2 FAIL. Sharpe 0.85, Fitness 0.62 below cutoffs.",
            "REJECTED",
        ),
        (
            "8dcd5b38",
            "TOP3000",
            "Market",
            4,
            {"sharpe": 0.91, "fitness": 0.52, "turnover": 0.1996, "sub_universe_sharpe": 1.01},
            "Candidate 3 (Pentagon Surface Accel in TOP3000 Market, Decay 4): 5 PASS / 2 FAIL. Sharpe 0.91, Fitness 0.52 below cutoffs, Sub-universe Sharpe 1.01 passed.",
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
    print("Batch 100 simulation results logged successfully in PostgreSQL.")
