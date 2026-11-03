"""Record Batch 77 simulation rejections in PostgreSQL."""
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
            "d8a3e9e7",
            "TOP3000",
            "Subindustry",
            0,
            {"sharpe": -0.05, "fitness": -0.01, "turnover": 0.2007, "sub_universe_sharpe": -0.10},
            "Candidate 1 (model51 Low-Beta & Risk Spike): 3 PASS / 4 FAIL. Sharpe -0.05, Fitness -0.01, Sub-universe -0.10, and weight concentration 15.38% > 10% cutoff. Raw beta without fundamental quality filter fails in recent mega-cap tech momentum regimes.",
        ),
        (
            "f734510a",
            "TOP2000",
            "Subindustry",
            0,
            {"sharpe": 0.11, "fitness": 0.02, "turnover": 0.0593, "sub_universe_sharpe": -0.28},
            "Candidate 2 (model16 Style Surface Accel & Quality): 4 PASS / 3 FAIL. Turnover 5.93% PASS. Sharpe 0.11 and Sub-universe -0.28 fail due to low instrument coverage (~37%) of style surface acceleration.",
        ),
        (
            "04cdcd74",
            "TOP1000",
            "Sector",
            0,
            {"sharpe": -0.60, "fitness": -0.16, "turnover": 0.7442, "sub_universe_sharpe": -0.04},
            "Candidate 3 (pv1 Overnight Gap vs Intraday Disparity): 4 PASS / 3 FAIL. Turnover 74.42% exceeds 70% cutoff, Sharpe -0.60 fails. Daily session gaps suffer extreme churn without volume execution anchors.",
        ),
    ]

    for cid_prefix, universe, neut, decay, metrics, reason in batch_records:
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
                session.add(
                    ExperimentMetric(
                        experiment_id=exp.id,
                        metric_name=k,
                        metric_value=v,
                        source="BRAIN_PLATFORM",
                    )
                )

            dec = Decision(
                candidate_id=cand.id,
                decision="REJECTED",
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            cand.status = "REJECTED"
            print(f"Recorded Candidate {cid_prefix} as REJECTED.")

    session.commit()
    print("All Batch 77 candidates successfully recorded in PostgreSQL.")
