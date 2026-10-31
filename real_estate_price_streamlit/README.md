# Predicting Real Estate Prices with Python and Scikit-learn

A professional Streamlit interface for exploring the California housing dataset,
training regression models, evaluating prediction performance, and estimating
median house values interactively.

## Features

- Executive overview of the housing dataset
- Interactive dataset filters and CSV export
- Relationship plots and correlation analysis
- Three Scikit-learn regression models:
  - Random Forest
  - Gradient Boosting
  - Linear Regression
- Evaluation with RMSE, MAE, and R²
- Actual-vs-predicted and residual diagnostics
- Feature-influence view
- Interactive prediction form
- Map display for selected latitude and longitude
- Cached data loading and model training
- Local `housing.csv` fallback if the remote URL is unavailable
- Verified HTTPS using the `certifi` CA bundle for consistent certificate trust

## Dataset

Source:

https://raw.githubusercontent.com/ageron/handson-ml/master/datasets/housing/housing.csv

Target variable:

`median_house_value`

Predictors:

`longitude`, `latitude`, `housing_median_age`, `total_rooms`,
`total_bedrooms`, `population`, `households`, `median_income`,
and `ocean_proximity`.

## Run locally

1. Open a terminal in this project folder.
2. Create a virtual environment if desired.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run app.py
```

Streamlit will display a local URL, usually `http://localhost:8501`.

## Modelling workflow

The app uses an 80/20 train/test split with `random_state=42`.

Numeric variables:
- median imputation
- standard scaling

Categorical variable:
- most-frequent imputation
- one-hot encoding

The preprocessing steps and regression model are combined in a Scikit-learn
`Pipeline`, which ensures that the exact same transformations are applied during
training and prediction.

## Important note

This application is intended for machine-learning education and portfolio use.
The source dataset contains historical California district-level housing data and
should not be treated as a live real-estate valuation service.
