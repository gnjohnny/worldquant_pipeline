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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("db42a322")).first()
    if not c:
        print("Candidate db42a322 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
        status="COMPLETED",
        universe="TOP1000",
        delay=1,
        decay=5,
        neutralization="Industry",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 1.81,
        "fitness": 1.61,
        "turnover": 0.1244,
        "sub_universe_sharpe": 1.96,
        "self_correlation": 0.7598,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="APPROVED",
        reason="8/8 PASS! GOLD LEVEL CONSULTANT QUALIFIED: Sharpe 1.81 > 1.25, Fitness 1.61 >= 1.50 (GOOD), Turnover 12.44% in [1%, 70%], Sub-universe Sharpe 1.96 > 0.96, Self-correlation 0.7598 PASS via platform Sharpe improvement rule. Large-Cap Operating Income Yield & Audited 10-K FX Translation Super Alpha.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "APPROVED"

    session.commit()
    print("Candidate db42a322 successfully APPROVED and recorded as Alpha 20 in PostgreSQL.")
