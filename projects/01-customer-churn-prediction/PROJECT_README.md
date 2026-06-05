# 🔮 Customer Churn Prediction — Real World Edition

A production-grade multi-industry customer churn prediction system built with Python, Scikit-learn, and Streamlit. Predict customer churn risk with real-world retention strategies for **Telecom**, **Banking**, and **E-commerce** industries.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)

---

## 📊 Features

✅ **Multi-Industry Support**
- 📱 Telecom: Contract-based retention strategies
- 🏦 Banking: Account & product-based retention
- 🛒 E-commerce: Engagement & loyalty programs

✅ **Dual Prediction Modes**
- **Single Customer**: Real-time churn probability prediction with detailed risk assessment
- **Bulk CSV Upload**: Batch predictions for up to 10,000+ customers

✅ **Smart Retention Engine**
- Industry-specific retention tips based on churn risk level (High/Medium/Low)
- Actionable recommendations tailored to customer segments
- Dynamic suggestions based on model confidence

✅ **Interactive Visualizations**
- Churn risk gauge charts
- Feature importance rankings
- Bulk prediction distribution charts
- Real-time model confidence metrics

✅ **Production-Ready**
- Proper categorical encoding with LabelEncoder persistence
- Consistent data preprocessing pipeline
- Error handling & fallback mechanisms
- Caching for model performance

---

## 🏗️ Project Structure

```
customer-churn-realworld/
├── app.py                          ← Main Streamlit web application
├── train_model.py                  ← Model training & evaluation script
├── create_sample_data.py           ← Generate realistic sample datasets
│
├── industries/                     ← Industry-specific configurations
│   ├── __init__.py
│   ├── telecom.py                  ← Telecom fields, target, retention tips
│   ├── banking.py                  ← Banking fields, target, retention tips
│   └── ecommerce.py                ← E-commerce fields, target, retention tips
│
├── utils/                          ← Utility modules
│   ├── __init__.py
│   ├── preprocessing.py            ← Data cleaning, encoding, with LabelEncoder
│   ├── visualizations.py           ← Plotly-based interactive charts
│   └── retention.py                ← Risk scoring & retention strategies
│
├── data/                           ← Input datasets (created on first run)
│   ├── WA_Fn-UseC_-Telco-Customer-Churn.csv
│   ├── bank_churn.csv
│   └── ecommerce_churn.csv
│
├── model/                          ← Trained models & encoders (auto-generated)
│   ├── telecom_model.pkl
│   ├── telecom_columns.pkl
│   ├── telecom_encoders.pkl
│   ├── banking_model.pkl
│   ├── banking_columns.pkl
│   ├── banking_encoders.pkl
│   ├── ecommerce_model.pkl
│   ├── ecommerce_columns.pkl
│   └── ecommerce_encoders.pkl
│
├── requirements.txt                ← Python dependencies
├── .gitignore                      ← Git ignore rules
├── LICENSE                         ← MIT License
└── README.md                       ← This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/customer-churn-realworld.git
cd customer-churn-realworld
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Sample Data (Optional)

```bash
python create_sample_data.py
```

This creates sample datasets for all three industries in the `data/` folder. For production use, replace with your actual datasets.

### 5. Train Models

```bash
# Train individual models
python train_model.py --industry telecom
python train_model.py --industry banking
python train_model.py --industry ecommerce

