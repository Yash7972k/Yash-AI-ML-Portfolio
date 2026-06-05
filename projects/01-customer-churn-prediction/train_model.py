"""
Train and save a Random Forest model for a given industry.
Usage:
    python train_model.py --industry telecom
    python train_model.py --industry banking
    python train_model.py --industry ecommerce
"""

import argparse
import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

from industries import INDUSTRIES
from utils.preprocessing import load_and_clean


def train(industry_key: str):
    industry_cls = INDUSTRIES.get(industry_key)
    if not industry_cls:
        print(f"❌ Unknown industry: {industry_key}. Choose from: {list(INDUSTRIES.keys())}")
        return

    industry = industry_cls()
    dataset_path = industry.dataset

    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at '{dataset_path}'.")
        print(f"   Please place your dataset at: {dataset_path}")
        return

    print(f"\n🚀 Training model for: {industry.name}")
    print(f"   Dataset: {dataset_path}")

    # Load and clean, also get the encoders
    df, categorical_encoders = load_and_clean(dataset_path, industry)
    target = industry.target_column

    X = df.drop(columns=[target])
    y = df[target]

    print(f"   Features: {len(X.columns)} | Samples: {len(X)}")
    print(f"   Class distribution: {dict(y.value_counts())}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    # Handle case where predict_proba returns only one column
    y_proba_result = model.predict_proba(X_test)
    if y_proba_result.shape[1] == 1:
        y_prob = y_proba_result[:, 0]
    else:
        y_prob = y_proba_result[:, 1]

    print("\n📊 Model Evaluation:")
    print(classification_report(y_test, y_pred))
    try:
        auc = roc_auc_score(y_test, y_prob)
        print(f"   ROC-AUC Score: {auc:.4f}")
    except Exception as e:
        print(f"   ROC-AUC Score: Could not compute ({str(e)})")

    os.makedirs("model", exist_ok=True)
    model_path = f"model/{industry_key}_model.pkl"
    columns_path = f"model/{industry_key}_columns.pkl"
    encoders_path = f"model/{industry_key}_encoders.pkl"

    # Save model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save column names
    with open(columns_path, "wb") as f:
        pickle.dump(list(X.columns), f)

    # Save categorical encoders
    with open(encoders_path, "wb") as f:
        pickle.dump(categorical_encoders, f)

    print(f"\n✅ Model saved → {model_path}")
    print(f"✅ Columns saved → {columns_path}")
    print(f"✅ Encoders saved → {encoders_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train churn model for an industry")
    parser.add_argument(
        "--industry",
        type=str,
        default="telecom",
        choices=list(INDUSTRIES.keys()),
        help="Industry to train model for",
    )
    args = parser.parse_args()
    train(args.industry)
