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
    # 1. Candidate 1: c88a5b5e (pv13_custretsig_retsig)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c88a5b5e")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": -1.48,
            "fitness": -0.76,
            "turnover": 0.4107,
            "sub_universe_sharpe": -0.96,
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
            reason="4 PASS / 3 FAIL. Sharpe -1.48 and Fitness -0.76. Signal direction is strongly inverted (needs negation) with 41% turnover.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 210ed592 (put_breakeven_30)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("210ed592")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": -0.78,
            "fitness": -0.40,
            "turnover": 0.2153,
            "sub_universe_sharpe": -0.50,
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
            decision="REJECTED",
            reason="3 PASS / 4 FAIL. Sharpe -0.78, Fitness -0.40, weight too concentrated.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: c5f12b8b (correlation)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c5f12b8b")).first()
    if c3:
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="FAILED: Attempted to use inaccessible or unknown operator 'correlation' on BRAIN platform.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED (operator correlation inaccessible).")

    session.commit()
    print("Batch 47 recorded successfully in PostgreSQL.")