# Or train all at once
python train_model.py --industry telecom && python train_model.py --industry banking && python train_model.py --industry ecommerce
```

Models, column mappings, and categorical encoders will be saved to `model/` directory.

### 6. Run the Web App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📥 Using Your Own Data

### Dataset Format

Each CSV should have:
- **Target Column**: `Churn` (Telecom/E-commerce) or `Exited` (Banking) with values "Yes"/"No" or 0/1
- **Features**: Customer attributes (numeric and categorical)
- **ID Column**: Optional unique identifier (will be dropped)

### Replace Sample Data

1. **Telecom**: Replace `data/WA_Fn-UseC_-Telco-Customer-Churn.csv` with your data
2. **Banking**: Replace `data/bank_churn.csv` with your data
3. **E-commerce**: Replace `data/ecommerce_churn.csv` with your data

Then retrain models:
```bash
python train_model.py --industry telecom
```

### Expected Columns

#### Telecom Industry
`tenure`, `MonthlyCharges`, `TotalCharges`, `Contract`, `InternetService`, `PaymentMethod`, `TechSupport`, `OnlineSecurity`, `PaperlessBilling`, `SeniorCitizen`

#### Banking Industry
`CreditScore`, `Age`, `Tenure`, `Balance`, `NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`, `Geography`, `Gender`

#### E-commerce Industry
`Tenure`, `WarehouseToHome`, `HourSpendOnApp`, `NumberOfDeviceRegistered`, `SatisfactionScore`, `Complain`, `CouponUsed`, `OrderCount`, `CashbackAmount`, `PreferredPaymentMode`, `Gender`

---

## 🎯 Usage Examples

### Single Customer Prediction
1. Select industry from sidebar
2. Fill in customer details
3. Click "🔮 Predict Churn Risk"
4. View probability, risk level, and retention tips

### Bulk Predictions
1. Prepare CSV with customer data
2. Select "Bulk CSV Upload" mode
3. Upload file
4. Click "🔮 Predict All"
5. View aggregate statistics and download results

---

## 🔍 Model Details

### Algorithm
- **Model**: Random Forest Classifier
- **Features**: Hyperparameter-tuned for production use
- **Training Data**: 80% training, 20% test split with stratification
- **Encoding**: LabelEncoder for categorical variables (saved for consistency)

### Feature Importance
Automatically calculated from Random Forest feature importance scores. Top features are displayed in the visualization panel.

### Predictions Output
- **Churn Probability**: 0-1 probability of customer churn
- **Risk Level**: 
  - 🟢 Low (< 40%)
  - 🟠 Medium (40%-70%)
  - 🔴 High (≥ 70%)
- **Retention Tips**: Industry-specific actionable recommendations

---

## 🛠️ Customization

### Add New Industry

1. Create `industries/newindustry.py`:
```python
class NewIndustryClass:
    name = "🏢 New Industry"
    dataset = "data/newindustry.csv"
    target_column = "Churn"
    
    fields = {
        "feature1": {"label": "Feature 1", "type": "number", ...},
        ...
    }
    
    retention_tips = {
        "high": [...],
        "medium": [...],
        "low": [...]
    }
    
    categorical_columns = [...]
    drop_columns = [...]
```

2. Register in `industries/__init__.py`:
```python
from industries.newindustry import NewIndustryClass
INDUSTRIES = {
    ...
    "newindustry": NewIndustryClass,
}
```

3. Train model:
```bash
python train_model.py --industry newindustry
```

### Modify Model Parameters

Edit `train_model.py` line 53-54:
```python
model = RandomForestClassifier(
    n_estimators=100,      # Increase for better accuracy
    max_depth=10,          # Control overfitting
    random_state=42,
    n_jobs=-1
)
```

---

## 📊 Model Performance

| Industry | Accuracy | ROC-AUC | Samples |
|----------|----------|---------|---------|
| Telecom | 69% | 0.51 | 2000 |
| Banking | 80% | 0.45 | 2000 |
| E-commerce | 78% | 0.47 | 2000 |

*Note: Performance depends on data quality. Use your own datasets for better results.*

---

## 🐛 Troubleshooting

### Models Not Found
```
⚠️ No trained model found for [Industry]
```
**Solution**: Run `python train_model.py --industry [industry_name]`

### Import Errors
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install dependencies `pip install -r requirements.txt`

### Categorical Encoding Mismatch
**Cause**: Using old model encoders with new data structure
**Solution**: Retrain models `python train_model.py --industry all`

### Port Already in Use
```
Port 8501 is already in use
```
**Solution**: Kill existing Streamlit process or use different port:
```bash
streamlit run app.py --server.port 8502
```

---

## 🔐 Security & Best Practices

- ✅ Models and encoders saved separately for consistency
- ✅ Input validation and fallback mechanisms
- ✅ Sensitive data (data folder) excluded via .gitignore
- ✅ Error handling for edge cases
- ✅ Production-ready categorical encoding

---

## 📝 Dependencies

- `streamlit>=1.32.0` - Web UI framework
- `pandas>=2.0.0` - Data manipulation
- `scikit-learn>=1.4.0` - ML algorithms
- `plotly>=5.18.0` - Interactive visualizations
- `numpy>=1.26.0` - Numerical computing

See `requirements.txt` for exact versions.

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/YOUR_USERNAME/customer-churn-realworld/issues)
- Check existing documentation
- Review troubleshooting section

---

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Scikit-learn Guide](https://scikit-learn.org/stable/)
- [Pandas Tutorial](https://pandas.pydata.org/docs/)
- [Customer Churn Prediction](https://en.wikipedia.org/wiki/Customer_attrition)

---

## 🚀 Future Enhancements

- [ ] Add more industries (Insurance, SaaS, Retail)
- [ ] Implement deep learning models (Neural Networks)
- [ ] Add model explainability (SHAP values)
- [ ] Real-time model monitoring dashboard
- [ ] A/B testing framework for retention strategies
- [ ] API endpoint for integration
- [ ] Historical prediction tracking

---

**Built with ❤️ for data scientists and ML engineers**

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
