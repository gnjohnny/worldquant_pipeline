"""Parser for WorldQuant BRAIN platform backtest simulation output."""
import re
from dataclasses import dataclass


@dataclass
class ParsedSimulationMetrics:
    """Structured metrics parsed from WorldQuant BRAIN platform text."""

    sharpe: float | None = None
    fitness: float | None = None
    turnover: float | None = None
    sub_universe_sharpe: float | None = None
    self_correlation: float | None = None
    drawdown: float | None = None
    pass_count: int | None = None
    fail_count: int | None = None
    weight_well_distributed: bool = True
    sub_universe_sharpe_passed: bool = True
    self_correlation_passed: bool = True
    raw_text: str = ""

    def to_metric_dict(self) -> dict[str, float]:
        """Convert available metrics to dictionary for database insertion."""
        d: dict[str, float] = {}
        if self.sharpe is not None:
            d["sharpe"] = self.sharpe
        if self.fitness is not None:
            d["fitness"] = self.fitness
        if self.turnover is not None:
            d["turnover"] = self.turnover
        if self.sub_universe_sharpe is not None:
            d["sub_universe_sharpe"] = self.sub_universe_sharpe
        if self.self_correlation is not None:
            d["self_correlation"] = self.self_correlation
        if self.drawdown is not None:
            d["drawdown"] = self.drawdown
        return d


def parse_brain_paste(raw_text: str) -> ParsedSimulationMetrics:
    """Parse raw text pasted from WorldQuant BRAIN backtest card into structured metrics."""
    result = ParsedSimulationMetrics(raw_text=raw_text)

    # Strip markdown links [Text](url) to bare Text for robust regex matching
    cleaned_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw_text)

    # 1. Pass / Fail count
    pass_m = re.search(r"(\d+)\s+PASS", cleaned_text, re.IGNORECASE)
    if pass_m:
        result.pass_count = int(pass_m.group(1))

    fail_m = re.search(r"(\d+)\s+FAIL", cleaned_text, re.IGNORECASE)
    if fail_m:
        result.fail_count = int(fail_m.group(1))

    # 2. Sub-universe Sharpe (must check before overall Sharpe to avoid false positive)
    sub_sharpe_m = re.search(
        r"(?i)sub-?universe\s+sharpe\s+(?:of\s+|:\s*|\=\s*)?(-?\d+(?:\.\d+)?)",
        cleaned_text,
    )
    if sub_sharpe_m:
        result.sub_universe_sharpe = float(sub_sharpe_m.group(1))
        if re.search(r"(?i)sub-?universe\s+sharpe.*below\s+cutoff", cleaned_text):
            result.sub_universe_sharpe_passed = False

    # 3. Overall Sharpe
    # Negative lookbehinds prevent matching "sub-universe sharpe" or "subuniverse sharpe"
    sharpe_m = re.search(
        r"(?i)(?<!sub-universe\s)(?<!subuniverse\s)\bsharpe\s+(?:of\s+|:\s*|\=\s*)?(-?\d+(?:\.\d+)?)",
        cleaned_text,
    )
    if sharpe_m:
        result.sharpe = float(sharpe_m.group(1))

    # 4. Fitness
    fitness_m = re.search(
        r"(?i)\bfitness\s+(?:of\s+|:\s*|\=\s*)?(-?\d+(?:\.\d+)?)",
        cleaned_text,
    )
    if fitness_m:
        result.fitness = float(fitness_m.group(1))

    # 5. Turnover (handles percentage like "14.48%" or decimals like "0.1448")
    turnover_pct_m = re.search(
        r"(?i)\bturnover\s+(?:of\s+|:\s*|\=\s*)?(\d+(?:\.\d+)?)\s*%",
        cleaned_text,
    )
    if turnover_pct_m:
        result.turnover = float(turnover_pct_m.group(1)) / 100.0
    else:
        turnover_dec_m = re.search(
            r"(?i)\bturnover\s+(?:of\s+|:\s*|\=\s*)?(0\.\d+)",
            cleaned_text,
        )
        if turnover_dec_m:
            result.turnover = float(turnover_dec_m.group(1))

    # 6. Self-correlation
    self_corr_m = re.search(
        r"(?i)self-?correlation\s+(?:is\s+|of\s+|:\s*|\=\s*)?([0-9.]+)",
        cleaned_text,
    )
    if self_corr_m:
        result.self_correlation = float(self_corr_m.group(1))
        if re.search(r"(?i)self-?correlation.*above cutoff.*and Sharpe not better", cleaned_text):
            result.self_correlation_passed = False
        elif re.search(r"(?i)or Sharpe is better by 10\.0% or more", cleaned_text):
            result.self_correlation_passed = True
        elif result.self_correlation >= 0.35:
            result.self_correlation_passed = False

    # 7. Max Drawdown
    dd_pct_m = re.search(
        r"(?i)(?:max\s+)?drawdown\s+(?:of\s+|:\s*|\=\s*)?(\d+(?:\.\d+)?)\s*%",
        cleaned_text,
    )
    if dd_pct_m:
        result.drawdown = float(dd_pct_m.group(1)) / 100.0

    # 8. Weight concentration flags
    if re.search(r"(?i)weight\s+concentration|too\s+strongly\s+concentrated", cleaned_text):
        result.weight_well_distributed = False

    return result


