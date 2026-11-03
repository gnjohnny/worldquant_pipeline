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
    # 1. Candidate 1: 7495ec23 (90-Day Quarterly Forward EPS Upgrade Acceleration)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7495ec23")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.84,
            "fitness": 1.27,
            "turnover": 0.2109,
            "sub_universe_sharpe": 1.05,
            "self_correlation": 0.9168,
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
            decision="NEEDS_REVISION",
            reason="7 PASS / 1 FAIL. Exceptional Sharpe 1.84, Fitness 1.27 ('GOOD' rating), Sub-universe Sharpe 1.05, Turnover 21.09%. Failed self-correlation (0.9168 vs 0.70 cutoff with Alpha 10) because both trade forward EPS revisions. Needs further decorrelation or Sharpe >= 2.16.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as NEEDS_REVISION.")

    # 2. Candidate 2: 73e2e269 (1-Year Forward Cash Flow Per Share Yield)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("73e2e269")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.04,
            "fitness": 0.65,
            "turnover": 0.1606,
            "sub_universe_sharpe": 0.90,
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
            reason="5 PASS / 2 FAIL. Sharpe 1.04 and Fitness 0.65 fail to meet BRAIN production thresholds of 1.25 and 1.00 respectively. Cash flow per share yield alone has insufficient signal-to-noise ratio.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: a05aa8cb (Bounded Options Variance Risk Premium (VRP) Ratio)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("a05aa8cb")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 0.04,
            "fitness": 0.00,
            "turnover": 0.2476,
            "sub_universe_sharpe": -0.04,
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
            decision="REJECTED",
            reason="3 PASS / 4 FAIL / 1 WARNING. Sharpe 0.04, Fitness 0.0, weight concentration failed, and Sub-universe Sharpe -0.04. Dimensionless options VRP ratio lacks predictive power across liquid equities.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 33 metrics and decisions successfully committed to PostgreSQL research memory!")
