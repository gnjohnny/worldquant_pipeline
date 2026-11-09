"""Record simulation results and decisions for Batch 270 in PostgreSQL."""
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
        "12edb6b2",
        {
            "turnover": 0.0241,
            "sharpe": -0.09,
            "fitness": -0.03,
            "sub_universe_sharpe": -0.54,
            "weight_concentration": 0.2155,
            "passes": 3,
            "fails": 4,
        },
        decision_str="REJECTED",
        reason="Failed platform criteria: 4 FAIL. Sharpe -0.09, Fitness -0.03, Sub-universe Sharpe -0.54, Weight concentration 21.55%. Model16 style derivative differentials suffer sparse distribution and weight concentration.",
    )

    record_candidate_result(
        "349beb1c",
        {
            "turnover": 0.0163,
            "sharpe": -0.29,
            "fitness": -0.16,
            "sub_universe_sharpe": 0.12,
            "weight_concentration": 0.2781,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="Failed platform criteria: 3 FAIL. Sharpe -0.29, Fitness -0.16, Weight concentration 27.81%. Model16 earnings certainty minus valuation differential creates severe weight concentration.",
    )

    record_candidate_result(
        "56884131",
        {
            "turnover": 0.0726,
            "sharpe": 0.35,
            "fitness": 0.09,
            "sub_universe_sharpe": 0.27,
            "passes": 5,
            "fails": 2,
        },
        decision_str="REJECTED",
        reason="Failed platform criteria: 2 FAIL. Sharpe 0.35 < 1.25, Fitness 0.09 < 1.0. Passed weight distribution and sub-universe Sharpe (0.27), but operating margin delta alone lacks sufficient alpha signal power.",
    )
