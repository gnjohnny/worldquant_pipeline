"""Prompt generator for zero-cost AI copilot brainstorming."""

from collections import Counter

from sqlalchemy.orm import Session

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.storage.models import Decision

# Domain-to-category mapping for smart field filtering
DOMAIN_CATEGORY_MAP: dict[str, list[str]] = {
    "price_volume": ["price_volume", "volatility"],
    "momentum": ["price_volume", "volatility", "model_fundamental_scores"],
    "analyst": ["analyst", "fundamental", "model_fundamental_scores"],
    "fundamental": ["fundamental", "model_fundamental_scores", "analyst"],
    "options": ["options", "option", "volatility"],
    "volatility": ["volatility", "options", "option", "model_systematic_risk"],
    "relationship": ["relationship", "price_volume"],
    "risk": ["model_systematic_risk", "risk", "volatility", "price_volume"],
}

CORE_BENCHMARK_FIELDS: set[str] = {
    "close", "open", "high", "low", "volume", "vwap", "returns", "adv20", "cap", "subindustry"
}


def _cluster_rejection_reasons(rejections: list[Decision]) -> tuple[str, list[str]]:
    """Cluster raw rejection strings into actionable quantitative failure modes."""
    if not rejections:
        return "None recorded yet (first iteration).", []

    categories = Counter()
    recent_examples = []

    for r in rejections:
        reason_text = r.reason.lower()
        if "turnover" in reason_text or "friction" in reason_text:
            categories["Excessive Turnover (>70% or rapid decay)"] += 1
        elif "self-correlation" in reason_text or "correlation" in reason_text:
            categories["Self-Correlation Collision with Approved Portfolio"] += 1
        elif "fitness" in reason_text or "sharpe" in reason_text:
            categories["Sub-Threshold Fitness (<1.50) or Low Sharpe (<1.25)"] += 1
        elif "weight" in reason_text or "concentrat" in reason_text:
            categories["Extreme Weight Concentration / Illiquidity"] += 1
        elif "sub-universe" in reason_text:
            categories["Sub-Universe Sharpe Instability"] += 1
        else:
            categories["Signal Decay / Inverted Direction"] += 1

    total = len(rejections)
    summary_lines = ["### Top Historical Failure Modes:"]
    for cat, count in categories.most_common(4):
        pct = (count / total) * 100
        summary_lines.append(f"- **{cat}**: {count} occurrences ({pct:.0f}%)")

    summary_lines.append("\n### Recent Specific Failures to Avoid:")
    for r in rejections[:5]:
        recent_examples.append(f"- Candidate `{r.candidate_id[:8]}`: {r.reason.strip()}")
    summary_lines.extend(recent_examples)

    return "\n".join(summary_lines), recent_examples


def generate_copilot_prompt(
    domain: str | None = None,
    session: Session | None = None,
    max_rejections: int = 15,
) -> str:
    """Generate a domain-tailored Markdown prompt with focused fields, operators, and failure intelligence."""
    settings = get_settings()
    active_domain = domain or settings.research_domain

    # 1. Gather whitelisted operators
    operators_dict = settings.get_allowed_operators()
    op_lines = []
    for name, spec in sorted(operators_dict.items()):
        params = ", ".join(spec.get("param_types", []))
        op_lines.append(f"- `{name}({params})`: {spec.get('description', '')}")

    # 2. Gather whitelisted fields tailored to active domain
    fields_dict = settings.get_allowed_fields()
    target_categories = set(DOMAIN_CATEGORY_MAP.get(active_domain.lower(), []))

    field_lines = []
    # Priority: Core benchmark fields + fields matching domain categories
    for key, spec in sorted(fields_dict.items()):
        cat = spec.get("category", "").lower()
        is_core = key.lower() in CORE_BENCHMARK_FIELDS
        matches_domain = not target_categories or cat in target_categories or any(tc in cat for tc in target_categories)

        if is_core or matches_domain:
            field_lines.append(f"- `{key}` ({spec.get('category')}): {spec.get('description')}")

    # Fallback if domain had no direct matches
    if len(field_lines) <= len(CORE_BENCHMARK_FIELDS):
        field_lines = [
            f"- `{key}` ({spec.get('category')}): {spec.get('description')}"
            for key, spec in sorted(fields_dict.items())[:60]
        ]

    # 3. Gather negative knowledge from past rejections with failure clustering
    rejection_section = "None recorded yet (first iteration)."
    if session is not None:
        try:
            recent_rejections = (
                session.query(Decision)
                .filter(Decision.decision == "REJECTED")
                .order_by(Decision.created_at.desc())
                .limit(max_rejections)
                .all()
            )
            rejection_section, _ = _cluster_rejection_reasons(recent_rejections)
        except Exception:  # noqa: BLE001, S110
            pass

    prompt = f"""# Research Task: WorldQuant BRAIN Alpha Hypotheses

You are assisting a quantitative researcher. Propose exactly **3 distinct, falsifiable candidate alphas** (Tri-Candidate Batch Protocol) for the research domain **`{active_domain}`**.

## Core Constraints & Quality Invariants
1. **Target Gold Track Rating (Fitness >= 1.50)**: Aim for Fitness >= 1.50, Sharpe >= 1.50, and turnover in the optimal 10%–25% range.
2. **Use ONLY Whitelisted Operators**: Do not invent functions. Use only the exact operators listed below.
3. **Use ONLY Whitelisted Fields**: Use only fields from the data catalog below. Always normalize or scale unbounded metrics.
4. **Delay = 1 Strictness**: Assume daily decision time at market open/close with delay=1 to prevent look-ahead bias.
5. **Radical Alpha Originality**: Do NOT repeat the boilerplate template `0.85 * signed_power(...) - 0.15 * group_rank(...)`. Explore conditional regime switches (`trade_when`), rolling regressions (`ts_regression`), rolling correlations (`ts_corr`), or ratio dispersion spreads (`group_zscore`).
6. **Learn from Past Rejections**: Address the specific historical failure modes listed below.

## Whitelisted Operators
{chr(10).join(op_lines)}

## Approved Data Fields (Domain: {active_domain})
{chr(10).join(field_lines)}

## Negative Knowledge & Failure Intelligence
{rejection_section}

## Required JSON Output Schema
Return a single valid JSON object matching this exact structure with exactly 3 candidate alphas:

```json
{{
  "hypotheses": [
    {{
      "title": "Short descriptive title",
      "domain": "{active_domain}",
      "economic_rationale": "Clear behavioral or economic explanation of why this anomaly exists.",
      "expected_direction": "positive",
      "intended_horizon": "15d",
      "confounders": ["sector_momentum", "liquidity_bias"],
      "falsification_test": "Returns diminish or reverse after controlling for subindustry.",
      "candidates": [
        {{
          "expression": "group_rank(ts_corr(close, volume, 20), subindustry)",
          "rationale": "Rolling 20-day price-volume co-movement decoupling within subindustry",
          "expected_direction": "positive"
        }},
        {{
          "expression": "group_zscore(ts_backfill(actual_cashflow_per_share_value_quarterly, 60) / close, subindustry)",
          "rationale": "Operating cash flow yield dispersion normalized cross-sectionally",
          "expected_direction": "positive"
        }},
        {{
          "expression": "trade_when(historical_volatility_60 > ts_mean(historical_volatility_60, 120), -group_rank(historical_volatility_60, subindustry), group_rank(ts_rank(close, 20), subindustry))",
          "rationale": "Regime-conditional switch allocating to defensive low-vol during panic and trend during calm",
          "expected_direction": "positive"
        }}
      ]
    }}
  ]
}}
```
"""
    return prompt.strip()
