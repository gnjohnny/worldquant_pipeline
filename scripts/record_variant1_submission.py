import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.expressions.canonicalize import (
    canonicalize_expression,
    compute_expression_hash,
)
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import (
    AlphaCandidate,
    DataField,
    Decision,
    Experiment,
    ExperimentMetric,
    ResearchHypothesis,
)


def record():
    expr = (
        "group_neutralize(signed_power(min(max(-group_zscore("
        "accumulated_depreciation_depletion_amortization_ppne, subindustry) * "
        "group_rank(composite_factor_score_derivative, subindustry), -2.5), 2.5), 2), subindustry)"
    )
    canon = canonicalize_expression(expr)
    e_hash = compute_expression_hash(canon)

    with get_session() as session:
        # Ensure field is in data_fields
        f_key = "accumulated_depreciation_depletion_amortization_ppne"
        f = session.get(DataField, f_key)
        if not f:
            f = DataField(
                field_key=f_key,
                category="fundamental",
                description="Accumulated depreciation, depletion, and amortization of property, plant, and equipment",
                timing_delay=1,
                region="USA",
                permitted_use=True,
            )
            session.add(f)
            session.flush()

        # Check if candidate already exists
        existing = session.query(AlphaCandidate).filter_by(expression_hash=e_hash).first()
        if existing:
            cand = existing
            print(f"Candidate already exists: {cand.id}")
        else:
            hypo_id = str(uuid.uuid4())
            hypo = ResearchHypothesis(
                id=hypo_id,
                title="Capital Vintage Depreciation Efficiency and Composite Momentum (TOPSP500)",
                domain="fundamental",
                economic_rationale=(
                    "Exploits physical capital asset vintage by identifying firms with lower accumulated "
                    "depreciation relative to subindustry peers, conditioned on multi-factor composite momentum."
                ),
                expected_direction="positive",
                intended_horizon="14d",
                status="ACTIVE",
            )
            session.add(hypo)

            cand_id = str(uuid.uuid4())
            cand = AlphaCandidate(
                id=cand_id,
                hypothesis_id=hypo_id,
                expression_raw=expr,
                expression_normalized=canon,
                expression_hash=e_hash,
                status="APPROVED",
            )
            session.add(cand)
            session.flush()
            print(f"Created Candidate: {cand.id}")

        exp_id = str(uuid.uuid4())
        exp = Experiment(
            id=exp_id,
            candidate_id=cand.id,
            universe="TOPSP500",
            delay=1,
            neutralization="SUBINDUSTRY",
            decay=14,
            truncation=0.02,
            finished_at=datetime.now(),
            status="COMPLETED",
        )
        session.add(exp)

        metrics = {
            "sharpe": 1.36,
            "fitness": 1.09,
            "turnover": 0.0189,
            "sub_universe_sharpe": 0.98,
            "self_correlation": 0.1921,
            "pass_count": 8.0,
        }
        for k, v in metrics.items():
            m = ExperimentMetric(
                id=str(uuid.uuid4()),
                experiment_id=exp_id,
                metric_name=k,
                metric_value=v,
                source="BRAIN_PLATFORM",
            )
            session.add(m)

        dec = Decision(
            id=str(uuid.uuid4()),
            candidate_id=cand.id,
            decision="APPROVED",
            reason=(
                "8 PASS on TOPSP500. Sharpe 1.36 > 1.25, Fitness 1.09 > 1.0, Turnover 1.89%, "
                "Sub-universe Sharpe 0.98 > 0.69, Self-correlation 0.1921 < 0.70. "
                "Ultra-low portfolio correlation with outstanding orthogonal diversification."
            ),
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)
        session.commit()
        print("Recorded candidate, experiment, and decision successfully!")
        return cand.id

if __name__ == "__main__":
    cand_id = record()
    print("Candidate ID:", cand_id)
