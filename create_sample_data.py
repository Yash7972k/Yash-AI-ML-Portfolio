"""
Generate sample datasets matching the actual industry requirements.
"""

import pandas as pd
import numpy as np

# ─── Sample Telecom Data ─────────────────────────────────────────────────────
telecom_data = {
    'customerID': [f'ID_{i}' for i in range(2000)],
    'gender': np.random.choice(['Male', 'Female'], 2000),
    'SeniorCitizen': np.random.choice([0, 1], 2000),
    'Partner': np.random.choice(['Yes', 'No'], 2000),
    'Dependents': np.random.choice(['Yes', 'No'], 2000),
    'tenure': np.random.randint(0, 73, 2000),
    'PhoneService': np.random.choice(['Yes', 'No'], 2000),
    'MultipleLines': np.random.choice(['Yes', 'No', 'No phone service'], 2000),
    'InternetService': np.random.choice(['DSL', 'Fiber optic', 'No'], 2000),
    'OnlineSecurity': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'OnlineBackup': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'DeviceProtection': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'TechSupport': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'StreamingTV': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'StreamingMovies': np.random.choice(['Yes', 'No', 'No internet service'], 2000),
    'Contract': np.random.choice(['Month-to-month', 'One year', 'Two year'], 2000),
    'PaperlessBilling': np.random.choice(['Yes', 'No'], 2000),
    'PaymentMethod': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'], 2000),
    'MonthlyCharges': np.random.uniform(20, 150, 2000),
    'TotalCharges': np.random.uniform(100, 8000, 2000),
    'Churn': np.random.choice(['Yes', 'No'], 2000, p=[0.3, 0.7]),  # 30% churn
}

df_telecom = pd.DataFrame(telecom_data)
df_telecom.to_csv('data/WA_Fn-UseC_-Telco-Customer-Churn.csv', index=False)
print("✅ Created: data/WA_Fn-UseC_-Telco-Customer-Churn.csv (2000 rows)")

# ─── Sample Banking Data ─────────────────────────────────────────────────────
banking_data = {
    'RowNumber': range(2000),
    'CustomerId': range(10000, 12000),
    'Surname': [f'Customer_{i}' for i in range(2000)],
    'CreditScore': np.random.randint(300, 850, 2000),
    'Geography': np.random.choice(['France', 'Germany', 'Spain'], 2000),
    'Gender': np.random.choice(['Male', 'Female'], 2000),
    'Age': np.random.randint(18, 92, 2000),
    'Tenure': np.random.randint(0, 11, 2000),
    'Balance': np.random.uniform(0, 250000, 2000),
    'NumOfProducts': np.random.randint(1, 5, 2000),
    'HasCrCard': np.random.choice([0, 1], 2000),
    'IsActiveMember': np.random.choice([0, 1], 2000),
    'EstimatedSalary': np.random.uniform(11000, 200000, 2000),
    'Exited': np.random.choice([0, 1], 2000, p=[0.8, 0.2]),  # 20% churn
}

df_banking = pd.DataFrame(banking_data)
df_banking.to_csv('data/bank_churn.csv', index=False)
print("✅ Created: data/bank_churn.csv (2000 rows)")

# ─── Sample E-commerce Data ──────────────────────────────────────────────────
ecommerce_data = {
    'CustomerID': [f'CUST_{i}' for i in range(2000)],
    'Tenure': np.random.randint(1, 61, 2000),
    'CityTier': np.random.choice(['1', '2', '3'], 2000),
    'WarehouseToHome': np.random.randint(5, 127, 2000),
    'HourSpendOnApp': np.random.randint(0, 10, 2000),
    'NumberOfDeviceRegistered': np.random.randint(1, 7, 2000),
    'SatisfactionScore': np.random.randint(1, 6, 2000),
    'NumberofAddress': np.random.randint(1, 21, 2000),
    'Complain': np.random.choice(['Yes', 'No'], 2000, p=[0.2, 0.8]),
    'OrderAmountHikeFromLastYear': np.random.randint(0, 101, 2000),
    'CouponUsed': np.random.randint(0, 17, 2000),
    'OrderCount': np.random.randint(1, 20, 2000),
    'DaySinceLastOrder': np.random.randint(0, 47, 2000),
    'CashbackAmount': np.random.uniform(0, 326, 2000),
    'PreferredLoginDevice': np.random.choice(['Mobile Phone', 'Computer', 'Tablet'], 2000),
    'PreferredPaymentMode': np.random.choice(['Debit Card', 'UPI', 'Credit Card', 'Cash on Delivery', 'E wallet'], 2000),
    'Gender': np.random.choice(['Male', 'Female'], 2000),
    'PreferedOrderCat': np.random.choice(['Laptop & Accessory', 'Mobile', 'Fashion', 'Grocery', 'Others'], 2000),
    'MaritalStatus': np.random.choice(['Single', 'Married', 'Divorced'], 2000),
    'Churn': np.random.choice(['Yes', 'No'], 2000, p=[0.25, 0.75]),  # 25% churn
}

df_ecommerce = pd.DataFrame(ecommerce_data)
df_ecommerce.to_csv('data/ecommerce_churn.csv', index=False)
print("✅ Created: data/ecommerce_churn.csv (2000 rows)")

print("\n✨ All sample datasets created successfully!")
print("📊 Dataset sizes: 2000 samples each with realistic churn distributions")

