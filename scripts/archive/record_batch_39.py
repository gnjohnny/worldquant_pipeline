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
    # 1. Candidate 1: 49869fd7 (LEAP Call Volatility Compound)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("49869fd7")).first()
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
            "sharpe": 2.26,
            "fitness": 1.54,
            "turnover": 0.2292,
            "sub_universe_sharpe": 1.75,
            "self_correlation": 0.9051,
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
            reason="7 PASS / 1 FAIL. Spectacular performance: Sharpe 2.26, Fitness 1.54 ('GOOD' rating), Sub-universe Sharpe 1.75. Failed self-correlation 0.9051 against ff15b378 (Sharpe 2.16); needs Sharpe >= 2.38 to clear +10% improvement hurdle.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as NEEDS_REVISION.")

    # 2. Candidate 2: 7f0ae98f (EBITDA Yield Compound Elevation - Alpha 13)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7f0ae98f")).first()
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
            "sharpe": 1.87,
            "fitness": 1.32,
            "turnover": 0.2225,
            "sub_universe_sharpe": 1.69,
            "self_correlation": 0.6969,
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
            reason="8/8 PASS! Stellar performance: Sharpe 1.87 > 1.25, Fitness 1.32 > 1.00, Turnover 22.25%, Sub-universe Sharpe 1.69 > 0.99, Self-correlation 0.6969 < 0.70 cutoff. Approved as Alpha 13!",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as APPROVED (Alpha 13)!")

    # 3. Candidate 3: 63ca8c32 (Crown Jewel ff15b378 Replica)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("63ca8c32")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 2.09,
            "fitness": 1.48,
            "turnover": 0.2612,
            "sub_universe_sharpe": 1.69,
            "self_correlation": 0.9480,
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
            reason="7 PASS / 1 FAIL. Sharpe 2.09, Fitness 1.48. Failed self-correlation 0.9480 against ff15b378.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 39 metrics and decisions successfully committed to PostgreSQL research memory!")
