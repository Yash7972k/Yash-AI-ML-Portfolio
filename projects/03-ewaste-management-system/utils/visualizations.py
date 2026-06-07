import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_waste_by_type(df):
    counts = df["item_type"].value_counts().reset_index()
    counts.columns = ["Item Type", "Count"]
    fig = px.bar(counts, x="Item Type", y="Count",
                 color="Count", color_continuous_scale="Greens",
                 title="E-Waste Collected by Type")
    return fig

def plot_status_distribution(df):
    counts = df["status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    color_map = {"Pending": "#f59e0b", "Collected": "#3b82f6", "Recycled": "#22c55e"}
    fig = px.pie(counts, names="Status", values="Count",
                 color="Status", color_discrete_map=color_map,
                 title="Submission Status Distribution")
    return fig

def plot_priority_distribution(df):
    counts = df["priority"].value_counts().reset_index()
    counts.columns = ["Priority", "Count"]
    color_map = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}
    fig = px.pie(counts, names="Priority", values="Count",
                 color="Priority", color_discrete_map=color_map,
                 title="Recycling Priority Distribution")
    return fig

def plot_co2_trend(df):
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["co2_saved"].sum().reset_index()
    fig = px.area(daily, x="date", y="co2_saved",
                  title="Daily CO₂ Saved (kg)",
                  color_discrete_sequence=["#22c55e"])
    return fig

def plot_monthly_submissions(df):
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
    monthly = df.groupby("month").size().reset_index(name="submissions")
    fig = px.bar(monthly, x="month", y="submissions",
                 color="submissions", color_continuous_scale="Greens",
                 title="Monthly Submissions")
    return fig

def plot_map(df):
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon",
        hover_name="name",
        hover_data=["address", "city", "capacity"],
        color="status",
        color_discrete_map={"Active": "#22c55e", "Full": "#ef4444"},
        size_max=15, zoom=10,
        title="E-Waste Collection Points"
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig
