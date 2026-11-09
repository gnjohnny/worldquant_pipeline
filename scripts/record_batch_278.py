"""Record simulation results and decisions for Batch 278 in PostgreSQL."""
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def record_candidate_result(
    candidate_id_prefix: str,
    metrics_dict: dict,
    decision_str: str,
    reason: str,
    universe: str = "TOP3000",
    neutralization: str = "SUBINDUSTRY",
    decay: int = 2,
    truncation: float = 0.08,
):
    session = get_session()
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.like(f"{candidate_id_prefix}%")).first()
    if not cand:
        print(f"Candidate {candidate_id_prefix} not found in database.")
        session.close()
        return

    exp = Experiment(
        candidate_id=cand.id,
        universe=universe,
        neutralization=neutralization,
        decay=decay,
        truncation=truncation,
    )
    session.add(exp)
    session.flush()

    for k, v in metrics_dict.items():
        if v is not None and k not in ("passes", "fails"):
            session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v))

    cand.status = decision_str
    dec = Decision(
        candidate_id=cand.id,
        decision=decision_str,
        reason=reason,
    )
    session.add(dec)
    session.commit()
    print(f"Recorded candidate {candidate_id_prefix}: {decision_str}")
    session.close()


if __name__ == "__main__":
    record_candidate_result(
        "44cabfca",
        {
            "sharpe": 1.79,
            "fitness": 0.89,
            "turnover": 0.2062,
            "sub_universe_sharpe": 1.36,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.79 is well above cutoff. Turnover 20.62%. Sub-universe Sharpe 1.36. Fitness 0.89 is below 1.0.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "ce6ea1b6",
        {
            "sharpe": 1.92,
            "fitness": 1.06,
            "turnover": 0.1851,
            "sub_universe_sharpe": 1.52,
            "self_correlation": 0.4198,
            "passes": 8,
            "fails": 0,
        },
        decision_str="NEEDS_REVIEW",
        reason="8 PASS / 0 FAIL! FULL PLATFORM PASS! Sharpe 1.92, Fitness 1.06 > 1.0, Turnover 18.51%, Sub-universe Sharpe 1.52, Self-correlation 0.4198 (exceptionally low, well below 0.70 cutoff). Meets all BRAIN submission criteria. Gold Level status: NEEDS_REVIEW (target >= 1.50).",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "f983d1af",
        {
            "sharpe": 1.64,
            "fitness": 0.82,
            "turnover": 0.1933,
            "sub_universe_sharpe": 1.28,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.64, Turnover 19.33%, Sub-universe Sharpe 1.28, Fitness 0.82.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )
