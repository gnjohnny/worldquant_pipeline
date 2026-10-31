"""Record Alpha 28 (Candidate 12ab1834) TOP3000 Decay 4 simulation run in PostgreSQL."""
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
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("12ab1834")).first()
    if not cand:
        print("Candidate 12ab1834 not found!")
        sys.exit(1)

    # Add Experiment 2 for this candidate (TOP3000, Decay 4)
    exp = Experiment(
        candidate_id=cand.id,
        status="COMPLETED",
        universe="TOP3000",
        delay=1,
        decay=4,
        neutralization="Market",
        truncation=0.0100,
    )
    session.add(exp)
    session.flush()

    metrics = {
        "sharpe": 2.11,
        "fitness": 2.03,
        "turnover": 0.1899,
        "sub_universe_sharpe": 1.85,
        "self_correlation": 0.9171,
    }
    for k, v in metrics.items():
        session.add(
            ExperimentMetric(
                experiment_id=exp.id,
                metric_name=k,
                metric_value=v,
                source="BRAIN_PLATFORM",
            )
        )

    # Log updated decision notes
    dec = Decision(
        candidate_id=cand.id,
        decision="APPROVED",
        reason=(
            "8/8 PASS! SPECTACULAR EXPANSION in TOP3000 Decay 4: "
            "Sharpe 2.11 >= 1.25 (SPECTACULAR > 2.10 hurdle!), Fitness 2.03 >= 1.50 (EXCELLENT), "
            "Turnover 18.99% in [1%, 70%], Sub-universe Sharpe 1.85 (exceptional breadth), "
            "Self-correlation 0.9171 passed via 10%+ Sharpe superiority rule. "
            "This confirms Alpha 28 as an elite multi-universe flagship alpha."
        ),
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    session.commit()
    print("Candidate 12ab1834 TOP3000 Decay 4 experiment logged successfully in PostgreSQL.")
