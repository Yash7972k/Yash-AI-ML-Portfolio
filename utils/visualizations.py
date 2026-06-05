import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def plot_churn_gauge(probability: float) -> go.Figure:
    """Gauge chart showing churn probability."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(probability * 100, 1),
        title={"text": "Churn Risk Score", "font": {"size": 20}},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 40], "color": "#2ecc71"},
                {"range": [40, 70], "color": "#f39c12"},
                {"range": [70, 100], "color": "#e74c3c"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": probability * 100,
            },
        },
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=20))
    return fig


def plot_feature_importance(model, feature_names: list) -> go.Figure:
    """Horizontal bar chart of top 15 feature importances."""
    importances = model.feature_importances_
    feat_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    feat_df = feat_df.sort_values("Importance", ascending=True).tail(15)

    fig = px.bar(
        feat_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top 15 Feature Importances",
        color="Importance",
        color_continuous_scale="Blues",
    )
    fig.update_layout(height=450, margin=dict(t=40, b=20))
    return fig


def plot_churn_distribution(df: pd.DataFrame, target_col: str) -> go.Figure:
    """Pie chart of churn vs non-churn in dataset."""
    counts = df[target_col].value_counts()
    labels = ["No Churn", "Churn"] if 0 in counts.index else counts.index.tolist()
    fig = go.Figure(go.Pie(
        labels=labels,
        values=counts.values,
        hole=0.4,
        marker_colors=["#2ecc71", "#e74c3c"],
    ))
    fig.update_layout(title="Dataset Churn Distribution", height=350)
    return fig


def plot_bulk_results(results_df: pd.DataFrame) -> go.Figure:
    """Histogram of churn probabilities for bulk prediction."""
    fig = px.histogram(
        results_df,
        x="Churn Probability (%)",
        nbins=20,
        title="Churn Risk Distribution (Bulk Prediction)",
        color_discrete_sequence=["#3498db"],
    )
    fig.update_layout(height=350, margin=dict(t=40, b=20))
    return fig
