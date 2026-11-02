from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

MISSING_LABEL = "(Missing)"

def column_profile(df: pd.DataFrame) -> list[dict[str, Any]]:
    out = []
    for col in df.columns:
        s = df[col]
        item = {
            "column": str(col),
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_pct": round(float(s.isna().mean() * 100), 2),
            "unique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            vals = pd.to_numeric(s, errors="coerce").dropna()
            if len(vals):
                item.update({
                    "mean": round(float(vals.mean()), 3),
                    "median": round(float(vals.median()), 3),
                    "std": round(float(vals.std(ddof=1)), 3) if len(vals) > 1 else 0.0,
                    "min": round(float(vals.min()), 3),
                    "max": round(float(vals.max()), 3),
                })
        out.append(item)
    return out

def overview(df: pd.DataFrame) -> dict[str, Any]:
    missing_cells = int(df.isna().sum().sum())
    numeric_cols = list(df.select_dtypes(include=np.number).columns.astype(str))
    categorical_cols = [str(c) for c in df.columns if str(c) not in numeric_cols]
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_cells": missing_cells,
        "completeness_pct": round(100 * (1 - missing_cells / max(1, df.size)), 2),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "profile": column_profile(df),
    }

def frequency(df: pd.DataFrame, column: str, top_n: int = 15) -> list[dict[str, Any]]:
    if column not in df.columns:
        raise KeyError(column)
    s = df[column].fillna(MISSING_LABEL).astype(str)
    counts = s.value_counts(dropna=False).head(top_n)
    total = len(s)
    return [{"value": str(k), "count": int(v), "pct": round(v / max(total, 1) * 100, 2)} for k, v in counts.items()]

def crosstab(df: pd.DataFrame, row: str, col: str) -> dict[str, Any]:
    if row not in df.columns or col not in df.columns:
        raise KeyError("Unknown column")
    r = df[row].fillna(MISSING_LABEL).astype(str)
    c = df[col].fillna(MISSING_LABEL).astype(str)
    table = pd.crosstab(r, c)
    row_pct = pd.crosstab(r, c, normalize="index") * 100
    chi2 = p = dof = None
    if table.shape[0] > 1 and table.shape[1] > 1 and table.values.sum() > 0:
        try:
            chi2, p, dof, _ = chi2_contingency(table)
        except ValueError:
            pass
    return {
        "row_variable": row,
        "column_variable": col,
        "columns": [str(x) for x in table.columns],
        "rows": [
            {
                "label": str(idx),
                "counts": [int(x) for x in table.loc[idx].tolist()],
                "row_pct": [round(float(x), 2) for x in row_pct.loc[idx].tolist()],
            }
            for idx in table.index
        ],
        "chi_square": None if chi2 is None else round(float(chi2), 4),
        "p_value": None if p is None else round(float(p), 6),
        "degrees_of_freedom": None if dof is None else int(dof),
    }

def numeric_summary(df: pd.DataFrame, column: str) -> dict[str, Any]:
    if column not in df.columns:
        raise KeyError(column)
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    if s.empty:
        raise ValueError("Column has no numeric values")
    q = s.quantile([0.25, 0.5, 0.75])
    return {
        "column": column,
        "count": int(s.count()),
        "mean": round(float(s.mean()), 3),
        "median": round(float(s.median()), 3),
        "std": round(float(s.std(ddof=1)), 3) if len(s) > 1 else 0.0,
        "min": round(float(s.min()), 3),
        "q1": round(float(q.loc[0.25]), 3),
        "q3": round(float(q.loc[0.75]), 3),
        "max": round(float(s.max()), 3),
    }

def correlation_matrix(df: pd.DataFrame) -> dict[str, Any]:
    num = df.select_dtypes(include=np.number)
    if num.shape[1] < 2:
        return {"columns": list(num.columns.astype(str)), "matrix": []}
    corr = num.corr(numeric_only=True).round(3)
    return {"columns": list(corr.columns.astype(str)), "matrix": corr.fillna(0).values.tolist()}
