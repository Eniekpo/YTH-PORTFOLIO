import pandas as pd

from src.analytics import calculate_kpis, monthly_performance, rfm_segmentation


def sample_sales():
    return pd.DataFrame({
        "order_id": ["A", "A", "B", "C"],
        "order_date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-02-01", "2024-02-15"]),
        "customer_id": [1, 1, 2, 1],
        "quantity": [1, 2, 1, 1],
        "gross_sales": [100, 200, 150, 120],
        "return_amount": [0, 0, 10, 0],
        "net_sales": [100, 200, 140, 120],
        "gross_profit": [40, 80, 50, 45],
    })


def test_calculate_kpis():
    k = calculate_kpis(sample_sales())
    assert k["orders"] == 3
    assert k["customers"] == 2
    assert k["units"] == 5
    assert round(k["revenue"], 2) == 560.00
    assert round(k["gross_profit"], 2) == 215.00


def test_monthly_performance():
    out = monthly_performance(sample_sales())
    assert len(out) == 2
    assert out.iloc[0]["revenue"] == 300
    assert out.iloc[1]["revenue"] == 260


def test_rfm_segmentation_has_expected_columns():
    out = rfm_segmentation(sample_sales())
    assert {"recency", "frequency", "monetary", "rfm_score", "segment"}.issubset(out.columns)
