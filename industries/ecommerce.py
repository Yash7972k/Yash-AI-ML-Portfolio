class EcommerceIndustry:
    name = "🛒 E-commerce"
    dataset = "data/ecommerce_churn.csv"
    target_column = "Churn"

    fields = {
        "Tenure": {"label": "Customer Tenure (months)", "type": "number", "min": 0, "max": 60, "default": 10},
        "CityTier": {"label": "City Tier", "type": "select", "options": ["1", "2", "3"], "default": "1"},
        "WarehouseToHome": {"label": "Warehouse to Home Distance (km)", "type": "number", "min": 1, "max": 100, "default": 15},
        "HourSpendOnApp": {"label": "Hours Spent on App/Day", "type": "number", "min": 0, "max": 10, "default": 3},
        "NumberOfDeviceRegistered": {"label": "Devices Registered", "type": "number", "min": 1, "max": 6, "default": 3},
        "SatisfactionScore": {"label": "Satisfaction Score (1-5)", "type": "number", "min": 1, "max": 5, "default": 3},
        "NumberOfAddress": {"label": "Number of Addresses", "type": "number", "min": 1, "max": 20, "default": 3},
        "Complain": {"label": "Filed Complaint", "type": "select", "options": ["Yes", "No"], "default": "No"},
        "OrderAmountHikeFromLastYear": {"label": "Order Amount Hike (%) from Last Year", "type": "number", "min": 0, "max": 100, "default": 15},
        "CouponUsed": {"label": "Coupons Used (Last Month)", "type": "number", "min": 0, "max": 20, "default": 2},
        "OrderCount": {"label": "Orders Last Month", "type": "number", "min": 0, "max": 30, "default": 3},
        "DaySinceLastOrder": {"label": "Days Since Last Order", "type": "number", "min": 0, "max": 365, "default": 10},
        "CashbackAmount": {"label": "Cashback Amount ($)", "type": "number", "min": 0.0, "max": 500.0, "default": 150.0},
        "PreferredLoginDevice": {"label": "Preferred Login Device", "type": "select", "options": ["Mobile Phone", "Computer", "Tablet"], "default": "Mobile Phone"},
        "PreferredPaymentMode": {"label": "Preferred Payment Mode", "type": "select", "options": ["Debit Card", "UPI", "Credit Card", "Cash on Delivery", "E wallet"], "default": "Debit Card"},
        "Gender": {"label": "Gender", "type": "select", "options": ["Male", "Female"], "default": "Male"},
        "PreferedOrderCat": {"label": "Preferred Order Category", "type": "select", "options": ["Laptop & Accessory", "Mobile", "Fashion", "Grocery", "Others"], "default": "Mobile"},
        "MaritalStatus": {"label": "Marital Status", "type": "select", "options": ["Single", "Married", "Divorced"], "default": "Single"},
    }

    retention_tips = {
        "high": [
            "🎟️ Send a personalized 30% discount coupon immediately",
            "🚚 Offer free express shipping for the next 3 months",
            "💎 Upgrade to VIP/Premium membership for free",
            "🎁 Surprise gift with next purchase",
            "📞 Proactive customer support outreach call",
        ],
        "medium": [
            "📧 Send re-engagement email with trending products",
            "💰 Offer loyalty cashback on next purchase",
            "🔔 Enable personalized push notifications",
        ],
        "low": [
            "✅ Customer is active — maintain engagement campaigns",
            "📊 Analyze purchase patterns for upsell opportunities",
        ],
    }

    categorical_columns = [
        "PreferredLoginDevice", "PreferredPaymentMode", "Gender",
        "PreferedOrderCat", "MaritalStatus", "Complain", "CityTier"
    ]

    drop_columns = ["CustomerID"]
