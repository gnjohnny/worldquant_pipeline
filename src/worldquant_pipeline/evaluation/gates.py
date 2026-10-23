"""Quality gates G0–G7 evaluation logic."""
from dataclasses import dataclass, field
from typing import Any

from worldquant_pipeline.config.settings import get_settings


@dataclass
class GateEvaluationResult:
    """Outcome of quality gate evaluation."""
    passed: bool
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    gate_details: dict[str, bool] = field(default_factory=dict)


class QualityGateRunner:
    """Evaluates simulation results against G0–G7 quantitative research gates."""

    def __init__(self, thresholds: dict[str, Any] | None = None) -> None:
        settings = get_settings()
        self.thresholds = thresholds or settings.research_config.get("quality_gates", {
            "min_sharpe": 1.25,
            "min_fitness": 1.00,
            "max_turnover": 0.70,
            "min_turnover": 0.01,
            "max_drawdown": 0.25,
        })

    def evaluate_metrics(self, metrics: dict[str, float]) -> GateEvaluationResult:
        """Evaluate platform simulation metrics against Gate G5 (Robustness & Friction)."""
        warnings: list[str] = []
        failures: list[str] = []
        gate_details: dict[str, bool] = {}

        sharpe = metrics.get("sharpe")
        turnover = metrics.get("turnover")
        fitness = metrics.get("fitness")
        drawdown = metrics.get("drawdown")

        # 1. Gate G5.1: Minimum Sharpe
        min_sharpe = self.thresholds.get("min_sharpe", 1.25)
        if sharpe is not None:
            if sharpe < min_sharpe:
                failures.append(f"Gate G5: Sharpe {sharpe:.2f} is below minimum threshold ({min_sharpe:.2f}).")
                gate_details["G5_min_sharpe"] = False
            else:
                gate_details["G5_min_sharpe"] = True

        # 2. Gate G5.2: Turnover Bounds (Trading Friction)
        max_turnover = self.thresholds.get("max_turnover", 0.70)
        min_turnover = self.thresholds.get("min_turnover", 0.01)
        if turnover is not None:
            if turnover > max_turnover:
                failures.append(
                    f"Gate G5: Turnover {turnover:.1%} exceeds maximum allowable friction ({max_turnover:.1%})."
                )
                gate_details["G5_turnover_bounds"] = False
            elif turnover < min_turnover:
                warnings.append(
                    f"Warning: Turnover {turnover:.1%} is suspiciously low (< {min_turnover:.1%}); check signal activity."
                )
                gate_details["G5_turnover_bounds"] = True
            else:
                gate_details["G5_turnover_bounds"] = True

        # 3. Gate G5.3: Minimum Fitness (if available)
        min_fitness = self.thresholds.get("min_fitness", 1.00)
        if fitness is not None:
            if fitness < min_fitness:
                warnings.append(f"Warning: Fitness score {fitness:.2f} is below target ({min_fitness:.2f}).")
                gate_details["G5_min_fitness"] = False
            else:
                gate_details["G5_min_fitness"] = True

        # 4. Gate G5.4: Maximum Drawdown (if available)
        max_drawdown = self.thresholds.get("max_drawdown", 0.25)
        if drawdown is not None:
            if drawdown > max_drawdown:
                failures.append(f"Gate G5: Drawdown {drawdown:.1%} exceeds limit ({max_drawdown:.1%}).")
                gate_details["G5_max_drawdown"] = False
            else:
                gate_details["G5_max_drawdown"] = True

        passed = len(failures) == 0
        return GateEvaluationResult(
            passed=passed,
            warnings=warnings,
            failures=failures,
            gate_details=gate_details,
        )
