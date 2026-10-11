import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("data/market1501_published_distribution.csv")
OUTPUT_DIR = Path("figures")
OUTPUT_PATH = OUTPUT_DIR / "market1501_age_distribution.pdf"

df = pd.read_csv(DATA_PATH)

OUTPUT_DIR.mkdir(exist_ok=True)

plt.figure(figsize=(6, 4))
plt.bar(df["category"], df["percentage"])
plt.xlabel("Age category")
plt.ylabel("Percentage (%)")
plt.title("Market-1501 Age-Category Distribution")
plt.ylim(0, 100)
plt.tight_layout()

plt.savefig(OUTPUT_PATH, bbox_inches="tight")
plt.close()

print(f"Saved figure to {OUTPUT_PATH}")
