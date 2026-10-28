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
    # 1. Candidate 1: 21d49ff7 (Correlation Reversal)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("21d49ff7")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="FAILED",
            universe="TOP1000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="Platform syntax rejection reported during execution.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 2071b269 (52-week high rank)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2071b269")).first()
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
            "sharpe": -0.44,
            "fitness": -0.26,
            "turnover": 0.1254,
            "sub_universe_sharpe": -0.31,
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
            reason="4 PASS / 3 FAIL. Negative Sharpe -0.44, Fitness -0.26. Pure price percentile rank over 252d lacks predictive edge.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: 11610534 (Dividend Yield)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("11610534")).first()
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
            "sharpe": 0.86,
            "fitness": 0.46,
            "turnover": 0.1038,
            "sub_universe_sharpe": 0.79,
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
            reason="5 PASS / 2 FAIL. Positive Sharpe 0.86 and low turnover 10.38%, but below 1.25 Sharpe cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 36 metrics and decisions successfully committed to PostgreSQL research memory!")
