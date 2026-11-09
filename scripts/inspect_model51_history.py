import sys

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate

with get_session() as session:
    cands = (
        session.query(AlphaCandidate)
        .filter(
            AlphaCandidate.expression_raw.like("%beta%")
            | AlphaCandidate.expression_raw.like("%unsystematic%")
        )
        .all()
    )
    print(f"Total model51 candidates: {len(cands)}")
    for c in cands:
        exps = c.experiments
        if exps:
            m = {em.metric_name: em.metric_value for em in exps[0].metrics}
            print(
                f"{c.id[:8]} | Status: {c.status} | Sharpe: {m.get('sharpe')} | Fit: {m.get('fitness')} | Tov: {m.get('turnover')} | Expr: {c.expression_raw[:80]}"
            )
