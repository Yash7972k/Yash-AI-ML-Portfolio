# 🔮 Customer Churn Prediction — Real World Edition

A production-style multi-industry customer churn prediction app built with Python, Scikit-learn, and Streamlit.

---

## 🏗️ Project Structure

```
customer-churn-realworld/
├── app.py                   ← Main Streamlit app (industry selector, single & bulk prediction)
├── train_model.py           ← Train models per industry
│
├── industries/
│   ├── __init__.py
│   ├── telecom.py           ← Telecom fields + retention tips
│   ├── banking.py           ← Banking fields + retention tips
│   └── ecommerce.py         ← Ecommerce fields + retention tips
│
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py     ← Data cleaning & encoding
│   ├── visualizations.py    ← Plotly charts
│   └── retention.py         ← Retention strategy engine
│
├── data/                    ← Place your CSV datasets here
├── model/                   ← Auto-generated after training
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add dataset(s)
| Industry   | Expected File                        | Download From |
|------------|--------------------------------------|---------------|
| Telecom    | `data/WA_Fn-UseC_-Telco-Customer-Churn.csv` | [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) |
| Banking    | `data/bank_churn.csv`               | [Kaggle](https://www.kaggle.com/datasets/shantanudhakadd/bank-customer-churn-prediction) |
| E-commerce | `data/ecommerce_churn.csv`          | [Kaggle](https://www.kaggle.com/datasets/ankitverma2010/ecommerce-customer-churn-analysis-and-prediction) |

### 3. Train the model(s)
```bash
python train_model.py --industry telecom
python train_model.py --industry banking
python train_model.py --industry ecommerce
```

### 4. Launch the app
```bash
streamlit run app.py
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏭 Multi-Industry | Switch between Telecom, Banking, E-commerce |
| 🔮 Single Prediction | Fill in customer details, get instant risk score |
| 📂 Bulk CSV Upload | Upload hundreds of customers, download results |
| 📊 Gauge Chart | Visual churn probability indicator |
| 💡 Retention Tips | Smart suggestions based on risk level |
| 📈 Feature Importance | See which factors drive churn |

---

## 📁 Portfolio

This project is part of the `ai-ml-portfolio` GitHub repository alongside:
- `customer-churn-prediction` — Core ML skills, EDA, model comparison
- `customer-churn-realworld` — Real-world thinking, multi-industry, bulk prediction ← **This project**
