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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("dfc08630")).first()
    if not c:
        print("Candidate dfc08630 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOP3000",
        delay=1,
        decay=6,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.86,
        "fitness": 1.53,
        "turnover": 0.1043,
        "sub_universe_sharpe": 1.64,
        "self_correlation": 0.6025,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.86 > 1.25, Fitness 1.53 >= 1.50, Turnover 10.43% in [1%, 70%], Sub-universe Sharpe 1.64 > 0.81, Self-correlation 0.6025 << 0.70. Audited annual 10-K FX translation hedging + market-wide 1-year call volatility Super Alpha.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("SUCCESS: Candidate dfc08630 officially APPROVED as Gold Level Consultant Alpha!")
    print(f"Candidate ID: {c.id}")
    print(f"Expression: {c.expression_raw}")
