import argparse
import json
import math
from pathlib import Path
import pandas as pd


def normalized_shannon(proportions):
    p = [float(x) for x in proportions if float(x) > 0]
    if len(p) <= 1:
        return 0.0
    total = sum(p)
    p = [x / total for x in p]
    return -sum(x * math.log(x) for x in p) / math.log(len(p))


def inclusivity_ratio(observed_categories, reference_categories):
    observed = set(observed_categories)
    reference = set(reference_categories)
    if not reference:
        raise ValueError("Reference taxonomy must not be empty.")
    unknown = observed - reference
    if unknown:
        raise ValueError(
            f"Observed categories not in the supplied reference taxonomy: {sorted(unknown)}"
        )
    return len(observed) / len(reference)


def summarize_attribute(frame: pd.DataFrame, attribute: str):
    part = frame[frame["attribute"] == attribute].copy()
    if part.empty:
        raise ValueError(f"No rows found for attribute: {attribute}")
    total = float(part["proportion"].sum())
    if total <= 0:
        raise ValueError(f"Attribute {attribute} has no positive mass.")
    part["normalized_proportion"] = part["proportion"] / total
    return {
        "attribute": attribute,
        "categories": part["category"].tolist(),
        "proportions": dict(zip(part["category"], part["normalized_proportion"].round(6))),
        "normalized_shannon": round(normalized_shannon(part["normalized_proportion"]), 6),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    required = {"attribute", "category", "proportion"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    out = {
        attribute: summarize_attribute(frame, attribute)
        for attribute in frame["attribute"].drop_duplicates()
    }

    if "gender" in out:
        observed = out["gender"]["categories"]
        reference = ["male", "female", "other"]
        if set(observed).issubset(reference):
            out["gender"]["inclusivity_reference"] = reference
            out["gender"]["inclusivity_ratio"] = round(
                inclusivity_ratio(observed, reference), 6
            )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
