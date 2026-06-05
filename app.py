"""
Customer Churn Prediction — Real World Edition
Multi-industry: Telecom | Banking | E-commerce
"""

import os
import pickle
import streamlit as st
import pandas as pd

from industries import INDUSTRIES
from utils.preprocessing import encode_input, encode_bulk
from utils.retention import get_retention_tips, get_risk_color, get_risk_emoji, get_risk_level
from utils.visualizations import (
    plot_churn_gauge,
    plot_feature_importance,
    plot_churn_distribution,
    plot_bulk_results,
)

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Predictor Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #1a1a2e; }
    .risk-badge-high   { background:#e74c3c; color:white; padding:6px 16px; border-radius:20px; font-weight:700; }
    .risk-badge-medium { background:#f39c12; color:white; padding:6px 16px; border-radius:20px; font-weight:700; }
    .risk-badge-low    { background:#2ecc71; color:white; padding:6px 16px; border-radius:20px; font-weight:700; }
    .tip-card { background:#f8f9fa; border-left:4px solid #3498db; padding:10px 15px; margin:6px 0; border-radius:4px; }
    .section-header { font-size:1.2rem; font-weight:700; margin-top:1rem; color:#2c3e50; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Load Model ───────────────────────────────────────────────────────
@st.cache_resource
def load_model(industry_key: str):
    model_path = f"model/{industry_key}_model.pkl"
    columns_path = f"model/{industry_key}_columns.pkl"
    encoders_path = f"model/{industry_key}_encoders.pkl"
    
    if not os.path.exists(model_path):
        return None, None, None
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(columns_path, "rb") as f:
        columns = pickle.load(f)
    
    # Load encoders if they exist (for new trained models)
    categorical_encoders = {}
    if os.path.exists(encoders_path):
        with open(encoders_path, "rb") as f:
            categorical_encoders = pickle.load(f)
    
    return model, columns, categorical_encoders


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔮 Churn Predictor Pro")
    st.markdown("---")

    industry_labels = {k: v().name for k, v in INDUSTRIES.items()}
    selected_label = st.selectbox("Select Industry", list(industry_labels.values()))
    industry_key = [k for k, v in industry_labels.items() if v == selected_label][0]
    industry = INDUSTRIES[industry_key]()

    st.markdown("---")
    mode = st.radio("Prediction Mode", ["Single Customer", "Bulk CSV Upload"])
    st.markdown("---")
    st.success("✅ Models Trained & Ready!")


# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown(f"<div class='main-title'>🔮 Churn Predictor Pro — {industry.name}</div>", unsafe_allow_html=True)
st.markdown("Predict customer churn with real-world retention strategies.")
st.markdown("---")

model, trained_columns, categorical_encoders = load_model(industry_key)

if model is None:
    st.warning(f"⚠️ No trained model found for **{industry.name}**.")
    st.code(f"python train_model.py --industry {industry_key}")
    st.stop()

# ─── Single Customer Prediction ──────────────────────────────────────────────
if mode == "Single Customer":
    st.subheader("📋 Enter Customer Details")

    fields = industry.fields
    input_data = {}
    cols = st.columns(2)

    for i, (field_key, field_cfg) in enumerate(fields.items()):
        with cols[i % 2]:
            label = field_cfg["label"]
            ftype = field_cfg["type"]
            if ftype == "number":
                val = st.number_input(
                    label,
                    min_value=float(field_cfg["min"]),
                    max_value=float(field_cfg["max"]),
                    value=float(field_cfg["default"]),
                    step=1.0,
                )
            elif ftype == "select":
                val = st.selectbox(label, field_cfg["options"], index=field_cfg["options"].index(field_cfg["default"]))
            input_data[field_key] = val

    st.markdown("---")
    if st.button("🔮 Predict Churn Risk", use_container_width=True, type="primary"):
        input_df = encode_input(input_data, industry, trained_columns, categorical_encoders)
        proba_result = model.predict_proba(input_df)[0]
        # Handle case where predict_proba returns only one column
        prob = proba_result[1] if len(proba_result) > 1 else proba_result[0]
        risk = get_risk_level(prob)
        emoji = get_risk_emoji(prob)
        tips = get_retention_tips(prob, industry)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(plot_churn_gauge(prob), use_container_width=True)

        with col2:
            st.markdown(f"### {emoji} Churn Probability: **{prob*100:.1f}%**")
            st.markdown(f"<span class='risk-badge-{risk}'>{risk.upper()} RISK</span>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### 💡 Retention Suggestions")
            for tip in tips:
                st.markdown(f"<div class='tip-card'>{tip}</div>", unsafe_allow_html=True)

        with st.expander("📊 Feature Importance"):
            st.plotly_chart(plot_feature_importance(model, trained_columns), use_container_width=True)

# ─── Bulk CSV Prediction ──────────────────────────────────────────────────────
else:
    st.subheader("📂 Upload Customer CSV for Bulk Prediction")
    st.markdown(f"Upload a CSV with customer data. The model will predict churn for each row.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        st.markdown(f"**Rows loaded:** {len(raw_df)}")
        st.dataframe(raw_df.head(5), use_container_width=True)

        if st.button("🔮 Predict All", use_container_width=True, type="primary"):
            with st.spinner("Running predictions..."):
                processed = encode_bulk(raw_df.copy(), industry, trained_columns, categorical_encoders)
                proba_result = model.predict_proba(processed)
                # Handle case where predict_proba returns only one column
                probs = proba_result[:, 1] if proba_result.shape[1] > 1 else proba_result[:, 0]
                raw_df["Churn Probability (%)"] = (probs * 100).round(1)
                raw_df["Risk Level"] = [get_risk_level(p) + " " + get_risk_emoji(p) for p in probs]

            st.success(f"✅ Predicted {len(raw_df)} customers!")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 High Risk", int((probs >= 0.70).sum()))
            col2.metric("🟠 Medium Risk", int(((probs >= 0.40) & (probs < 0.70)).sum()))
            col3.metric("🟢 Low Risk", int((probs < 0.40).sum()))

            st.plotly_chart(plot_bulk_results(raw_df), use_container_width=True)
            st.dataframe(raw_df, use_container_width=True)

            csv_out = raw_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Results CSV",
                data=csv_out,
                file_name=f"{industry_key}_churn_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )
