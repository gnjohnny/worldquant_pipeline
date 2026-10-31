"""Record Batch 78 simulation results in PostgreSQL."""
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
            "a99ede7d",
            "TOP2000",
            "Subindustry",
            6,
            {"sharpe": 0.11, "fitness": 0.03, "turnover": 0.0810, "sub_universe_sharpe": 0.10},
            "Candidate 1 (PSAD Sales Acceleration & Yield): 5 PASS / 2 FAIL. Turnover 8.10% PASS, Sub-universe 0.10 PASS. Sharpe 0.11 and Fitness 0.03 below thresholds.",
            "REJECTED",
        ),
        (
            "01dea933",
            "TOP1000",
            "Industry",
            6,
            {"sharpe": 1.26, "fitness": 0.84, "turnover": 0.0774, "sub_universe_sharpe": 1.54},
            "Candidate 2 (SUE Earnings Surprise Drift): 6 PASS / 1 FAIL / 1 WARNING. Sharpe 1.26 PASS, Sub-universe 1.54 SPECTACULAR, Turnover 7.74% ULTRA-LOW. Fitness 0.84 failed due to unit warning on (+ 0.10) to TSPrice and lack of liquidity timing entry. High conviction candidate for revision.",
            "NEEDS_REVISION",
        ),
        (
            "872f85c9",
            "TOPSP500",
            "Sector",
            5,
            {"sharpe": -0.13, "fitness": -0.03, "turnover": 0.1774, "sub_universe_sharpe": -0.13},
            "Candidate 3 (Options Term Structure Contango): 4 PASS / 3 FAIL / 2 WARNINGS (Incompatible unit adding 0.001 to CSPrice). Sharpe -0.13 and Sub-universe -0.13 fail.",
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
                decision=decision,
                reason=reason,
                reviewer="HUMAN_RESEARCHER",
            )
            session.add(dec)
            cand.status = decision
            print(f"Recorded Candidate {cid_prefix} as {decision}.")

    session.commit()
    print("All Batch 78 candidates successfully recorded in PostgreSQL.")
