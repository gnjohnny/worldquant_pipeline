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
    # 1. Candidate 1: 4726c896 (Quadratic Conviction Forward EPS Yield)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("4726c896")).first()
    if c1:
        exp1 = Experiment(
            candidate_id=c1.id,
            status="COMPLETED",
            universe="TOP1000",
            delay=1,
            decay=5,
            neutralization="Subindustry",
            truncation=0.0100,
        )
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.95,
            "fitness": 1.46,
            "turnover": 0.2150,
            "sub_universe_sharpe": 1.29,
            "self_correlation": 0.976,
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
            reason="7 PASS / 1 FAIL. Outstanding Sharpe 1.95, Fitness 1.46 ('GOOD' rating), Sub-universe Sharpe 1.29, Turnover 21.50%. Failed only self-correlation (0.976 vs 0.70 cutoff with Alpha 10) because it uses anl4_afv4_eps_mean. Needs >10% Sharpe boost (>=2.16) or decorrelation.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"
        print(f"Recorded Candidate 1 ({c1.id[:8]}) as NEEDS_REVISION.")

    # 2. Candidate 2: 969fde42 (Cashflow Efficiency Power Engine)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("969fde42")).first()
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
            "sharpe": 0.15,
            "fitness": 0.04,
            "turnover": 0.2493,
            "sub_universe_sharpe": 0.11,
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
            reason="5 PASS / 2 FAIL. Low Sharpe 0.15 and Fitness 0.04. Pure rank derivative lacks sufficient signal-to-noise ratio in standalone form.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "REJECTED"
        print(f"Recorded Candidate 2 ({c2.id[:8]}) as REJECTED.")

    # 3. Candidate 3: c2186f76 (Put Breakeven Support Floor)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("c2186f76")).first()
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
            "sharpe": -0.04,
            "fitness": -0.0,
            "turnover": 0.3020,
            "sub_universe_sharpe": 0.19,
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
            reason="4 PASS / 3 FAIL. Negative Sharpe -0.04, Fitness -0.0, and failed weight concentration. Put breakeven with signed_power concentrated weights excessively.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "REJECTED"
        print(f"Recorded Candidate 3 ({c3.id[:8]}) as REJECTED.")

    session.commit()
    print("Batch 32 metrics and decisions successfully committed to PostgreSQL research memory!")
