import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import select

from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate


def list_recent():
    with get_session() as session:
        stmt = select(AlphaCandidate).order_by(AlphaCandidate.created_at.desc()).limit(10)
        cands = session.scalars(stmt).all()
        for c in cands:
            print(f"Cand ID: {c.id}")
            print(f"  Raw: {c.expression_raw}")
            print(f"  Created: {c.created_at}")

if __name__ == "__main__":
    list_recent()
