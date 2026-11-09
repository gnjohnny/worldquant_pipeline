"""Record simulation results and decisions for Batch 277 in PostgreSQL."""
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
        "a805ec18",
        {
            "sharpe": 1.35,
            "fitness": 0.75,
            "turnover": 0.1007,
            "sub_universe_sharpe": 0.98,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.35 is above cutoff of 1.25. Turnover 10.07% in sweet spot. Sub-universe Sharpe 0.98 > 0.58. Fitness 0.75 is below approval cutoff.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "f7491a19",
        {
            "sharpe": 1.35,
            "fitness": 0.75,
            "turnover": 0.1021,
            "sub_universe_sharpe": 1.01,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.35 is above cutoff of 1.25. Turnover 10.21% in sweet spot. Sub-universe Sharpe 1.01 > 0.58. Fitness 0.75 is below approval cutoff.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )

    record_candidate_result(
        "a3daa722",
        {
            "sharpe": 1.53,
            "fitness": 0.89,
            "turnover": 0.0963,
            "sub_universe_sharpe": 1.11,
            "passes": 6,
            "fails": 1,
        },
        decision_str="NEEDS_REVISION",
        reason="6 PASS / 1 FAIL. Sharpe 1.53 is above cutoff of 1.25. Sub-universe Sharpe 1.11 is outstanding (> 0.66). Turnover 9.63% in sweet spot. Weight well distributed. Fitness 0.89 is below 1.0.",
        universe="TOP3000",
        neutralization="SUBINDUSTRY",
        decay=4,
        truncation=0.08,
    )
