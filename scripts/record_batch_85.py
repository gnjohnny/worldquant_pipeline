"""Record Batch 85 simulation results in PostgreSQL."""
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
            "8a1aea20",
            "TOP1000",
            "Subindustry",
            5,
            {"sharpe": -0.66, "fitness": -0.36, "turnover": 0.1732, "sub_universe_sharpe": -0.19},
            "Candidate 1 (Trend Efficiency Ratio in TOP1000 Subindustry, Decay 5): 5 PASS / 2 FAIL. Sharpe -0.66 and Fitness -0.36 fail cutoffs. Price path efficiency alone did not establish directional edge.",
            "REJECTED",
        ),
        (
            "574e34ba",
            "TOP1000",
            "Subindustry",
            4,
            {"sharpe": 1.93, "fitness": 0.77, "turnover": 0.8488, "sub_universe_sharpe": 1.13},
            "Candidate 2 (Abnormal Volume Absorption Reversion in TOP1000 Subindustry, Decay 4): 5 PASS / 2 FAIL. OUTSTANDING Sharpe 1.93 > 1.25, Sub-universe 1.13 > 1.02. Turnover was 84.88% (exceeding 70% limit), directly penalizing Fitness to 0.77. Primary candidate for temporal smoothing (ts_decay_linear / ts_rank) to compress turnover into 15-25% range and unlock Fitness >= 1.50.",
            "NEEDS_REVISION",
        ),
        (
            "3762c7d9",
            "TOP1000",
            "Subindustry",
            4,
            {"sharpe": -0.06, "fitness": -0.01, "turnover": 0.0720, "sub_universe_sharpe": -0.15},
            "Candidate 3 (Intra-Industry Low-Beta in TOP1000 Subindustry, Decay 4): 3 PASS / 4 FAIL. Failed instrument concentration and Sharpe cutoffs.",
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
    print("Batch 85 simulation results logged successfully in PostgreSQL.")
