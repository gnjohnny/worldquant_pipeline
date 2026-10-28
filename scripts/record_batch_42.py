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
    # 1. Candidate 1: a04cde80 (Sales Yield)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("a04cde80")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.01,
            "fitness": 0.62,
            "turnover": 0.2279,
            "sub_universe_sharpe": 0.55,
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
            reason="5 PASS / 2 FAIL. Sharpe 1.01 and Fitness 0.62 below platform cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 3b19f77f (Parkinson LEAP Call Compound)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("3b19f77f")).first()
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
            "sharpe": 2.37,
            "fitness": 1.65,
            "turnover": 0.2436,
            "sub_universe_sharpe": 1.83,
            "self_correlation": 0.8074,
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
            reason="7 PASS / 1 FAIL. Incredible performance: Sharpe 2.37, Fitness 1.65 ('GOOD'/'EXCELLENT' rating), Sub-universe Sharpe 1.83. Failed self-correlation by just 0.006 Sharpe points (needed >= 2.376 to clear +10% hurdle over ff15b378).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 42 metrics and decisions successfully committed to PostgreSQL research memory!")
