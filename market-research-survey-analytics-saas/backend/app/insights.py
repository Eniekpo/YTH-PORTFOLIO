from __future__ import annotations
import pandas as pd
from .analytics import overview, frequency

def generate_insights(df: pd.DataFrame) -> dict:
    """Deterministic offline insight generator for a reproducible portfolio demo."""
    ov = overview(df)
    bullets = [
        f"The dataset contains {ov['rows']:,} responses across {ov['columns']} variables with {ov['completeness_pct']}% cell completeness."
    ]
    for col in ov["categorical_columns"][:3]:
        freq = frequency(df, col, top_n=2)
        if freq:
            lead = freq[0]
            bullets.append(f"For {col}, the largest response group is '{lead['value']}' at {lead['pct']}% ({lead['count']:,} responses).")
    for col in ov["numeric_columns"][:3]:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s):
            bullets.append(f"{col} averages {s.mean():.2f}, with a median of {s.median():.2f} and observed range {s.min():.2f}-{s.max():.2f}.")
    missing = sorted(ov["profile"], key=lambda x: x["missing_pct"], reverse=True)
    if missing and missing[0]["missing_pct"] > 0:
        bullets.append(f"The highest missingness is in {missing[0]['column']} ({missing[0]['missing_pct']}%), which should be reviewed before inference or modelling.")
    return {
        "mode": "offline-statistical-narrative",
        "headline": "Automated Research Snapshot",
        "bullets": bullets[:7],
        "note": "Generated from descriptive statistics only. Treat as analyst prompts, not causal conclusions."
    }
