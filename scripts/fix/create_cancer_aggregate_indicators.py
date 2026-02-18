#!/usr/bin/env python3
"""
Create cancer-specific aggregate indicators (CECAP-style) and
write a quick mapping list of Cancer -> Aggregate Elements.
"""
import json
import random
import string
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DE_PATH = BASE_DIR / "Data Element" / "Data Element.json"
IND_PATH = BASE_DIR / "Options" / "Indicator.json"
REPORT_PATH = BASE_DIR / "artifacts" / "reports" / "CANCER_AGGREGATE_MAPPING.txt"

CANCERS = [
    "Bladder",
    "Breast",
    "Colorectal",
    "Esophageal",
    "Kaposi Sarcoma",
    "Kidney",
    "Leukemia",
    "Liver",
    "Lung",
    "Lymphoma",
    "Oral Head Neck",
    "Ovarian",
    "Pancreatic",
    "Prostate",
    "Skin Melanoma",
    "Stomach",
    "Testicular",
    "Thyroid",
]


def generate_uid():
    chars = string.ascii_letters + string.digits
    first = random.choice(string.ascii_letters)
    rest = "".join(random.choice(chars) for _ in range(10))
    return first + rest


def truncate_short_name(value):
    if not value:
        return value
    if len(value) <= 50:
        return value
    return value[:50]


def extract_ids(expression):
    if not expression:
        return []
    ids = []
    start = 0
    while True:
        idx = expression.find("#{", start)
        if idx == -1:
            break
        end = expression.find("}", idx)
        if end == -1:
            break
        ids.append(expression[idx + 2 : end])
        start = end + 1
    return ids


def main():
    with open(DE_PATH) as f:
        de_data = json.load(f)

    data_elements = de_data.get("dataElements", [])
    agg_elements = [de for de in data_elements if de.get("domainType") == "AGGREGATE"]
    de_by_id = {de.get("id"): de for de in agg_elements}
    de_by_name = {de.get("name"): de for de in agg_elements}

    # Identify base aggregate elements (non-prefixed)
    base_aggs = [
        de for de in agg_elements
        if not any(de.get("name", "").startswith(f"{cancer} - ") for cancer in CANCERS)
    ]

    with open(IND_PATH) as f:
        ind_data = json.load(f)

    indicators = ind_data.get("indicators", [])
    existing_names = {i.get("name") for i in indicators}
    existing_ids = {i.get("id") for i in indicators}

    # Use existing indicators as base (CECAP-style)
    base_indicators = indicators[:]
    if not base_indicators:
        print("No base indicators found; skipping indicator creation.")
    else:
        now = datetime.now().isoformat()
        created = 0
        for cancer in CANCERS:
            for base in base_indicators:
                base_name = base.get("name") or ""
                new_name = f"{cancer} - {base_name}"
                if new_name in existing_names:
                    continue

                base_num_ids = extract_ids(base.get("numerator"))
                base_den_ids = extract_ids(base.get("denominator"))

                def map_expr(expr_ids):
                    mapped = []
                    for de_id in expr_ids:
                        base_de = de_by_id.get(de_id)
                        if not base_de:
                            continue
                        base_de_name = base_de.get("name")
                        if not base_de_name:
                            continue
                        target_name = f"{cancer} - {base_de_name}"
                        target_de = de_by_name.get(target_name)
                        if not target_de:
                            continue
                        mapped.append(target_de.get("id"))
                    return mapped

                mapped_num = map_expr(base_num_ids)
                mapped_den = map_expr(base_den_ids)

                if base_num_ids and not mapped_num:
                    continue
                if base_den_ids and not mapped_den:
                    continue

                new_id = generate_uid()
                while new_id in existing_ids:
                    new_id = generate_uid()

                clone = json.loads(json.dumps(base))
                clone["id"] = new_id
                clone["name"] = new_name
                clone["shortName"] = truncate_short_name(new_name)
                clone["created"] = now
                clone["lastUpdated"] = now

                if mapped_num:
                    clone["numerator"] = " + ".join(f"#{{{i}}}" for i in mapped_num)
                    clone["numeratorDescription"] = new_name
                if mapped_den:
                    clone["denominator"] = " + ".join(f"#{{{i}}}" for i in mapped_den)
                    clone["denominatorDescription"] = new_name

                indicators.append(clone)
                existing_names.add(new_name)
                existing_ids.add(new_id)
                created += 1

        ind_data["indicators"] = indicators
        with open(IND_PATH, "w") as f:
            json.dump(ind_data, f, indent=2, ensure_ascii=True)
            f.write("\n")

        print(f"Created {created} aggregate indicators.")

    # Normalize existing indicator short names to max length
    updated = 0
    for ind in indicators:
        short_name = ind.get("shortName")
        if short_name and len(short_name) > 50:
            ind["shortName"] = truncate_short_name(short_name)
            updated += 1

    if updated:
        with open(IND_PATH, "w") as f:
            json.dump(ind_data, f, indent=2, ensure_ascii=True)
            f.write("\n")
        print(f"Normalized {updated} indicator shortName values.")

    # Write mapping list for verification
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("Cancer Aggregate Elements Mapping")
    lines.append("=" * 40)
    lines.append(f"Base aggregate elements: {len(base_aggs)}")
    lines.append("")

    for cancer in CANCERS:
        cancer_elements = [
            de for de in agg_elements if (de.get("name", "").startswith(f"{cancer} - "))
        ]
        lines.append(f"{cancer} ({len(cancer_elements)}):")
        for de in sorted(cancer_elements, key=lambda d: d.get("name", "")):
            lines.append(f"  - {de.get('name')} [{de.get('id')}]")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines))
    print(f"Mapping report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
