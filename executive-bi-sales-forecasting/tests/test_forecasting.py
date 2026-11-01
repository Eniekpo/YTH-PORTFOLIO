import numpy as np
import pandas as pd

from src.forecasting import forecast_monthly_revenue


def test_forecast_shape_and_nonnegative_bounds():
    months = pd.date_range("2023-01-01", periods=36, freq="MS")
    revenue = 100_000 + np.arange(36) * 1_500 + 12_000 * np.sin(2 * np.pi * np.arange(36) / 12)
    df = pd.DataFrame({"month": months, "revenue": revenue})
    forecast, metrics = forecast_monthly_revenue(df, periods=6)
    assert len(forecast) == 6
    assert set(["month", "forecast", "lower", "upper"]).issubset(forecast.columns)
    assert (forecast["lower"] >= 0).all()
    assert metrics["model"]
