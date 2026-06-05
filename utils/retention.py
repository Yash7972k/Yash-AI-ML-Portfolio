def get_risk_level(probability: float) -> str:
    """Classify churn probability into risk level."""
    if probability >= 0.70:
        return "high"
    elif probability >= 0.40:
        return "medium"
    else:
        return "low"


def get_retention_tips(probability: float, industry) -> list:
    """Return retention tips based on risk level and industry."""
    level = get_risk_level(probability)
    return industry.retention_tips.get(level, [])


def get_risk_color(probability: float) -> str:
    """Return Streamlit color string for risk badge."""
    level = get_risk_level(probability)
    return {"high": "red", "medium": "orange", "low": "green"}[level]


def get_risk_emoji(probability: float) -> str:
    """Return emoji indicator for risk level."""
    level = get_risk_level(probability)
    return {"high": "🔴", "medium": "🟠", "low": "🟢"}[level]