def evaluate_consultant_track_decision(
    metrics: ParsedSimulationMetrics,
) -> tuple[str, str]:
    """Evaluate candidate metrics against Platform Submission Invariants.

    Submission Invariants:
    1. Fitness > 1.55 (Strict rule: only alphas with Fitness > 1.55 can be submitted).
    2. Sharpe >= 1.25.
    3. Turnover in [0.01, 0.70].
    4. Sub-universe Sharpe >= 0.0.
    5. Self-correlation < 0.35 (Strict rule: only alphas with Self-correlation < 0.35 can be submitted).
    """
    reasons: list[str] = []
    is_approved = True

    if metrics.sharpe is None or metrics.sharpe < 1.25:
        is_approved = False
        reasons.append(f"Sharpe {metrics.sharpe} < 1.25 cutoff")

    if metrics.fitness is None or metrics.fitness <= 1.55:
        is_approved = False
        reasons.append(f"Fitness {metrics.fitness} <= 1.55 cutoff (Submission Rule: Fitness > 1.55)")

    if metrics.turnover is not None and (metrics.turnover < 0.01 or metrics.turnover > 0.70):
        is_approved = False
        reasons.append(f"Turnover {metrics.turnover:.2%} outside [1%, 70%] bounds")

    if not metrics.sub_universe_sharpe_passed:
        is_approved = False
        reasons.append(f"Sub-universe Sharpe {metrics.sub_universe_sharpe} below platform cutoff")
    elif metrics.sub_universe_sharpe is not None and metrics.sub_universe_sharpe < 0.0:
        is_approved = False
        reasons.append(f"Sub-universe Sharpe {metrics.sub_universe_sharpe} < 0.0")

    if metrics.self_correlation is not None and (metrics.self_correlation >= 0.35 or not metrics.self_correlation_passed):
        is_approved = False
        reasons.append(f"Self-correlation {metrics.self_correlation} >= 0.35 collision threshold (Submission Rule: Self-correlation < 0.35)")

    if not metrics.weight_well_distributed:
        is_approved = False
        reasons.append("Weight concentration detected")

    if is_approved:
        decision = "APPROVED"
        full_reason = (
            f"8/8 PASS! SUBMISSION QUALIFIED: Sharpe {metrics.sharpe} >= 1.25, "
            f"Fitness {metrics.fitness} > 1.55, Turnover {metrics.turnover:.2%}, "
            f"Sub-universe Sharpe {metrics.sub_universe_sharpe}."
        )
        if metrics.self_correlation is not None:
            full_reason += f" Self-correlation {metrics.self_correlation} < 0.35 (Clean pass)."
    else:
        # If platform hard checks failed (self-correlation >= 0.35, turnover, weight, sharpe, or fitness <= 1.55), it is strictly REJECTED
        hard_fail = (
            (metrics.self_correlation is not None and (metrics.self_correlation >= 0.35 or not metrics.self_correlation_passed))
            or (metrics.turnover is not None and (metrics.turnover < 0.01 or metrics.turnover > 0.70))
            or (not metrics.weight_well_distributed)
            or (metrics.sharpe is not None and metrics.sharpe < 1.25)
            or (metrics.fitness is not None and metrics.fitness <= 1.55)
        )
        if not hard_fail and metrics.fitness is not None and metrics.fitness > 1.55:
            # Passed submission gates (Fitness > 1.55, Self-correlation < 0.35)
            decision = "NEEDS_REVIEW"
        else:
            decision = "REJECTED"
        full_reason = "; ".join(reasons)

    return decision, full_reason
