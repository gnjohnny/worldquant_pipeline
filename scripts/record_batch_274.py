"""Record simulation results and decisions for Batch 274 in PostgreSQL."""
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
        "071199b5",
        {},
        decision_str="NEEDS_REVISION",
        reason="Platform Error: Operator ts_backfill does not support event inputs (anl4_ady_pu, anl4_ady_down, anl4_ady_numest are event fields).",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "2ec45a78",
        {
            "sharpe": -0.11,
            "fitness": -0.01,
            "turnover": 0.3599,
            "sub_universe_sharpe": 0.49,
            "passes": 4,
            "fails": 3,
        },
        decision_str="REJECTED",
        reason="4 PASS / 3 FAIL. Sharpe -0.11 is below cutoff of 1.25. Fitness -0.01 is below cutoff of 1.0. Weight is too strongly concentrated.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )

    record_candidate_result(
        "838446fe",
        {
            "sharpe": 1.35,
            "fitness": 0.74,
            "turnover": 0.0535,
            "sub_universe_sharpe": 0.99,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.35 is above cutoff of 1.25. Turnover 5.35% is well-behaved. Weight well distributed. Sub-universe Sharpe 0.99 > 0.58. Fitness 0.74 is below Gold Level approval cutoff of 1.50.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
    )
