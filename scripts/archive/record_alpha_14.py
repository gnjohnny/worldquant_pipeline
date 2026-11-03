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
    # 1. Candidate 1: b6dec7ef (20% Reversal Tuned)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("b6dec7ef")).first()
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
            "sharpe": 2.35,
            "fitness": 1.60,
            "turnover": 0.2781,
            "sub_universe_sharpe": 1.94,
            "self_correlation": 0.8345,
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
            reason="7 PASS / 1 FAIL. Incredible Sharpe 2.35 and Fitness 1.60. Failed self-correlation 0.8345 by just 0.026 Sharpe points.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as NEEDS_REVISION.")

    # 2. Candidate 2: d1ac34ee (Put Surface Decorrelation)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("d1ac34ee")).first()
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
            "sharpe": 1.68,
            "fitness": 1.03,
            "turnover": 0.2339,
            "sub_universe_sharpe": 1.12,
            "self_correlation": 0.7006,
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
            reason="7 PASS / 1 FAIL. Sharpe 1.68, Fitness 1.03. Self-correlation was 0.7006, missing the 0.70 cutoff by just 0.0006.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as NEEDS_REVISION.")

    # 3. Candidate 3: c2f5c78d (3-Year LEAP Call Term Premium - Alpha 14 Spectacular)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c2f5c78d")).first()
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
            "sharpe": 2.42,
            "fitness": 1.58,
            "turnover": 0.2846,
            "sub_universe_sharpe": 1.85,
            "self_correlation": 0.8214,
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
            decision="APPROVED",
            reason="8/8 PASS! SPECTACULAR PERFORMANCE: Sharpe 2.42 > 1.25, Fitness 1.58 > 1.00, Turnover 28.46%, Sub-universe Sharpe 1.85 > 1.05. Passed self-correlation via >10% Sharpe improvement rule over ff15b378 (2.42 vs 2.16*1.10=2.376). Approved as Alpha 14 Spectacular Crown Jewel!",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "APPROVED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as APPROVED (Alpha 14 SPECTACULAR)!")

    session.commit()
    print("Batch 43 metrics and decisions successfully committed to PostgreSQL research memory!")
