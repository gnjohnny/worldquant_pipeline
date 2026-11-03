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
    # 1. Candidate 1: c5cf9ec1 (Smoothed VWAP Divergence)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c5cf9ec1")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.40,
            "fitness": 0.66,
            "turnover": 0.4175,
            "sub_universe_sharpe": 0.80,
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
            reason="6 PASS / 1 FAIL. Sharpe 1.40 > 1.25, but turnover of 41.75% penalizes Fitness to 0.66 (< 1.00 cutoff).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: bc479a99 (Volume-Weighted VWAP Reversal)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("bc479a99")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 1.58,
            "fitness": 0.71,
            "turnover": 0.4721,
            "sub_universe_sharpe": 0.78,
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
            reason="6 PASS / 1 FAIL. Strong Sharpe 1.58, but high turnover 47.21% yields Fitness 0.71.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: 0a08da2b (Smoothed Bollinger Z-Score)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0a08da2b")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=6,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 0.85,
            "fitness": 0.49,
            "turnover": 0.1953,
            "sub_universe_sharpe": 0.57,
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
            reason="5 PASS / 2 FAIL / 1 WARNING. Sharpe 0.85, Fitness 0.49. Unit mismatch in add.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 41 metrics and decisions successfully committed to PostgreSQL research memory!")
