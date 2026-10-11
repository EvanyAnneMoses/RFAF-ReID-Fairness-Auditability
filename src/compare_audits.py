import argparse
import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score

VALID = {"D", "P", "ND", "NA"}


def compare(human: pd.DataFrame, llm: pd.DataFrame) -> dict:
    keys = ["dataset", "dimension"]
    merged = human.merge(llm, on=keys, suffixes=("_human", "_llm"), how="inner")
    if merged.empty:
        raise ValueError("No matching dataset/dimension rows between audits.")

    for col in ["status_human", "status_llm"]:
        bad = set(merged[col]) - VALID
        if bad:
            raise ValueError(f"Invalid codes in {col}: {sorted(bad)}")

    merged["agreement"] = merged["status_human"] == merged["status_llm"]
    merged["potential_overclaim"] = (
        (merged["status_human"] == "ND")
        & (merged["status_llm"].isin(["D", "P"]))
    )

    exact = float(merged["agreement"].mean())
    kappa = float(cohen_kappa_score(merged["status_human"], merged["status_llm"]))
    overclaim_rate = float(merged["potential_overclaim"].mean())

    disagreements = merged.loc[
        ~merged["agreement"],
        keys + ["status_human", "status_llm", "potential_overclaim"],
    ].to_dict(orient="records")

    return {
        "n_compared": int(len(merged)),
        "exact_agreement": round(exact, 4),
        "cohen_kappa": round(kappa, 4),
        "potential_overclaim_rate": round(overclaim_rate, 4),
        "disagreements": disagreements,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--human", required=True)
    p.add_argument("--llm", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    result = compare(pd.read_csv(args.human), pd.read_csv(args.llm))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
