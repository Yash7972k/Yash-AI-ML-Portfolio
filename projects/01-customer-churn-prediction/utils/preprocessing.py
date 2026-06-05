import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle


def load_and_clean(dataset_path: str, industry) -> tuple:
    """
    Load dataset, clean, encode categoricals, and return df + encoders.
    Returns: (df, categorical_encoders)
    """
    df = pd.read_csv(dataset_path)

    # Drop irrelevant columns
    df.drop(columns=[c for c in industry.drop_columns if c in df.columns], inplace=True)

    target = industry.target_column

    # Fill missing numeric values
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # Identify categorical columns (excluding target)
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if target in cat_cols:
        cat_cols.remove(target)

    # Fill missing categorical values
    for col in cat_cols:
        df[col] = df[col].fillna("Unknown")

    # Encode target column FIRST
    if target in df.columns:
        if df[target].dtype == object:
            df[target] = df[target].fillna("No")
            df[target] = df[target].map({"Yes": 1, "No": 0})
            # For banking: 0 = No churn, 1 = Exited
            df[target] = pd.to_numeric(df[target], errors='coerce').fillna(0).astype(int)

    # Label-encode categorical columns and save encoders
    categorical_encoders = {}
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            categorical_encoders[col] = le

    return df, categorical_encoders


def encode_input(input_dict: dict, industry, trained_columns: list, categorical_encoders: dict) -> pd.DataFrame:
    """
    Encode a single customer input using the trained encoders.
    """
    row = {}
    
    for col in trained_columns:
        if col in input_dict:
            val = input_dict[col]
            
            # If this column was label-encoded during training, use the encoder
            if col in categorical_encoders:
                try:
                    # Get the encoder for this column
                    le = categorical_encoders[col]
                    # Check if value is in the encoder's classes
                    if val in le.classes_:
                        row[col] = le.transform([val])[0]
                    else:
                        # Unknown category: use the most common class (0)
                        row[col] = 0
                except Exception:
                    row[col] = 0
            else:
                # Numeric column: convert to float
                try:
                    row[col] = float(val)
                except (ValueError, TypeError):
                    row[col] = 0
        else:
            row[col] = 0

    return pd.DataFrame([row])


def encode_bulk(df: pd.DataFrame, industry, trained_columns: list, categorical_encoders: dict) -> pd.DataFrame:
    """
    Encode a bulk CSV for batch prediction using trained encoders.
    """
    # Drop target column if present
    target = industry.target_column
    if target in df.columns:
        df = df.drop(columns=[target])

    # Drop irrelevant columns
    df.drop(columns=[c for c in industry.drop_columns if c in df.columns], inplace=True)

    # Process categorical columns
    for col in df.select_dtypes(include=["object"]).columns:
        if col in categorical_encoders:
            le = categorical_encoders[col]
            # Apply encoding with fallback for unknown values
            df[col] = df[col].apply(
                lambda x: le.transform([str(x)])[0] if str(x) in le.classes_ else 0
            )
        else:
            # Simple yes/no mapping for unmapped categoricals
            df[col] = df[col].map({"Yes": 1, "No": 0}).fillna(0)

    # Fill any NaN values
    df = df.fillna(0)

    # Ensure all trained columns exist and in correct order
    for col in trained_columns:
        if col not in df.columns:
            df[col] = 0

    return df[trained_columns]

