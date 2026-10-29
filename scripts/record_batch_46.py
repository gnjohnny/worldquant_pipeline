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
    # 1. Candidate 1: 66eaf9cb (Cash Flow Valuation + FX Hedging Super Alpha)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("66eaf9cb")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP3000",
            delay=1,
            decay=4,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.64,
            "fitness": 1.25,
            "turnover": 0.1686,
            "sub_universe_sharpe": 1.34,
            "self_correlation": 0.7839,
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
            reason="7 PASS / 1 FAIL. Sharpe 1.64, Fitness 1.25, Turnover 16.86% passed, but failed self-correlation at 0.7839 (> 0.70 cutoff).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as REJECTED.")

    # 2. Candidate 2: 06d2acff (Pure 1-Year Average FX Translation in TOP1000)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("06d2acff")).first()
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
            "sharpe": 1.63,
            "fitness": 1.18,
            "turnover": 0.1298,
            "sub_universe_sharpe": 1.37,
            "self_correlation": 0.5602,
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
            reason="8/8 PASS! Full platform quality gates cleared on WorldQuant BRAIN: Sharpe 1.63 > 1.25, Fitness 1.18 > 1.00, Turnover 12.98%, Sub-universe 1.37, Self-correlation 0.5602 (< 0.70 cutoff).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "APPROVED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as APPROVED (8/8 PASS, Alpha 15 candidate).")

    # 3. Candidate 3: 081a78b5 (LEAP Call Options + FX Hedging Super Alpha)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("081a78b5")).first()
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
            "sharpe": 2.05,
            "fitness": 1.39,
            "turnover": 0.2079,
            "sub_universe_sharpe": 1.70,
            "self_correlation": 0.7565,
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
            reason="7 PASS / 1 FAIL. Exceptional Sharpe 2.05, Fitness 1.39, Sub-universe 1.70, but self-correlation 0.7565 narrowly exceeded 0.70 cutoff.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as NEEDS_REVISION.")

    session.commit()
    print("Batch 46 recorded successfully in PostgreSQL.")
