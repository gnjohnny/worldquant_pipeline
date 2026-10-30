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
    # 1. Candidate 1: 8229a0c3 (TOP2000, Market, Decay 5)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("8229a0c3")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=5,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {"sharpe": 1.75, "fitness": 1.57, "turnover": 0.1243, "sub_universe_sharpe": 1.63, "self_correlation": 0.8051}
        for k, v in m1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec1 = Decision(
            candidate_id=c1.id,
            decision="REJECTED",
            reason="7 PASS / 1 FAIL: Sharpe 1.75, Fitness 1.57, Turnover 12.43%, Sub-universe 1.63. FAILED Gate G6 on Self-correlation (0.8051 > 0.70 cutoff against Alpha 23). Needs universe/neutralization shift to TOP1000 Industry.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "REJECTED"
        print("Recorded Candidate 1 (8229a0c3) as REJECTED.")

    # 2. Candidate 2: b6345e1d (TOP2000, Market, Decay 5)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("b6345e1d")).first()
    if c2:
        exp2 = Experiment(
            candidate_id=c2.id,
            status="COMPLETED",
            universe="TOP2000",
            delay=1,
            decay=5,
            neutralization="Market",
            truncation=0.0100,
        )
        session.add(exp2)
        session.flush()
        m2 = {"sharpe": 1.19, "fitness": 1.05, "turnover": 0.1310, "sub_universe_sharpe": 1.03}
        for k, v in m2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec2 = Decision(
            candidate_id=c2.id,
            decision="REJECTED",
            reason="6 PASS / 1 FAIL: Sharpe 1.19 < 1.25 cutoff. Quarterly sales yield insufficient standalone Sharpe in TOP2000 Market neutral.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print("Recorded Candidate 2 (b6345e1d) as REJECTED.")

    # 3. Candidate 3: db3719cd (TOP1000, Industry, Decay 5)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("db3719cd")).first()
    if c3:
        exp3 = Experiment(
            candidate_id=c3.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp3)
        session.flush()
        m3 = {"sharpe": 1.14, "fitness": 0.99, "turnover": 0.1324, "sub_universe_sharpe": 1.16}
        for k, v in m3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec3 = Decision(
            candidate_id=c3.id,
            decision="REJECTED",
            reason="5 PASS / 2 FAIL: Sharpe 1.14 < 1.25, Fitness 0.99 < 1.0. Annual sales yield insufficient standalone Sharpe.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print("Recorded Candidate 3 (db3719cd) as REJECTED.")

    # 4. Candidate 4: 0bc3ff18 (TOP1000, Industry, Decay 5)
    c4 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("0bc3ff18")).first()
    if c4:
        exp4 = Experiment(
            candidate_id=c4.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Industry",
            truncation=0.0100,
        )
        session.add(exp4)
        session.flush()
        m4 = {"sharpe": 1.30, "fitness": 1.06, "turnover": 0.1289, "sub_universe_sharpe": 1.23, "self_correlation": 0.6702}
        for k, v in m4.items():
            session.add(ExperimentMetric(experiment_id=exp4.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))
        dec4 = Decision(
            candidate_id=c4.id,
            decision="NEEDS_REVIEW",
            reason="8/8 PASS on platform! Sharpe 1.30 > 1.25, Turnover 12.89%, Self-corr 0.6702 < 0.70. Placed in NEEDS_REVIEW per Gold Consultant Invariant 1 (Fitness 1.06 < 1.50 threshold for GOOD rating). Candidate for Sharpe/Fitness boost.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec4)
        c4.status = "NEEDS_REVIEW"
        print("Recorded Candidate 4 (0bc3ff18) as NEEDS_REVIEW (passed platform, awaiting Fitness boost).")

    session.commit()
    print("Batch 70 experiments recorded in PostgreSQL.")
