"""Find which fields in configs/data_sources.yaml have NEVER been used in alpha_candidates table."""
import sys

import yaml

sys.path.insert(0, "src")
from worldquant_pipeline.storage.database import get_session
from worldquant_pipeline.storage.models import AlphaCandidate

session = get_session()
cands = session.query(AlphaCandidate.expression_raw).all()
all_exprs = " ".join([c[0] for c in cands])

with open("configs/data_sources.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
fields = cfg["fields"]

never_used = []
for f in fields:
    key = f["field_key"]
    if key not in all_exprs:
        never_used.append(f)

print(f"Total fields in catalog: {len(fields)}")
print(f"Never used fields: {len(never_used)} ({len(never_used)/len(fields)*100:.1f}%)")

from collections import defaultdict

by_cat = defaultdict(list)
for f in never_used:
    by_cat[f["category"]].append(f["field_key"])

for cat, f_list in sorted(by_cat.items()):
    print(f"\nCategory '{cat}' ({len(f_list)} never-used fields):")
    print("  " + ", ".join(f_list[:15]))
    if len(f_list) > 15:
        print(f"  ... and {len(f_list)-15} more")

session.close()
