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
    # 1. Candidate 1: 39d42c74 (Consensus Net Income Yield in TOPSP500)
    c1 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("39d42c74")).first()
    if c1:
        exp1 = Experiment(candidate_id=c1.id, status="COMPLETED")
        session.add(exp1)
        session.flush()
        m1 = {
            "sharpe": 1.20,
            "fitness": 1.13,
            "turnover": 0.0933,
            "sub_universe_sharpe": 1.19,
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
            reason="Achieved 6 PASS, Fitness 1.13, Turnover 9.33%, Sub-universe Sharpe 1.19, missed Sharpe cutoff 1.25 by only 0.05 (Sharpe 1.20).",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec1)
        c1.status = "NEEDS_REVISION"

    # 2. Candidate 2: 5de1fbd0 (Asset Fair Value to Market Cap Yield in TOP1000)
    c2 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("5de1fbd0")).first()
    if c2:
        exp2 = Experiment(candidate_id=c2.id, status="COMPLETED")
        session.add(exp2)
        session.flush()
        m2 = {
            "sharpe": 0.71,
            "fitness": 0.46,
            "turnover": 0.1167,
            "sub_universe_sharpe": 0.58,
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
            reason="Achieved 5 PASS, Turnover 11.67%, Sub-universe Sharpe 0.58 (PASS), but Sharpe 0.71 and Fitness 0.46.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec2)
        c2.status = "NEEDS_REVISION"

    # 3. Candidate 3: 2c92b947 (Consensus Forward EPS Yield Trajectory)
    c3 = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("2c92b947")).first()
    if c3:
        exp3 = Experiment(candidate_id=c3.id, status="COMPLETED")
        session.add(exp3)
        session.flush()
        m3 = {
            "sharpe": 1.83,
            "fitness": 1.52,
            "turnover": 0.1243,
            "sub_universe_sharpe": 1.18,
            "self_correlation": 0.7301,
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
            reason="Superb alpha: 7 PASS, Sharpe 1.83, Fitness 1.52 ('GOOD'), Turnover 12.43%, Sub-universe Sharpe 1.18. Failed only on Self-correlation (0.7301 vs 0.70 cutoff with Alpha 9). Needs minor decorrelation to pass 8/8.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec3)
        c3.status = "NEEDS_REVISION"

    session.commit()
    print("Batch 28 metrics and decisions successfully recorded into PostgreSQL research memory!")
