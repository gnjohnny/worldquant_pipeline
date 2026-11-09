import glob
import re
import sys

import pypdf

sys.stdout.reconfigure(encoding="utf-8")

for fpath in sorted(glob.glob("Quant_data/*.pdf")):
    reader = pypdf.PdfReader(fpath)
    full_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
    fields = re.findall(r"\b[a-z0-9_]{4,40}\b", full_text)
    valid_fields = [
        f
        for f in set(fields)
        if any(
            k in f
            for k in [
                "anl",
                "score",
                "fscore",
                "pv13",
                "revere",
                "volatility",
                "breakeven",
                "beta",
                "risk",
            ]
        )
    ]
    fname = fpath.split("\\")[-1]
    print(f"{fname}: {len(valid_fields)} fields -> {sorted(valid_fields)[:6]}")
