"""Automated submission metadata generator for WorldQuant BRAIN candidate alphas."""
import re
from dataclasses import dataclass

from worldquant_pipeline.storage.models import AlphaCandidate


@dataclass
class AlphaSubmissionMetadata:
    """Standardized metadata block complying with Invariant 6."""

    candidate_id: str
    name: str
    category: str  # 'none', 'price reversion', or 'price momentum'
    tags: list[str]  # exactly 3 tags
    description: str
    expression: str
    universe: str = "TOP1000"
    neutralization: str = "Sector"
    decay: int = 4
    delay: int = 1
    truncation: float = 0.0100


def generate_submission_metadata(
    candidate: AlphaCandidate,
    universe: str = "TOP1000",
    neutralization: str = "Sector",
    decay: int = 4,
) -> AlphaSubmissionMetadata:
    """Generate standardized, compliant submission metadata for an approved alpha."""
    expr = candidate.expression_raw
    name_parts: list[str] = []
    tags: list[str] = []
    category = "price momentum"

    # Category detection
    if "ts_delta(close" in expr or "ts_decay" in expr:
        if "-" in expr and "ts_delta" in expr:
            category = "price momentum"
        else:
            category = "price reversion"
    else:
        category = "none"

    # Primary driver detection & tag generation
    if "anl4_afv4_median_eps" in expr:
        name_parts.append("Consensus_Median_EPS_Yield")
        tags.extend(["analyst", "earnings", "capex"])
        desc_driver = (
            "Ranks equities by analyst consensus forward median EPS relative to stock price (Forward Earnings Yield). "
            "Stabilized by corporate capital expenditure intensity to reward disciplined capital allocation."
        )
    elif "anl4_cfo_value" in expr:
        name_parts.append("Operating_Cash_Flow_Yield")
        tags.extend(["analyst", "cashflow", "capex"])
        desc_driver = (
            "Ranks equities by analyst operating cash flow estimates relative to market capitalization. "
            "Combines cash flow generation convexity with announced capex reinvestment to capture free cash flow momentum."
        )
    elif "anl4_afv4_cfps" in expr:
        name_parts.append("Consensus_Cash_Flow_Per_Share_Yield")
        tags.extend(["analyst", "cashflow", "capex"])
        desc_driver = (
            "Ranks equities by Wall Street consensus cash flow per share forecasts relative to price. "
            "Operating cash flow isolates organic unit profitability free from non-cash accounting accruals."
        )
    elif "implied_volatility_call" in expr:
        name_parts.append("Call_Implied_Vol_Surface_Asymmetry")
        tags.extend(["options", "volatility", "capex"])
        desc_driver = (
            "Measures institutional upside call option implied volatility relative to realized Parkinson volatility. "
            "Stationarized percentile ranking captures speculative accumulation while capex discipline prevents value traps."
        )
    elif "historical_volatility" in expr and "implied_volatility" in expr:
        name_parts.append("Variance_Risk_Premium_Realized_Dislocation")
        tags.extend(["options", "volatility", "vrp"])
        desc_driver = (
            "Exploits the structural Variance Risk Premium (VRP) by ranking stocks where realized price volatility "
            "diverges from option implied volatility over a 180-day percentile window."
        )
    elif "pv13" in expr:
        name_parts.append("Supply_Chain_Customer_Momentum_Spillover")
        tags.extend(["relationship", "supplychain", "leadlag"])
        desc_driver = (
            "Captures customer return signal propagation along corporate supply chain linkages. "
            "Exploits delayed information diffusion between major buyers and upstream component suppliers."
        )
    elif "beta_" in expr or "unsystematic_" in expr:
        name_parts.append("Idiosyncratic_Risk_Defensive_Convexity")
        tags.extend(["risk", "lowbeta", "quality"])
        desc_driver = (
            "Ranks equities by unsystematic return variance and rolling beta against the broad market index, "
            "harvesting the empirical low-beta and low-volatility anomaly within sector peers."
        )
    else:
        # Fallback generic detection
        fields = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr)
        valid_fields = [f for f in fields if f not in {"signed_power", "group_rank", "ts_rank", "ts_mean", "ts_delta", "close", "sector", "market", "subindustry", "ts_backfill"}]
        top_f = valid_fields[0] if valid_fields else "Factor"
        name_parts.append(f"{top_f.capitalize()}_Alpha")
        tags.extend(["fundamental", "momentum", "quant"])
        desc_driver = f"Quantitative composite ranking equities by {top_f} combined with short-term microstructure stabilization."

    # Neutralization & convexity in name
    if "signed_power" in expr:
        name_parts.append("Convexity")
    if neutralization == "Market":
        name_parts.append("Market_Neutral")

    full_name = "_".join(name_parts)
    # Ensure exactly 3 tags
    tags = (tags + ["quant", "equities", "stat_arb"])[:3]

    return AlphaSubmissionMetadata(
        candidate_id=candidate.id[:8],
        name=full_name,
        category=category,
        tags=tags,
        description=desc_driver,
        expression=expr,
        universe=universe,
        neutralization=neutralization,
        decay=decay,
    )
