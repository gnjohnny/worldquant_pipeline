"""Prompt generator for zero-cost AI copilot brainstorming."""

from sqlalchemy.orm import Session

from worldquant_pipeline.config.settings import get_settings
from worldquant_pipeline.storage.models import Decision


def generate_copilot_prompt(
    domain: str | None = None,
    session: Session | None = None,
    max_rejections: int = 5,
) -> str:
    """Generate a structured Markdown prompt pre-loaded with fields, operators, and failure memory."""
    settings = get_settings()
    active_domain = domain or settings.research_domain

    # 1. Gather whitelisted operators
    operators_dict = settings.get_allowed_operators()
    op_lines = []
    for name, spec in sorted(operators_dict.items()):
        params = ", ".join(spec.get("param_types", []))
        op_lines.append(f"- `{name}({params})`: {spec.get('description', '')}")

    # 2. Gather whitelisted fields
    fields_dict = settings.get_allowed_fields()
    field_lines = []
    for key, spec in sorted(fields_dict.items()):
        field_lines.append(f"- `{key}` ({spec.get('category')}): {spec.get('description')}")

    # 3. Gather negative knowledge from past rejections
    rejection_lines = []
    if session is not None:
        try:
            recent_rejections = (
                session.query(Decision)
                .filter(Decision.decision == "REJECTED")
                .order_by(Decision.created_at.desc())
                .limit(max_rejections)
                .all()
            )
            for r in recent_rejections:
                rejection_lines.append(f"- Candidate `{r.candidate_id}` rejected: {r.reason}")
        except Exception:  # noqa: BLE001, S110
            pass

    rejection_section = "\n".join(rejection_lines) if rejection_lines else "None recorded yet (first iteration)."

    prompt = f"""# Research Task: WorldQuant BRAIN Alpha Hypotheses

You are assisting a quantitative researcher. Propose at most 3 distinct, falsifiable hypotheses for the research domain **`{active_domain}`**.

## Core Constraints
1. **Use ONLY Whitelisted Operators**: Do not invent functions. Use only the exact operators listed below.
2. **Use ONLY Whitelisted Fields**: Use only fields from the data catalog below.
3. **Delay = 1 Strictness**: Assume daily decision time at market open/close with delay=1 to prevent look-ahead bias.
4. **Learn from Past Rejections**: Avoid patterns previously rejected for high turnover, data leakage, or lack of economic mechanism.

## Whitelisted Operators
{chr(10).join(op_lines)}

## Approved Data Fields
{chr(10).join(field_lines)}

## Negative Knowledge (Prior Failures to Avoid)
{rejection_section}

## Required JSON Output Schema
Return a single valid JSON object matching this exact structure:

```json
{{
  "hypotheses": [
    {{
      "title": "Short descriptive title",
      "domain": "{active_domain}",
      "economic_rationale": "Clear behavioral or economic explanation of why this anomaly exists.",
      "expected_direction": "positive",
      "intended_horizon": "5d",
      "confounders": ["sector_momentum", "liquidity_bias"],
      "falsification_test": "Returns diminish or reverse after controlling for subindustry.",
      "candidates": [
        {{
          "expression": "ts_rank(close, 10)",
          "rationale": "10-day lookback variant",
          "expected_direction": "positive"
        }},
        {{
          "expression": "group_rank(ts_delta(close, 5), subindustry)",
          "rationale": "5-day delta normalized across subindustry",
          "expected_direction": "positive"
        }}
      ]
    }}
  ]
}}
```
"""
    return prompt.strip()
