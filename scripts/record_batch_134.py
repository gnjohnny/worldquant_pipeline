"""Record simulation results and decisions for Batch 134 in PostgreSQL."""
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
    universe: str = "TOP1000",
    neutralization: str = "SUBINDUSTRY",
    decay: int = 5,
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
    self_corr = metrics_dict.get("self_correlation")
    fails = metrics_dict.get("fails", 0)

    if fails == 0 and fitness >= 1.50 and (self_corr is None or self_corr <= 0.70):
        decision_str = "APPROVED"
        reason = f"Passed all platform checks (8 PASS / 0 FAIL)! Sharpe {sharpe:.2f}, Fitness {fitness:.2f} >= 1.50, Turnover {metrics_dict.get('turnover')*100:.2f}%, Self-corr {self_corr}."
    elif fails == 0 and fitness >= 1.00:
        decision_str = "NEEDS_REVIEW"
        reason = f"Passed platform checks (8 PASS / 0 FAIL), Sharpe {sharpe:.2f}, Fitness {fitness:.2f} (< 1.50 Gold standard), Self-corr {self_corr}."
    else:
        decision_str = "REJECTED"
        reason = f"Failed platform criteria: {fails} FAIL. Sharpe {sharpe}, Fitness {fitness}, Self-corr {self_corr}."

    cand.status = decision_str
    session.add(Decision(candidate_id=cand.id, decision=decision_str, reason=reason))
    session.commit()
    print(f"Recorded {cand.id[:8]}: {decision_str} - {reason}")
    session.close()


if __name__ == "__main__":
    record_candidate_result(
        "38ea838a",
        {
            "sharpe": 1.65,
            "fitness": 1.10,
            "turnover": 0.1531,
            "sub_universe_sharpe": 1.14,
            "self_correlation": 0.4844,
            "passes": 8,
            "fails": 0,
        },
    )
    record_candidate_result(
        "3bb95076",
        {
            "sharpe": -0.11,
            "fitness": -0.03,
            "turnover": 0.0767,
            "sub_universe_sharpe": -0.10,
            "passes": 3,
            "fails": 4,
        },
    )
    record_candidate_result(
        "0c4d2fa0",
        {
            "sharpe": 2.14,
            "fitness": 1.65,
            "turnover": 0.1445,
            "sub_universe_sharpe": 2.00,
            "self_correlation": 0.5738,
            "passes": 8,
            "fails": 0,
        },
    )
