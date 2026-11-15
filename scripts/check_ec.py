import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import select

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate, Experiment


def check_ec():
    with get_session() as session:
        cands = session.scalars(select(AlphaCandidate).where(AlphaCandidate.expression_raw.like('%earnings_certainty_rank_derivative%'))).all()
        print(f"Found {len(cands)} cands with earnings certainty")
        for c in cands:
            exps = session.scalars(select(Experiment).where(Experiment.candidate_id == c.id)).all()
            for exp in exps:
                metrics = {m.metric_name: float(m.metric_value) for m in exp.metrics}
                print(f"  {c.id[:8]}: Sharpe={metrics.get('sharpe')}, Fitness={metrics.get('fitness')}, Turnover={metrics.get('turnover')}")

if __name__ == "__main__":
    check_ec()
