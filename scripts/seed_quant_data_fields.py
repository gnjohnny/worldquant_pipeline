import json
from pathlib import Path

import yaml

# Load extracted fields catalog
catalog_path = Path("docs/brain_data_catalog.json")
with open(catalog_path, encoding="utf-8") as f:
    catalog = json.load(f)

# Load existing data_sources.yaml
data_sources_path = Path("configs/data_sources.yaml")
with open(data_sources_path, encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

existing_keys = {item["field_key"] for item in cfg["fields"]}
print(f"Existing fields in data_sources.yaml: {len(existing_keys)}")

# Mapping dataset to category
cat_map = {
    "model16": "fundamental",
    "model51": "risk",
    "option8": "options",
    "option9": "options",
    "analyst4": "analyst",
    "pv13": "alternative",
    "pv1": "price_volume",
    "univ1": "universe"
}

added_count = 0
for ds_id, ds_data in catalog.items():
    category = cat_map.get(ds_id, "alternative")
    for fname, fmeta in ds_data["fields"].items():
        # filter clean valid field names
        clean_name = fname.strip()
        # skip if too short or header artifacts
        if len(clean_name) <= 2 or clean_name in ["dates", "select", "clear", "matrix", "vector", "group"]:
            continue
        # clean any digit prefix artifact from pdf parsing like '0beta_last_30_days_spy' or '1actual_sales'
        if clean_name[0] in "0123456789" and len(clean_name) > 1 and clean_name[1].isalpha():
            clean_name = clean_name[1:]
        clean_name = clean_name.removeprefix("dates")
        
        if clean_name not in existing_keys:
            desc = fmeta["description"]
            cfg["fields"].append({
                "field_key": clean_name,
                "category": category,
                "description": desc[:150],
                "timing_delay": 1,
                "unit": "ratio" if "ratio" in clean_name or "rank" in clean_name else "USD",
                "region": "USA",
                "permitted_use": True
            })
            existing_keys.add(clean_name)
            added_count += 1

print(f"Added {added_count} new fields to data_sources.yaml. Total now: {len(cfg['fields'])}")

# Write back
with open(data_sources_path, "w", encoding="utf-8") as f:
    yaml.dump(cfg, f, sort_keys=False, indent=2)

print("Saved updated configs/data_sources.yaml")
