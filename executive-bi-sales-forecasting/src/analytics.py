from __future__ import annotations

import pandas as pd
import numpy as np


def filter_sales(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    regions=None,
    channels=None,
    categories=None,
) -> pd.DataFrame:
    out = df.copy()
    out["order_date"] = pd.to_datetime(out["order_date"])
    if start_date is not None:
        out = out[out["order_date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        out = out[out["order_date"] <= pd.Timestamp(end_date)]
    if regions:
        out = out[out["region"].isin(regions)]
    if channels:
        out = out[out["channel"].isin(channels)]
    if categories:
        out = out[out["category"].isin(categories)]
    return out


def calculate_kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "revenue": 0.0, "gross_profit": 0.0, "gross_margin": 0.0,
            "orders": 0, "customers": 0, "units": 0, "aov": 0.0,
            "return_rate": 0.0,
        }
    revenue = float(df["net_sales"].sum())
    gross_profit = float(df["gross_profit"].sum())
    orders = int(df["order_id"].nunique())
    customers = int(df["customer_id"].nunique())
    units = int(df["quantity"].sum())
    returns = float(df["return_amount"].sum())
    gross_sales = float(df["gross_sales"].sum())
    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "gross_margin": gross_profit / revenue if revenue else 0.0,
        "orders": orders,
        "customers": customers,
        "units": units,
        "aov": revenue / orders if orders else 0.0,
        "return_rate": returns / gross_sales if gross_sales else 0.0,
    }


def monthly_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["month", "revenue", "gross_profit", "orders", "units"])
    x = df.copy()
    x["month"] = pd.to_datetime(x["order_date"]).dt.to_period("M").dt.to_timestamp()
    result = (
        x.groupby("month", as_index=False)
        .agg(
            revenue=("net_sales", "sum"),
            gross_profit=("gross_profit", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity", "sum"),
        )
        .sort_values("month")
    )
    result["gross_margin"] = np.where(result["revenue"] != 0, result["gross_profit"] / result["revenue"], 0)
    return result


def rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["customer_id", "recency", "frequency", "monetary", "rfm_score", "segment"])

    x = df.copy()
    x["order_date"] = pd.to_datetime(x["order_date"])
    snapshot = x["order_date"].max() + pd.Timedelta(days=1)
    rfm = x.groupby("customer_id").agg(
        recency=("order_date", lambda s: (snapshot - s.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("net_sales", "sum"),
    ).reset_index()

    # Rank-based scoring avoids qcut failures when many customers share values.
    rfm["R"] = pd.qcut(rfm["recency"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["rfm_score"] = rfm["R"] + rfm["F"] + rfm["M"]

    def label(score: int) -> str:
        if score >= 13:
            return "Champions"
        if score >= 10:
            return "Loyal"
        if score >= 7:
            return "Potential"
        if score >= 5:
            return "At Risk"
        return "Hibernating"

    rfm["segment"] = rfm["rfm_score"].map(label)
    return rfm


def yoy_growth(monthly_df: pd.DataFrame) -> float | None:
    if monthly_df.empty or len(monthly_df) < 13:
        return None
    x = monthly_df.sort_values("month").copy()
    current = x.iloc[-1]["revenue"]
    prior = x.iloc[-13]["revenue"]
    if prior == 0:
        return None
    return float(current / prior - 1)
