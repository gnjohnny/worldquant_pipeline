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
    # 1. Candidate 1: 2582e96a (EBITDA Yield 180d)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2582e96a")).first()
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
            "sharpe": 1.37,
            "fitness": 0.98,
            "turnover": 0.1422,
            "sub_universe_sharpe": 1.36,
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
            reason="6 PASS / 1 FAIL. Strong Sharpe 1.37, Sub-universe Sharpe 1.36, Turnover 14.22%. Fitness is 0.98, just 0.02 from the 1.00 cutoff. Tuning decay to 5/6 or applying conviction shaping will push Fitness > 1.20.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as NEEDS_REVISION.")

    # 2. Candidate 2: 2bd91a47 (Domestic EBIT)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2bd91a47")).first()
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
            "sharpe": 1.19,
            "fitness": 0.74,
            "turnover": 0.1140,
            "sub_universe_sharpe": 1.10,
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
            reason="5 PASS / 2 FAIL. Sharpe 1.19 and Fitness 0.74 slightly below 1.25 and 1.00 cutoffs.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: 032764a5 (LEAP Call Volatility Premium)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("032764a5")).first()
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
            "sharpe": 1.42,
            "fitness": 0.85,
            "turnover": 0.1619,
            "sub_universe_sharpe": 1.02,
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
            reason="6 PASS / 1 FAIL. Strong Sharpe 1.42, Sub-universe Sharpe 1.02, Turnover 16.19%. Fitness 0.85 needs turnover dampening via decay=6 or power transform to reach >1.20.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 37 metrics and decisions successfully committed to PostgreSQL research memory!")
