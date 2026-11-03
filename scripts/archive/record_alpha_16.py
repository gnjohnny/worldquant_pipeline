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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("7c3e864f")).first()
    if not c:
        print("Candidate 7c3e864f not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOP1000",
        delay=1,
        decay=6,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.77,
        "fitness": 2.02,
        "turnover": 0.1640,
        "sub_universe_sharpe": 1.58,
        "self_correlation": 0.6159,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! EXCELLENT Platform Rating: Sharpe 1.77 > 1.25, Fitness 2.02 >= 1.80 (EXCELLENT), Turnover 16.40% in [1%, 70%], Sub-universe Sharpe 1.58 > 0.94, Self-correlation 0.6159 << 0.70. Market-neutralized 1-Year Call Volatility Risk Premia.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("SUCCESS: Candidate 7c3e864f officially APPROVED as Gold Level EXCELLENT Alpha!")
    print(f"Candidate ID: {c.id}")
    print(f"Expression: {c.expression_raw}")
