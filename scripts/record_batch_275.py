"""Record simulation results and decisions for Batch 275 in PostgreSQL."""
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
    decay: int = 4,
    truncation: float = 0.01,
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
        "cc9f07aa",
        {
            "sharpe": 0.01,
            "fitness": 0.0,
            "turnover": 0.0729,
            "sub_universe_sharpe": -0.04,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="4 PASS / 3 FAIL. Sharpe 0.01 is below cutoff of 1.25. Fitness 0.0 is below cutoff of 1.0. Sub-universe Sharpe -0.04 is below 0. Incompatible unit warning.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "0aaa6e1d",
        {
            "sharpe": 0.67,
            "fitness": 0.18,
            "turnover": 0.3238,
            "sub_universe_sharpe": 0.19,
            "passes": 3,
            "fails": 4,
        },
        decision_str="REJECTED",
        reason="3 PASS / 4 FAIL. Sharpe 0.67 is below cutoff of 1.25. Fitness 0.18 is below cutoff of 1.0. Weight concentration 15.38% > 10% on 1/25/2022. Incompatible unit warning.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "e4dd0dfe",
        {
            "sharpe": 0.43,
            "fitness": 0.13,
            "turnover": 0.1174,
            "sub_universe_sharpe": 0.02,
            "passes": 3,
            "fails": 4,
        },
        decision_str="REJECTED",
        reason="3 PASS / 4 FAIL. Sharpe 0.43 is below cutoff of 1.25. Fitness 0.13 is below cutoff of 1.0. Weight is too strongly concentrated or too few instruments assigned weight due to NaN addition.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )
