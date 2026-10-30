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
    c = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("a9482cb9")).first()
    if not c:
        print("Candidate a9482cb9 not found!")
        sys.exit(1)

    exp = Experiment(
        candidate_id=c.id,
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
        "sharpe": 1.84,
        "fitness": 1.58,
        "turnover": 0.2448,
        "sub_universe_sharpe": 1.55,
        "self_correlation": 0.7766,
    }
    for k, v in metrics.items():
        session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

    dec = Decision(
        candidate_id=c.id,
        decision="REJECTED",
        reason="7 PASS / 1 FAIL: Sharpe 1.84, Fitness 1.58, Turnover 24.48%, Sub-universe Sharpe 1.55. FAILED Gate G6 on Self-correlation (0.7766 > 0.70 cutoff against Alpha 19). Needs scope/universe or structural decorrelation.",
        reviewer="HUMAN_RESEARCHER",
    )
    session.add(dec)
    c.status = "REJECTED"

    session.commit()
    print("Candidate a9482cb9 recorded as REJECTED in PostgreSQL.")
