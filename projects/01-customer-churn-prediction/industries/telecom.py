class TelecomIndustry:
    name = "📱 Telecom"
    dataset = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    target_column = "Churn"

    fields = {
        "tenure": {"label": "Tenure (months)", "type": "number", "min": 0, "max": 72, "default": 12},
        "MonthlyCharges": {"label": "Monthly Charges ($)", "type": "number", "min": 0.0, "max": 200.0, "default": 65.0},
        "TotalCharges": {"label": "Total Charges ($)", "type": "number", "min": 0.0, "max": 10000.0, "default": 1000.0},
        "Contract": {"label": "Contract Type", "type": "select", "options": ["Month-to-month", "One year", "Two year"], "default": "Month-to-month"},
        "InternetService": {"label": "Internet Service", "type": "select", "options": ["DSL", "Fiber optic", "No"], "default": "Fiber optic"},
        "PaymentMethod": {"label": "Payment Method", "type": "select", "options": ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"], "default": "Electronic check"},
        "TechSupport": {"label": "Tech Support", "type": "select", "options": ["Yes", "No", "No internet service"], "default": "No"},
        "OnlineSecurity": {"label": "Online Security", "type": "select", "options": ["Yes", "No", "No internet service"], "default": "No"},
        "PaperlessBilling": {"label": "Paperless Billing", "type": "select", "options": ["Yes", "No"], "default": "Yes"},
        "SeniorCitizen": {"label": "Senior Citizen", "type": "select", "options": ["Yes", "No"], "default": "No"},
    }

    retention_tips = {
        "high": [
            "🎁 Offer a 2-year contract with 20% discount to lock in loyalty",
            "📞 Assign a dedicated customer success manager",
            "🚀 Upgrade internet speed for free for 3 months",
            "💳 Switch to automatic payment with a $5/month discount",
            "🔒 Provide free online security + tech support bundle",
        ],
        "medium": [
            "📬 Send a personalized loyalty reward email",
            "💡 Suggest a better-value plan based on usage",
            "🎉 Offer a referral bonus program",
        ],
        "low": [
            "✅ Customer is satisfied — maintain regular check-ins",
            "📊 Monitor usage trends quarterly",
        ],
    }

    categorical_columns = [
        "gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService",
        "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
        "Contract", "PaperlessBilling", "PaymentMethod"
    ]

    drop_columns = ["customerID"]
