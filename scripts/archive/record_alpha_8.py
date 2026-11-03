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
    # 1. Primary Approved Alpha 8: 1cb6d821
    cand1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("1cb6d821")).first()
    if cand1:
        exp1 = Experiment(candidate_id=cand1.id, status="COMPLETED")
        session.add(exp1)
        session.flush()

        metrics1 = {
            "sharpe": 1.53,
            "fitness": 1.14,
            "turnover": 0.0919,
            "sub_universe_sharpe": 1.58,
            "self_correlation": 0.2572,
        }
        for k, v in metrics1.items():
            session.add(ExperimentMetric(experiment_id=exp1.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec1 = Decision(
            candidate_id=cand1.id,
            decision="APPROVED",
            reason="Alpha 8: Subindustry Operating Income Yield Valuation Breakout. Cleared all 8 platform gates with Sharpe 1.53, Fitness 1.14, Turnover 9.19%, Sub-universe Sharpe 1.58, and remarkably low self-correlation 0.2572.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        cand1.status = "APPROVED"
        print(f"Recorded and approved Alpha 8: {cand1.id} ({cand1.expression_raw})")

    # 2. Approved Alternative Candidate 2: b63923ac (Backfilled variant)
    cand2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("b63923ac")).first()
    if cand2:
        exp2 = Experiment(candidate_id=cand2.id, status="COMPLETED")
        session.add(exp2)
        session.flush()

        metrics2 = {
            "sharpe": 1.51,
            "fitness": 1.10,
            "turnover": 0.0950,
            "sub_universe_sharpe": 1.61,
            "self_correlation": 0.3604,
        }
        for k, v in metrics2.items():
            session.add(ExperimentMetric(experiment_id=exp2.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec2 = Decision(
            candidate_id=cand2.id,
            decision="APPROVED",
            reason="Approved Alternative: Quarterly backfilled operating income yield with subindustry neutralization. Cleared all 8 platform gates with Sharpe 1.51, Fitness 1.10, Turnover 9.50%, Sub-universe Sharpe 1.61, Self-correlation 0.3604.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        cand2.status = "APPROVED"
        print(f"Recorded and approved alternative: {cand2.id} ({cand2.expression_raw})")

    # 3. Approved Alternative Candidate 3: 842e8fd2 (Raw ts_rank variant)
    cand3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("842e8fd2")).first()
    if cand3:
        exp3 = Experiment(candidate_id=cand3.id, status="COMPLETED")
        session.add(exp3)
        session.flush()

        metrics3 = {
            "sharpe": 1.34,
            "fitness": 1.01,
            "turnover": 0.0734,
            "sub_universe_sharpe": 1.60,
            "self_correlation": 0.2728,
        }
        for k, v in metrics3.items():
            session.add(ExperimentMetric(experiment_id=exp3.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec3 = Decision(
            candidate_id=cand3.id,
            decision="APPROVED",
            reason="Approved Baseline: Raw time-series operating income yield. Cleared all 8 platform gates with Sharpe 1.34, Fitness 1.01, Turnover 7.34%, Sub-universe Sharpe 1.60, Self-correlation 0.2728.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        cand3.status = "APPROVED"
        print(f"Recorded and approved baseline: {cand3.id} ({cand3.expression_raw})")

    session.commit()
    print("Database commit successful!")
