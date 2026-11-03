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
    # 1. Candidate 1: 50f24c6e (Forward EPS Yield + 15% Reversal Blend) - Alpha 10
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("50f24c6e")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.96,
            "fitness": 1.53,
            "turnover": 0.1672,
            "sub_universe_sharpe": 1.27,
            "self_correlation": 0.6881,
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
            decision="APPROVED",
            reason="8/8 PASS. Exceptional performance: Sharpe 1.96, Fitness 1.53 ('GOOD' Rating), Turnover 16.72%, Sub-universe Sharpe 1.27, Self-correlation 0.6881 (<0.70 cutoff). Approved as Alpha 10.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "APPROVED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as APPROVED (Alpha 10)!")

    # 2. Candidate 2: 8b9f2667 (180-Day Semi-Annual Forward EPS Yield Trajectory) - Alpha 11
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("8b9f2667")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.92,
            "fitness": 1.54,
            "turnover": 0.1394,
            "sub_universe_sharpe": 1.23,
            "self_correlation": 0.7304,
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
            decision="APPROVED",
            reason="8/8 PASS. Outstanding performance: Sharpe 1.92, Fitness 1.54 ('GOOD' Rating), Turnover 13.94%, Sub-universe Sharpe 1.23. Passed self-correlation via >10% Sharpe improvement rule over Alpha 9 (1.92 vs 1.74*1.10=1.914). Approved as Alpha 11.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as APPROVED (Alpha 11)!")

    session.commit()
    print("Both winning alphas committed into PostgreSQL research memory successfully!")
