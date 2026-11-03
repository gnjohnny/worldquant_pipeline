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
    # 1. Candidate 1: 44a887c8 (1-Year Trailing Average FX Translation Yield)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("44a887c8")).first()
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
            "sharpe": 1.08,
            "fitness": 0.64,
            "turnover": 0.1300,
            "sub_universe_sharpe": 0.62,
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
            reason="5 PASS / 2 FAIL / 1 WARNING. Sharpe 1.08 and Fitness 0.64 below cutoffs. Unit mismatch warning on (cap + 1000).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 7e874606 (1-Year TS Rank Asset-Normalized FX)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7e874606")).first()
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
            "sharpe": 1.47,
            "fitness": 0.92,
            "turnover": 0.1479,
            "sub_universe_sharpe": 1.33,
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
            reason="6 PASS / 1 FAIL. Sharpe 1.47 and Sub-universe 1.33 passed strongly, but Fitness 0.92 fell slightly below 1.00 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as NEEDS_REVISION.")

    # 3. Candidate 3: 06d2acff (4-Quarter Rolling Average FX Translation)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("06d2acff")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 1.51,
            "fitness": 1.07,
            "turnover": 0.1302,
            "sub_universe_sharpe": 1.31,
            "self_correlation": 0.7407,
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
            reason="7 PASS / 1 FAIL. Sharpe 1.51, Fitness 1.07, Turnover 13.02%, Sub-universe 1.31 all passed! Failed self-correlation at 0.7407 (> 0.70 cutoff). Requires Sharpe >= 1.82 to override or decorrelation.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 44 recorded successfully in PostgreSQL.")
