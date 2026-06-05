class BankingIndustry:
    name = "🏦 Bank / Finance"
    dataset = "data/bank_churn.csv"
    target_column = "Exited"

    fields = {
        "CreditScore": {"label": "Credit Score", "type": "number", "min": 300, "max": 900, "default": 650},
        "Age": {"label": "Age", "type": "number", "min": 18, "max": 92, "default": 38},
        "Tenure": {"label": "Tenure (years)", "type": "number", "min": 0, "max": 10, "default": 4},
        "Balance": {"label": "Account Balance ($)", "type": "number", "min": 0.0, "max": 250000.0, "default": 75000.0},
        "NumOfProducts": {"label": "Number of Products", "type": "number", "min": 1, "max": 4, "default": 2},
        "HasCrCard": {"label": "Has Credit Card", "type": "select", "options": ["Yes", "No"], "default": "Yes"},
        "IsActiveMember": {"label": "Active Member", "type": "select", "options": ["Yes", "No"], "default": "Yes"},
        "EstimatedSalary": {"label": "Estimated Salary ($)", "type": "number", "min": 0.0, "max": 200000.0, "default": 60000.0},
        "Geography": {"label": "Geography", "type": "select", "options": ["France", "Germany", "Spain"], "default": "France"},
        "Gender": {"label": "Gender", "type": "select", "options": ["Male", "Female"], "default": "Male"},
    }

    retention_tips = {
        "high": [
            "👨‍💼 Assign a dedicated relationship manager immediately",
            "💰 Offer a premium savings account with higher interest rate",
            "🏠 Provide pre-approved loan offers with lower rates",
            "🎖️ Upgrade to Gold/Platinum membership tier",
            "📱 Offer exclusive mobile banking premium features",
        ],
        "medium": [
            "📧 Send personalized financial planning newsletter",
            "💳 Offer a credit limit increase",
            "🎁 Provide cashback rewards on debit/credit usage",
        ],
        "low": [
            "✅ Customer is engaged — send quarterly portfolio summary",
            "📊 Review product cross-sell opportunities",
        ],
    }

    categorical_columns = ["Geography", "Gender", "HasCrCard", "IsActiveMember"]

    drop_columns = ["RowNumber", "CustomerId", "Surname"]
