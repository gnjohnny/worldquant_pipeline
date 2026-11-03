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
    # 1. Candidate 1: f8d9aaab (Novy-Marx Operating ROA)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("f8d9aaab")).first()
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
            "sharpe": 0.66,
            "fitness": 0.43,
            "turnover": 0.1539,
            "sub_universe_sharpe": 0.49,
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
            reason="5 PASS / 2 FAIL. Low Sharpe 0.66 and Fitness 0.43. Asset-base normalization lacks cross-sectional dispersion in TOP3000.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 0081b888 (Free Cash Flow Yield)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0081b888")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 0.47,
            "fitness": 0.16,
            "turnover": 0.2066,
            "sub_universe_sharpe": -0.09,
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
            reason="4 PASS / 3 FAIL. Low Sharpe 0.47 and Fitness 0.16. Capex deduction dilutes operating cash flow signal density.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: d911e5ae (LEAP Call 60d Hurdle Breaker)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d911e5ae")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0080,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 1.98,
            "fitness": 1.21,
            "turnover": 0.2673,
            "sub_universe_sharpe": 1.49,
            "self_correlation": 0.8406,
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
            reason="7 PASS / 1 FAIL. Strong Sharpe 1.98, Fitness 1.21. Failed self-correlation 0.8406 against ff15b378; needs Sharpe >= 2.38.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 40 metrics and decisions successfully committed to PostgreSQL research memory!")
