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
    # 1. Candidate 1: 8229a0c3 (TOP1000, Industry, Decay 5)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("8229a0c3")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.61, "fitness": 1.37, "turnover": 0.1296, "sub_universe_sharpe": 1.66, "self_correlation": 0.7186}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.61, Fitness 1.37, Turnover 12.96%, Sub-universe 1.66. Self-correlation 0.7186 slightly exceeds 0.70 cutoff against Alpha 20 (Operating Income in TOP1000 Industry).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (8229a0c3) as REJECTED.")

    # 2. Candidate 2: 1c2c2d86 (TOP1000, Sector, Decay 5)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1c2c2d86")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Sector",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.81, "fitness": 1.81, "turnover": 0.1234, "sub_universe_sharpe": 1.89, "self_correlation": 0.7870}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Exceptional performance (Sharpe 1.81, Fitness 1.81 EXCELLENT, Turnover 12.34%, Sub-universe 1.89). Self-correlation 0.7870 > 0.70 against Alpha 22 (LEAP Call IV in TOP1000 Sector). Needs Subindustry or TOP2000 scope shift.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (1c2c2d86) as REJECTED.")

    # 3. Candidate 3: 0bc3ff18 (TOP2000, Market, Decay 5)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0bc3ff18")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=5,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.15, "fitness": 0.91, "turnover": 0.1266, "sub_universe_sharpe": 1.02}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 1.15 < 1.25, Fitness 0.91 < 1.0. Cash cushion insufficient standalone Sharpe in TOP2000 Market.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (0bc3ff18) as REJECTED.")

    # 4. Candidate 4: 1831b96e (Platform unknown variable)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1831b96e")).first()
    if c4:
        dec4 = Decision(
            candidate_id=c4.id,
            decision="REJECTED",
            reason="G0 Syntax/Data Field Rejection: Platform reported unknown variable actual_dividend_value_qua.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "REJECTED"
        print("Recorded Candidate 4 (1831b96e) as REJECTED.")

    session.commit()
    print("Batch 71 experiments and decisions committed to PostgreSQL.")
