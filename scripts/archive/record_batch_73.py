"""Record simulation results and decisions for Batch 73."""
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
            "57e31605",
            "TOP3000",
            "SUBINDUSTRY",
            0,
            {"sharpe": 0.06, "fitness": 0.01, "turnover": 0.0494, "sub_universe_sharpe": 0.28},
            "Candidate 1 (H01 Sloan Accruals): 5 PASS / 2 FAIL. Turnover 4.94%, Sub-universe 0.28 PASS. Sharpe 0.06 and Fitness 0.01 fail cutoffs. Raw accrual needs yield scaling (/ close).",
        ),
        (
            "0371378d",
            "TOP2000",
            "SUBINDUSTRY",
            0,
            {"sharpe": -0.27, "fitness": -0.07, "turnover": 0.0911, "sub_universe_sharpe": -0.18},
            "Candidate 2 (H11 Analyst Uncertainty): 4 PASS / 3 FAIL. Turnover 9.11% PASS. Sharpe -0.27 and Fitness -0.07 fail cutoffs. 30d delta is sparse without price scaling.",
        ),
        (
            "e83d8b50",
            "TOPSP500",
            "SECTOR",
            0,
            {"sharpe": -0.35, "fitness": -0.08, "turnover": 0.3256, "sub_universe_sharpe": -0.06},
            "Candidate 3 (H15 Options IV Smirk): 5 PASS / 2 FAIL / 1 WARNING (Incompatible unit adding 0.001 to TSPrice). Sharpe -0.35 and Fitness -0.08 fail.",
        ),
        (
            "b2f20062",
            "TOP1000",
            "SUBINDUSTRY",
            0,
            {"sharpe": 0.10, "fitness": 0.03, "turnover": 0.0261, "sub_universe_sharpe": -0.07},
            "Candidate 4 (H03 Asset Bloat vs Margin): 4 PASS / 3 FAIL. Turnover 2.61% PASS. Sharpe 0.10, Fitness 0.03, Sub-universe -0.07 fail.",
        ),
        (
            "b276832a",
            "TOP2000",
            "SUBINDUSTRY",
            0,
            {"sharpe": -1.60, "fitness": -0.75, "turnover": 0.7359, "sub_universe_sharpe": -1.33},
            "Candidate 5 (H13 Supply Chain): 3 PASS / 4 FAIL. High churn (Turnover 73.59%) and Sharpe -1.60 fail. Raw signal requires heavy smoothing or decay.",
        ),
        (
            "1289f59d",
            "TOP3000",
            "SUBINDUSTRY",
            0,
            {"sharpe": 0.47, "fitness": 0.15, "turnover": 0.0320, "sub_universe_sharpe": -0.01},
            "Candidate 6 (H18 Debt Cliff): 4 PASS / 3 FAIL. Positive Sharpe 0.47, Turnover 3.20% PASS, but Fitness 0.15 and Sub-universe -0.01 below cutoffs.",
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
    print("All Batch 73 candidates successfully recorded in PostgreSQL.")
