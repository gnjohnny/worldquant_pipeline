import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import select

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import ResearchHypothesis


def check_batch334():
    with get_session() as session:
        # Check hypothesis titles
        stmt = select(ResearchHypothesis).where(ResearchHypothesis.title.like('%Supply Chain%'))
        hyps = session.scalars(stmt).all()
        print(f"Found {len(hyps)} hypotheses matching 'Supply Chain'")
        for h in hyps[-5:]:
            print(f"Hypothesis {h.id}: {h.title}")
            for c in h.candidates:
                print(f"  Candidate {c.id}: {c.expression_raw[:70]}")

if __name__ == "__main__":
    check_batch334()
