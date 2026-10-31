"""Quality gates G0–G7 evaluation logic."""
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.evaluation.fingerprint import FactorFingerprintAuditor
from worldquant_pipeline.evaluation.turnover_proxy import TurnoverProxyCalculator
from worldquant_pipeline.expressions.validator import ExpressionValidator


@dataclass
class GateEvaluationResult:
    """Outcome of quality gate evaluation."""
    passed: bool
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    gate_details: dict[str, bool] = field(default_factory=dict)


class QualityGateRunner:
    """Evaluates simulation results and pre-simulation expressions against G0–G7 research gates."""

    def __init__(self, thresholds: dict[str, Any] | None = None) -> None:
        settings = get_settings()
        self.thresholds = thresholds or settings.research_config.get("quality_gates", {
            "min_sharpe": 1.25,
            "min_fitness": 1.50,
            "max_turnover": 0.70,
            "min_turnover": 0.01,
            "max_drawdown": 0.25,
            "max_correlation": 0.70,
        })
        self.validator = ExpressionValidator()

    def evaluate_pre_simulation(
        self,
        expression: str,
        session: Session | None = None,
        decay: int = 4,
        target_grouping: str | None = None,
    ) -> GateEvaluationResult:
        """Run pre-simulation quality gates: G1 (AST & event inputs), G2 (turnover proxy), and G3+ (fingerprint overlap)."""
        warnings: list[str] = []
        failures: list[str] = []
        gate_details: dict[str, bool] = {}

        # 1. Gate G1: Deterministic AST & Event Input Verification
        ast_res = self.validator.validate_expression_string(expression)
        if not ast_res.is_valid:
            failures.extend(ast_res.errors)
            gate_details["G1_ast_validity"] = False
        else:
            gate_details["G1_ast_validity"] = True
        warnings.extend(ast_res.warnings)

        # 2. Gate G2: Mathematical Turnover Pre-Screening
        turnover_res = TurnoverProxyCalculator.estimate(expression, decay=decay)
        warnings.extend(turnover_res.warnings)
        if not turnover_res.is_safe and turnover_res.status == "HIGH_RISK":
            failures.extend(turnover_res.warnings)
            gate_details["G2_turnover_proxy"] = False
        else:
            gate_details["G2_turnover_proxy"] = True

        # 3. Gate G3+: Factor Fingerprint & Self-Correlation Collision Auditor
        if session is not None:
            fp_res = FactorFingerprintAuditor.audit_against_database(
                expression, session, target_grouping=target_grouping
            )
            warnings.extend(fp_res.warnings)
            if fp_res.risk_level == "HIGH":
                gate_details["G3_correlation_risk"] = False
            else:
                gate_details["G3_correlation_risk"] = True
        else:
            gate_details["G3_correlation_risk"] = True

        passed = len(failures) == 0
        return GateEvaluationResult(
            passed=passed,
            warnings=warnings,
            failures=failures,
            gate_details=gate_details,
        )

    def evaluate_metrics(self, metrics: dict[str, float]) -> GateEvaluationResult:
        """Evaluate platform simulation metrics against Gate G5 (Robustness & Friction)."""
        warnings: list[str] = []
        failures: list[str] = []
        gate_details: dict[str, bool] = {}

        sharpe = metrics.get("sharpe")
        turnover = metrics.get("turnover")
        fitness = metrics.get("fitness")
        drawdown = metrics.get("drawdown")
        self_corr = metrics.get("self_correlation")

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

        # 3. Gate G5.3: Minimum Fitness
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

        # 5. Gate G5.5: Maximum Self-Correlation
        max_corr = self.thresholds.get("max_correlation", 0.70)
        if self_corr is not None:
            if self_corr >= max_corr:
                failures.append(f"Gate G5: Self-correlation {self_corr:.4f} is above cutoff of {max_corr:.2f}.")
                gate_details["G5_max_correlation"] = False
            else:
                gate_details["G5_max_correlation"] = True

        passed = len(failures) == 0
        return GateEvaluationResult(
            passed=passed,
            warnings=warnings,
            failures=failures,
            gate_details=gate_details,
        )
