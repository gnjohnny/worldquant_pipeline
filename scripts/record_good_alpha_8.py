import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Decision, Experiment, ExperimentMetric

with get_session() as session:
    cand = session.query(AlphaCandidate).filter(AlphaCandidate.id.startswith("df2c5ace")).first()
    if cand:
        exp = Experiment(candidate_id=cand.id, status="COMPLETED")
        session.add(exp)
        session.flush()

        metrics = {
            "sharpe": 1.58,
            "fitness": 1.55,
            "turnover": 0.0790,
            "sub_universe_sharpe": 1.44,
            "self_correlation": 0.2707,
        }
        for k, v in metrics.items():
            session.add(ExperimentMetric(experiment_id=exp.id, metric_name=k, metric_value=v, source="BRAIN_PLATFORM"))

        dec = Decision(
            candidate_id=cand.id,
            decision="APPROVED",
            reason="Alpha 8 Crown Jewel ('GOOD' Platform Rating): 170-day operating income yield in TOPSP500 with Market neutralization and decay=4. Cleared all 8 platform gates with Sharpe 1.58, Fitness 1.55, Turnover 7.90%, Sub-universe Sharpe 1.44, and Self-correlation 0.2707.",
            reviewer="HUMAN_RESEARCHER",
        )
        session.add(dec)
        cand.status = "APPROVED"
        session.commit()
        print(f"Successfully recorded Alpha 8 Crown Jewel ({cand.id}): Fitness 1.55 'GOOD', Sharpe 1.58, Turnover 7.90%!")
