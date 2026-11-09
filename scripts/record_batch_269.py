"""Record simulation results and decisions for Batch 269 in PostgreSQL."""
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
    universe: str = "TOP3000",
    neutralization: str = "SUBINDUSTRY",
    decay: int = 4,
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

    sharpe = metrics_dict.get("sharpe", 0.0) or 0.0
    fitness = metrics_dict.get("fitness", 0.0) or 0.0
    fails = metrics_dict.get("fails", 0)

    decision_str = "REJECTED"
    reason = f"Failed platform criteria: {fails} FAIL. Sharpe {sharpe}, Fitness {fitness}, Turnover {metrics_dict.get('turnover')*100:.2f}%. Static ratio sluggishness without time-series ranking."

    cand.status = decision_str
    session.add(Decision(candidate_id=cand.id, decision=decision_str, reason=reason))
    session.commit()
    print(f"Recorded {cand.id[:8]}: {decision_str} - {reason}")
    session.close()


if __name__ == "__main__":
    record_candidate_result(
        "5aeb6d50",
        {
            "sharpe": -0.34,
            "fitness": -0.13,
            "turnover": 0.0197,
            "sub_universe_sharpe": -0.10,
            "passes": 5,
            "fails": 2,
        },
    )
    record_candidate_result(
        "36f0b65d",
        {
            "sharpe": -0.27,
            "fitness": -0.07,
            "turnover": 0.0264,
            "sub_universe_sharpe": -0.41,
            "passes": 4,
            "fails": 3,
        },
    )
    record_candidate_result(
        "a33766ad",
        {
            "sharpe": -0.12,
            "fitness": -0.03,
            "turnover": 0.0100,
            "sub_universe_sharpe": -0.13,
            "passes": 4,
            "fails": 3,
        },
    )
