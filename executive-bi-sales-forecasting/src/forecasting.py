from __future__ import annotations

import warnings
import numpy as np
import pandas as pd


def forecast_monthly_revenue(monthly_df: pd.DataFrame, periods: int = 6) -> tuple[pd.DataFrame, dict]:
    """Forecast revenue with Holt-Winters; gracefully fall back to trend projection."""
    if monthly_df.empty:
        return pd.DataFrame(columns=["month", "forecast", "lower", "upper"]), {"model": "No data", "mae": None, "mape": None}

    series = monthly_df[["month", "revenue"]].dropna().copy().sort_values("month")
    series["month"] = pd.to_datetime(series["month"])
    y = series.set_index("month")["revenue"].asfreq("MS")
    y = y.interpolate(limit_direction="both")

    next_index = pd.date_range(y.index.max() + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    model_name = "Linear trend fallback"
    fitted = None

    if len(y) >= 24:
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = ExponentialSmoothing(
                    y,
                    trend="add",
                    seasonal="mul",
                    seasonal_periods=12,
                    initialization_method="estimated",
                )
                fitted = model.fit(optimized=True)
            forecast = fitted.forecast(periods)
            model_name = "Holt-Winters (additive trend, multiplicative seasonality)"
        except Exception:
            fitted = None

    if fitted is None:
        x = np.arange(len(y), dtype=float)
        coeffs = np.polyfit(x, y.values, deg=1)
        future_x = np.arange(len(y), len(y) + periods, dtype=float)
        forecast = pd.Series(np.polyval(coeffs, future_x), index=next_index)

    residuals = None
    mae = None
    mape = None
    if fitted is not None:
        fitted_values = pd.Series(fitted.fittedvalues, index=y.index)
        residuals = (y - fitted_values).dropna()
        mae = float(np.mean(np.abs(residuals))) if len(residuals) else None
        nonzero = y.replace(0, np.nan)
        mape_series = ((y - fitted_values).abs() / nonzero).dropna()
        mape = float(mape_series.mean()) if len(mape_series) else None
    else:
        fit = np.polyval(np.polyfit(np.arange(len(y)), y.values, 1), np.arange(len(y)))
        residuals = y.values - fit
        mae = float(np.mean(np.abs(residuals))) if len(residuals) else None
        mape_vals = np.abs(residuals) / np.where(y.values == 0, np.nan, y.values)
        mape = float(np.nanmean(mape_vals)) if np.isfinite(mape_vals).any() else None

    sigma = float(np.nanstd(residuals)) if residuals is not None and len(residuals) else 0.0
    out = pd.DataFrame({
        "month": next_index,
        "forecast": np.asarray(forecast, dtype=float),
    })
    out["lower"] = np.maximum(0, out["forecast"] - 1.96 * sigma)
    out["upper"] = out["forecast"] + 1.96 * sigma

    metrics = {"model": model_name, "mae": mae, "mape": mape}
    return out, metrics
