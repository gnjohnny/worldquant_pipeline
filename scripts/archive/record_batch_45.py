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
    # 1. Candidate 1: 7b76750c (180-Day TS Rank on Quarterly FX)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7b76750c")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 0.47,
            "fitness": 0.17,
            "turnover": 0.1581,
            "sub_universe_sharpe": 0.33,
        }
        for k, v in m1.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp1.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL. Sharpe 0.47 and Fitness 0.17 below cutoffs due to discrete step function variance collapse in 180d ts_rank.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 13b0d33d (Volatility-Scaled 5-Day Reversal Overlay)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("13b0d33d")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.37,
            "fitness": 0.88,
            "turnover": 0.1344,
            "sub_universe_sharpe": 1.21,
        }
        for k, v in m2.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp2.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec2 = Decision(
            candidate_id=c2.id,
            decision="NEEDS_REVISION",
            reason="6 PASS / 1 FAIL / 1 WARNING. Sharpe 1.37 and Sub-universe 1.21 passed, but Fitness 0.88 missed cutoff. Unit warning on ts_std_dev + 0.01.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as NEEDS_REVISION.")

    # 3. Candidate 3: 3c75ccd0 (Foreign Operating Hedging Ratio)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3c75ccd0")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 1.40,
            "fitness": 0.95,
            "turnover": 0.1231,
            "sub_universe_sharpe": 0.66,
        }
        for k, v in m3.items():
            session.add(
                ExperimentMetric(
                    experiment_id=exp3.id,
                    metric_name=k,
                    metric_value=v,
                    source="BRAIN_PLATFORM",
                )
            )
        dec3 = Decision(
            candidate_id=c3.id,
            decision="NEEDS_REVISION",
            reason="6 PASS / 1 FAIL. Sharpe 1.40, Turnover 12.31%, Sub-universe 0.66 passed cleanly with ZERO self-correlation breach! Fitness 0.95 narrowly missed 1.00 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 45 recorded successfully in PostgreSQL.")
