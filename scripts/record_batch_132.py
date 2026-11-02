"""Record simulation results and decisions for Batch 132 in PostgreSQL."""
import re
import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    Decision,
    Experiment,
    ExperimentMetric,
)


def parse_brain_paste(text: str):
    """Parse metrics from BRAIN simulation text."""
    sharpe_match = re.search(r"Sharpe\s+(?:of\s+)?([-\d\.]+)", text, re.IGNORECASE)
    fitness_match = re.search(r"Fitness\s+(?:of\s+)?([-\d\.]+)", text, re.IGNORECASE)
    turnover_match = re.search(r"Turnover\s+(?:of\s+)?([\d\.]+)%", text, re.IGNORECASE)
    sub_sharpe_match = re.search(r"Sub-universe Sharpe\s+(?:of\s+)?([-\d\.]+)", text, re.IGNORECASE)
    self_corr_match = re.search(r"Self-correlation\s+(?:is\s+)?([-\d\.]+)", text, re.IGNORECASE)

    sharpe = float(sharpe_match.group(1)) if sharpe_match else None
    fitness = float(fitness_match.group(1)) if fitness_match else None
    turnover = (float(turnover_match.group(1)) / 100.0) if turnover_match else None
    sub_sharpe = float(sub_sharpe_match.group(1)) if sub_sharpe_match else None
    self_corr = float(self_corr_match.group(1)) if self_corr_match else None

    passes = len(re.findall(r"\bPASS\b", text))
    fails = len(re.findall(r"\bFAIL\b", text))

    return {
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "sub_universe_sharpe": sub_sharpe,
        "self_correlation": self_corr,
        "passes": passes,
        "fails": fails,
    }


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

    is_approved = False
    decision_str = "REJECTED"
    reason = ""

    if fails == 0 and fitness >= 1.50 and (self_corr is None or self_corr <= 0.70):
        decision_str = "APPROVED"
        is_approved = True
        reason = f"Passed all platform checks! Sharpe {sharpe:.2f}, Fitness {fitness:.2f} >= 1.50, Self-corr {self_corr}."
    elif fails == 0 and fitness >= 1.00:
        decision_str = "NEEDS_REVIEW"
        reason = f"Passed platform checks (8 PASS / 0 FAIL), Sharpe {sharpe:.2f}, Fitness {fitness:.2f} (< 1.50 Gold standard)."
    else:
        decision_str = "REJECTED"
        reason = f"Failed platform criteria: {fails} FAIL. Sharpe {sharpe}, Fitness {fitness}, Self-corr {self_corr}."

    cand.status = decision_str
    session.add(Decision(candidate_id=cand.id, decision=decision_str, reason=reason))
    session.commit()
    print(f"Recorded {cand.id[:8]}: {decision_str} - {reason}")
    session.close()
    return is_approved


if __name__ == "__main__":
    print("Record Batch 132 Helper Ready.")
