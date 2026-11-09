"""Record simulation results and decisions for Batch 276 in PostgreSQL."""
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
        "5e32b6ed",
        {
            "sharpe": 0.90,
            "fitness": 0.41,
            "turnover": 0.0519,
            "sub_universe_sharpe": 0.79,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 0.90 is below cutoff of 1.25. Fitness 0.41 is below cutoff of 1.0. Turnover 5.19%.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "ae571a0d",
        {
            "sharpe": 0.53,
            "fitness": 0.19,
            "turnover": 0.0642,
            "sub_universe_sharpe": 0.48,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 0.53 is below cutoff of 1.25. Fitness 0.19 is below cutoff of 1.0. Turnover 6.42%.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )

    record_candidate_result(
        "f51f418e",
        {
            "sharpe": 1.10,
            "fitness": 0.56,
            "turnover": 0.0498,
            "sub_universe_sharpe": 0.92,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="5 PASS / 2 FAIL. Sharpe 1.10 is below cutoff of 1.25. Fitness 0.56 is below cutoff of 1.0. Sub-universe Sharpe 0.92 > 0.48. Turnover 4.98%.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=2,
        truncation=0.08,
    )
