"""Record simulation results and decisions for Batch 74."""
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
            "b4bb5f2b",
            "TOP1000",
            "Industry",
            5,
            {"sharpe": 0.27, "fitness": 0.12, "turnover": 0.0975, "sub_universe_sharpe": 0.0},
            "Candidate 1 (Sloan Accrual Yield): 4 PASS / 3 FAIL. Turnover 9.75% PASS. Sharpe 0.27, Fitness 0.12, Sub-universe 0.0 fail cutoffs. Accrual delta between quarterly and annual statements introduces noise.",
        ),
        (
            "18f40659",
            "TOP2000",
            "Industry",
            5,
            {"sharpe": 0.96, "fitness": 0.62, "turnover": 0.0893, "sub_universe_sharpe": 1.19},
            "Candidate 2 (Analyst Consensus Yield & 60d Revision): 5 PASS / 2 FAIL. Turnover 8.93% PASS, Sub-universe Sharpe 1.19 PASS. Sharpe 0.96 and Fitness 0.62 close to thresholds. Needs short-term liquidity entry timing.",
        ),
        (
            "568e6161",
            "TOPSP500",
            "Sector",
            4,
            {"sharpe": 1.12, "fitness": 0.63, "turnover": 0.3273, "sub_universe_sharpe": 1.57},
            "Candidate 3 (LEAP Call Term Structure & Skew): 5 PASS / 2 FAIL / 1 WARNING. Sub-universe Sharpe 1.57 SPECTACULAR. Sharpe 1.12 near 1.25 cutoff. Unit warning on parkinson_volatility + 0.001; 30d skew churn elevated turnover.",
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
    print("All Batch 74 candidates successfully recorded in PostgreSQL.")
