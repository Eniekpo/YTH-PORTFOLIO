from pathlib import Path
import ssl
from urllib.request import urlopen

import certifi
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "🏠 Predicting Real Estate Prices with Python and Scikit-learn"
DATA_URL = (
    "https://raw.githubusercontent.com/ageron/handson-ml/"
    "master/datasets/housing/housing.csv"
)
LOCAL_DATA_PATH = Path(__file__).resolve().parent / "housing.csv"
TARGET = "median_house_value"
CATEGORICAL_FEATURES = ["ocean_proximity"]
NUMERIC_FEATURES = [
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
RANDOM_STATE = 42


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 42%);
        }

        [data-testid="stSidebar"] {
            background: #0f172a;
        }

        [data-testid="stSidebar"] * {
            color: #e2e8f0;
        }

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label {
            color: #f8fafc !important;
            font-weight: 600;
        }

        .hero {
            padding: 1.65rem 1.8rem;
            border-radius: 20px;
            background:
                radial-gradient(circle at 90% 10%, rgba(56, 189, 248, 0.28), transparent 28%),
                linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
            color: #ffffff;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 12px 35px rgba(15, 23, 42, 0.12);
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(1.75rem, 3vw, 2.65rem);
            line-height: 1.15;
            letter-spacing: -0.025em;
        }

        .hero p {
            margin: 0.7rem 0 0 0;
            max-width: 900px;
            color: #cbd5e1;
            font-size: 1rem;
        }

        .section-title {
            font-size: 1.22rem;
            font-weight: 750;
            color: #0f172a;
            margin: 0.35rem 0 0.7rem 0;
        }

        .metric-card {
            border: 1px solid transparent;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            min-height: 108px;
            box-shadow: 0 5px 16px rgba(15, 23, 42, 0.07);
        }

        .metric-card--blue {
            background: #eff6ff;
            border-color: #bfdbfe;
        }

        .metric-card--green {
            background: #ecfdf5;
            border-color: #a7f3d0;
        }

        .metric-card--amber {
            background: #fffbeb;
            border-color: #fde68a;
        }

        .metric-card--rose {
            background: #fff1f2;
            border-color: #fecdd3;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.82rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-value {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 800;
            margin-top: 0.3rem;
        }

        .prediction-card {
            background: linear-gradient(135deg, #ecfeff 0%, #eff6ff 100%);
            border: 1px solid #bae6fd;
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            box-shadow: 0 8px 24px rgba(14, 116, 144, 0.08);
        }

        .prediction-label {
            color: #0e7490;
            font-size: 0.82rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .prediction-value {
            color: #0f172a;
            font-size: 2.45rem;
            font-weight: 850;
            margin: 0.15rem 0 0.25rem 0;
        }

        .muted {
            color: #64748b;
            font-size: 0.9rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e2e8f0;
            padding: 0.8rem 1rem;
            border-radius: 14px;
        }

        .block-container {
            padding-top: 1.7rem;
            padding-bottom: 3rem;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data and modelling utilities
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load the housing data from GitHub, with a local-file fallback."""
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(DATA_URL, context=ssl_context) as response:
            return pd.read_csv(response)
    except Exception:
        if LOCAL_DATA_PATH.exists():
            return pd.read_csv(LOCAL_DATA_PATH)
        raise


def make_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def make_estimator(model_name: str):
    if model_name == "Linear Regression":
        return LinearRegression()

    if model_name == "Gradient Boosting":
        return GradientBoostingRegressor(
            n_estimators=180,
            learning_rate=0.05,
            max_depth=3,
            loss="squared_error",
            random_state=RANDOM_STATE,
        )

    return RandomForestRegressor(
        n_estimators=250,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        min_samples_leaf=1,
    )


@st.cache_resource(show_spinner=False)
def train_model(model_name: str, data_signature: tuple):
    # Reload inside the cached resource so the cache key stays lightweight.
    df = load_data()

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            ("model", make_estimator(model_name)),
        ]
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    metrics = {
        "RMSE": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "MAE": float(mean_absolute_error(y_test, predictions)),
        "R2": float(r2_score(y_test, predictions)),
    }

    evaluation = X_test.copy()
    evaluation["Actual"] = y_test.values
    evaluation["Predicted"] = predictions
    evaluation["Residual"] = evaluation["Actual"] - evaluation["Predicted"]

    return pipeline, metrics, evaluation


def feature_influence_table(pipeline: Pipeline) -> tuple[pd.DataFrame | None, str]:
    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]

    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        return None, ""

    clean_names = [
        name.replace("numeric__", "").replace("categorical__", "")
        for name in feature_names
    ]

    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
        label = "Feature importance"
    elif hasattr(model, "coef_"):
        values = np.abs(np.ravel(model.coef_))
        label = "Absolute coefficient magnitude"
    else:
        return None, ""

    table = (
        pd.DataFrame({"Feature": clean_names, "Influence": values})
        .sort_values("Influence", ascending=False)
        .head(12)
    )
    return table, label


def metric_card(label: str, value: str, color: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card metric-card--{color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_location_chart(
    locations: pd.DataFrame,
    height: int = 390,
    marker_size: int = 5,
) -> None:
    longitude_min = float(locations["longitude"].min())
    longitude_max = float(locations["longitude"].max())
    latitude_min = float(locations["latitude"].min())
    latitude_max = float(locations["latitude"].max())
    longitude_padding = max((longitude_max - longitude_min) * 0.05, 0.1)
    latitude_padding = max((latitude_max - latitude_min) * 0.05, 0.1)

    fig = px.scatter(
        locations,
        x="longitude",
        y="latitude",
        render_mode="svg",
        opacity=0.65,
        labels={"longitude": "Longitude", "latitude": "Latitude"},
    )
    fig.update_traces(
        marker={"color": "#0284c7", "size": marker_size},
        showlegend=False,
    )
    fig.update_xaxes(
        range=[
            longitude_min - longitude_padding,
            longitude_max + longitude_padding,
        ],
        showgrid=True,
    )
    fig.update_yaxes(
        range=[
            latitude_min - latitude_padding,
            latitude_max + latitude_padding,
        ],
        showgrid=True,
    )
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=15, b=10),
        showlegend=False,
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


def hero() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{APP_TITLE}</h1>
            <p>
                An interactive machine-learning dashboard for exploring the California
                housing dataset, evaluating regression models, and estimating median
                house values from user-defined housing and location characteristics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------
try:
    data = load_data()
except Exception as exc:
    st.error(
        "⚠️ The dataset could not be loaded from GitHub and no local housing.csv "
        "file was found."
    )
    st.exception(exc)
    st.stop()

data_signature = (
    data.shape[0],
    data.shape[1],
    int(data.isna().sum().sum()),
)


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏠 Real Estate ML")
    st.caption("🧰 Python • Streamlit • Scikit-learn")
    st.markdown("---")

    page = st.radio(
        "🧭 Navigate",
        [
            "Overview",
            "Data Explorer",
            "Model Performance",
            "Price Predictor",
            "Methodology",
        ],
        format_func=lambda value: {
            "Overview": "📊 Overview",
            "Data Explorer": "🗂️ Data Explorer",
            "Model Performance": "📈 Model Performance",
            "Price Predictor": "🏡 Price Predictor",
            "Methodology": "🔬 Methodology",
        }[value],
        index=0,
    )

    st.markdown("---")
    st.caption("🗃️ Dataset")
    st.write("California Housing")
    st.caption(f"📋 {len(data):,} observations • {data.shape[1]} columns")

    st.markdown("---")
    st.caption(
        "Educational project. Predictions are model estimates from historical "
        "California housing data, not live property valuations."
    )


# -----------------------------------------------------------------------------
# Shared hero
# -----------------------------------------------------------------------------
hero()


# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    st.markdown('<div class="section-title">📌 Project snapshot</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("📋 Observations", f"{len(data):,}", "blue")
    with c2:
        metric_card("🧩 Predictor fields", f"{len(FEATURES)}", "green")
    with c3:
        metric_card("💵 Median house value", f"${data[TARGET].median():,.0f}", "amber")
    with c4:
        metric_card("🕳️ Missing cells", f"{int(data.isna().sum().sum()):,}", "rose")

    st.write("")

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown(
            '<div class="section-title">💰 Median house value distribution</div>',
            unsafe_allow_html=True,
        )
        fig = px.histogram(
            data,
            x=TARGET,
            nbins=45,
            labels={TARGET: "Median house value ($)"},
        )
        fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=15, b=10),
            bargap=0.04,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(
            '<div class="section-title">🌊 Ocean proximity mix</div>',
            unsafe_allow_html=True,
        )
        ocean_counts = (
            data["ocean_proximity"]
            .value_counts()
            .rename_axis("Ocean proximity")
            .reset_index(name="Count")
        )
        fig = px.bar(
            ocean_counts,
            x="Count",
            y="Ocean proximity",
            orientation="h",
        )
        fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=15, b=10),
            yaxis_title="",
            xaxis_title="Records",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="section-title">🗺️ Geographic distribution</div>',
        unsafe_allow_html=True,
    )
    map_sample = data[["latitude", "longitude"]].dropna().sample(
        n=min(4000, len(data)),
        random_state=RANDOM_STATE,
    )
    show_location_chart(map_sample)

    with st.expander("💡 What this application demonstrates"):
        st.markdown(
            """
            - Loading and inspecting a real-world regression dataset.
            - Handling missing numeric values and categorical variables.
            - Building reusable Scikit-learn preprocessing and modelling pipelines.
            - Evaluating models with RMSE, MAE, and R².
            - Turning a trained model into an interactive Streamlit prediction interface.
            """
        )


# -----------------------------------------------------------------------------
# Data Explorer
# -----------------------------------------------------------------------------
elif page == "Data Explorer":
    st.markdown(
        '<div class="section-title">🗂️ Explore the dataset</div>',
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2 = st.columns([0.8, 1.2])

    ocean_options = sorted(data["ocean_proximity"].dropna().unique().tolist())
    with filter_col1:
        selected_ocean = st.multiselect(
            "🌊 Ocean proximity",
            options=ocean_options,
            default=ocean_options,
        )

    min_value = int(data[TARGET].min())
    max_value = int(data[TARGET].max())

    with filter_col2:
        value_range = st.slider(
            "💵 Median house value range ($)",
            min_value=min_value,
            max_value=max_value,
            value=(min_value, max_value),
            step=5000,
        )

    filtered = data[
        data["ocean_proximity"].isin(selected_ocean)
        & data[TARGET].between(value_range[0], value_range[1])
    ].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("📋 Filtered records", f"{len(filtered):,}")
    c2.metric("💵 Average value", f"${filtered[TARGET].mean():,.0f}" if len(filtered) else "—")
    c3.metric("💰 Median income", f"{filtered['median_income'].median():.2f}" if len(filtered) else "—")

    tab1, tab2, tab3 = st.tabs(["📋 Table", "🔗 Relationships", "🧮 Correlation"])

    with tab1:
        st.dataframe(
            filtered,
            use_container_width=True,
            height=430,
        )
        st.download_button(
            "⬇️ Download filtered CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered_housing_data.csv",
            mime="text/csv",
        )

    with tab2:
        x_feature = st.selectbox(
            "↔️ X-axis feature",
            options=[
                "median_income",
                "housing_median_age",
                "total_rooms",
                "population",
                "latitude",
                "longitude",
            ],
            index=0,
        )

        sample = filtered.sample(
            n=min(5000, len(filtered)),
            random_state=RANDOM_STATE,
        ) if len(filtered) else filtered

        if len(sample):
            fig = px.scatter(
                sample,
                x=x_feature,
                y=TARGET,
                render_mode="svg",
                color="ocean_proximity",
                opacity=0.55,
                labels={TARGET: "Median house value ($)"},
            )
            fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records match the current filters.")

    with tab3:
        numeric_data = filtered.select_dtypes(include=np.number)
        if len(numeric_data):
            corr = numeric_data.corr(numeric_only=True)
            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                zmin=-1,
                zmax=1,
            )
            fig.update_layout(height=620, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records match the current filters.")


# -----------------------------------------------------------------------------
# Model Performance
# -----------------------------------------------------------------------------
elif page == "Model Performance":
    st.markdown(
        '<div class="section-title">📈 Train and evaluate a regression model</div>',
        unsafe_allow_html=True,
    )

    model_name = st.selectbox(
        "🤖 Model",
        ["Random Forest", "Gradient Boosting", "Linear Regression"],
        index=0,
        help="Choose a regression algorithm. Training results are cached for this session.",
    )

    with st.spinner(f"Training {model_name}..."):
        pipeline, metrics, evaluation = train_model(model_name, data_signature)

    m1, m2, m3 = st.columns(3)
    m1.metric("📉 RMSE", f"${metrics['RMSE']:,.0f}")
    m2.metric("📏 MAE", f"${metrics['MAE']:,.0f}")
    m3.metric("🎯 R²", f"{metrics['R2']:.3f}")

    st.caption(
        "Lower RMSE and MAE are better. R² closer to 1 indicates that the model "
        "explains more variation in the held-out test data."
    )

    tab1, tab2, tab3 = st.tabs(
        ["🎯 Actual vs Predicted", "📊 Residuals", "🧩 Feature Influence"]
    )

    with tab1:
        chart_data = evaluation.sample(
            n=min(3500, len(evaluation)),
            random_state=RANDOM_STATE,
        )
        fig = px.scatter(
            chart_data,
            x="Actual",
            y="Predicted",
            render_mode="svg",
            opacity=0.55,
            labels={
                "Actual": "Actual median house value ($)",
                "Predicted": "Predicted median house value ($)",
            },
        )
        axis_min = float(min(chart_data["Actual"].min(), chart_data["Predicted"].min()))
        axis_max = float(max(chart_data["Actual"].max(), chart_data["Predicted"].max()))
        fig.add_shape(
            type="line",
            x0=axis_min,
            y0=axis_min,
            x1=axis_max,
            y1=axis_max,
            line=dict(dash="dash"),
        )
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.histogram(
            evaluation,
            x="Residual",
            nbins=45,
            labels={"Residual": "Residual: actual − predicted ($)"},
        )
        fig.update_layout(
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
            bargap=0.04,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        influence, influence_label = feature_influence_table(pipeline)
        if influence is not None:
            influence = influence.sort_values("Influence", ascending=True)
            fig = px.bar(
                influence,
                x="Influence",
                y="Feature",
                orientation="h",
                labels={"Influence": influence_label},
            )
            fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            if model_name == "Linear Regression":
                st.caption(
                    "For Linear Regression, the chart shows absolute coefficient "
                    "magnitude after preprocessing; it should not be interpreted as "
                    "causal importance."
                )
        else:
            st.info("Feature influence is not available for this model.")


# -----------------------------------------------------------------------------
# Price Predictor
# -----------------------------------------------------------------------------
elif page == "Price Predictor":
    st.markdown(
        '<div class="section-title">🏡 Interactive house-value prediction</div>',
        unsafe_allow_html=True,
    )

    model_name = st.selectbox(
        "🤖 Prediction model",
        ["Random Forest", "Gradient Boosting", "Linear Regression"],
        index=0,
    )

    with st.spinner(f"Preparing {model_name}..."):
        pipeline, metrics, _ = train_model(model_name, data_signature)

    medians = data[NUMERIC_FEATURES].median(numeric_only=True)

    st.markdown("#### 🏠 Property and area characteristics")

    row1 = st.columns(3)
    with row1[0]:
        longitude = st.number_input(
            "📍 Longitude",
            min_value=float(data["longitude"].min()),
            max_value=float(data["longitude"].max()),
            value=float(medians["longitude"]),
            step=0.01,
            format="%.2f",
        )
    with row1[1]:
        latitude = st.number_input(
            "📍 Latitude",
            min_value=float(data["latitude"].min()),
            max_value=float(data["latitude"].max()),
            value=float(medians["latitude"]),
            step=0.01,
            format="%.2f",
        )
    with row1[2]:
        housing_median_age = st.number_input(
            "🏗️ Median housing age (years)",
            min_value=float(data["housing_median_age"].min()),
            max_value=float(data["housing_median_age"].max()),
            value=float(medians["housing_median_age"]),
            step=1.0,
        )

    row2 = st.columns(3)
    with row2[0]:
        total_rooms = st.number_input(
            "🚪 Total rooms",
            min_value=1.0,
            max_value=float(data["total_rooms"].max()),
            value=float(medians["total_rooms"]),
            step=10.0,
        )
    with row2[1]:
        total_bedrooms = st.number_input(
            "🛏️ Total bedrooms",
            min_value=1.0,
            max_value=float(data["total_bedrooms"].max(skipna=True)),
            value=float(medians["total_bedrooms"]),
            step=5.0,
        )
    with row2[2]:
        households = st.number_input(
            "👨‍👩‍👧‍👦 Households",
            min_value=1.0,
            max_value=float(data["households"].max()),
            value=float(medians["households"]),
            step=5.0,
        )

    row3 = st.columns(3)
    with row3[0]:
        population = st.number_input(
            "👥 Population",
            min_value=1.0,
            max_value=float(data["population"].max()),
            value=float(medians["population"]),
            step=10.0,
        )
    with row3[1]:
        median_income = st.number_input(
            "💰 Median income (dataset units)",
            min_value=float(data["median_income"].min()),
            max_value=float(data["median_income"].max()),
            value=float(medians["median_income"]),
            step=0.10,
            format="%.4f",
            help="In this dataset, median income is expressed in units of roughly $10,000.",
        )
    with row3[2]:
        ocean_options = sorted(data["ocean_proximity"].dropna().unique().tolist())
        ocean_mode = data["ocean_proximity"].mode().iloc[0]
        ocean_proximity = st.selectbox(
            "🌊 Ocean proximity",
            options=ocean_options,
            index=ocean_options.index(ocean_mode),
        )

    prediction_input = pd.DataFrame(
        [
            {
                "longitude": longitude,
                "latitude": latitude,
                "housing_median_age": housing_median_age,
                "total_rooms": total_rooms,
                "total_bedrooms": total_bedrooms,
                "population": population,
                "households": households,
                "median_income": median_income,
                "ocean_proximity": ocean_proximity,
            }
        ]
    )

    st.write("")
    predict_col, map_col = st.columns([1.05, 0.95], gap="large")

    with predict_col:
        predicted_value = float(pipeline.predict(prediction_input)[0])
        dataset_median = float(data[TARGET].median())
        difference = predicted_value - dataset_median
        direction = "above" if difference >= 0 else "below"

        st.markdown(
            f"""
            <div class="prediction-card">
                <div class="prediction-label">💵 Estimated median house value</div>
                <div class="prediction-value">${predicted_value:,.0f}</div>
                <div class="muted">
                    Using {model_name}. This estimate is
                    <strong>${abs(difference):,.0f} {direction}</strong>
                    the dataset median of ${dataset_median:,.0f}.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.caption(
            f"Hold-out performance for this model: RMSE ${metrics['RMSE']:,.0f}, "
            f"MAE ${metrics['MAE']:,.0f}, R² {metrics['R2']:.3f}."
        )

        with st.expander("🔎 View model input"):
            st.dataframe(prediction_input, use_container_width=True)

    with map_col:
        st.markdown("#### 📍 Selected location")
        show_location_chart(
            pd.DataFrame({"latitude": [latitude], "longitude": [longitude]}),
            height=330,
            marker_size=12,
        )

    st.info(
        "Use this prediction as a machine-learning demonstration only. The dataset "
        "describes historical California districts and does not include current "
        "transactions, interest rates, renovations, exact addresses, or live market conditions."
    )


# -----------------------------------------------------------------------------
# Methodology
# -----------------------------------------------------------------------------
else:
    st.markdown(
        '<div class="section-title">🔬 Methodology and project architecture</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown(
            """
            #### 🎯 1. Problem definition
            Predict `median_house_value`, a continuous target, from geographic,
            demographic, housing-stock, income, and ocean-proximity variables.

            #### 🧹 2. Data preparation
            - Numeric missing values are imputed with the median.
            - Numeric predictors are standardized.
            - `ocean_proximity` is one-hot encoded.
            - Preprocessing is contained in a Scikit-learn `Pipeline`.

            #### 🧪 3. Train/test design
            The application uses an 80/20 random train/test split with
            `random_state=42` for reproducibility.
            """
        )

    with right:
        st.markdown(
            """
            #### 🤖 4. Models
            - **Linear Regression** provides an interpretable baseline.
            - **Random Forest** captures nonlinearities and interactions.
            - **Gradient Boosting** builds an additive sequence of regression trees.

            #### 📊 5. Evaluation
            - **RMSE** penalizes larger errors more strongly.
            - **MAE** reports average absolute prediction error.
            - **R²** summarizes explained variation on held-out observations.

            #### 🚀 6. Deployment layer
            Streamlit provides the interactive interface while cached functions
            reduce repeated data-loading and model-training work.
            """
        )

    st.markdown("---")
    st.markdown("#### 🧾 Dataset fields")

    field_table = pd.DataFrame(
        {
            "Field": [
                "longitude",
                "latitude",
                "housing_median_age",
                "total_rooms",
                "total_bedrooms",
                "population",
                "households",
                "median_income",
                "ocean_proximity",
                "median_house_value",
            ],
            "Role": [
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Predictor",
                "Target",
            ],
            "Type": [
                "Numeric",
                "Numeric",
                "Numeric",
                "Numeric",
                "Numeric",
                "Numeric",
                "Numeric",
                "Numeric",
                "Categorical",
                "Numeric",
            ],
        }
    )
    st.dataframe(field_table, use_container_width=True, hide_index=True)

    st.markdown("---")
    
